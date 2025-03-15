# main.py 核心逻辑
import time
import random
import hashlib
import logging
import requests
from typing import Dict
from config import headers, cookies, B_VALUES, REQUEST_TEMPLATE, PUSH_CONFIG

# ======================
# 日志配置
# ======================
logger = logging.getLogger('WXReadCore')
logger.setLevel(logging.INFO)

# ======================
# 加密配置
# ======================
class SecurityEngine:
    @staticmethod
    def generate_signature(Dict) -> str:
        """生成请求签名"""
        def custom_hash(input_str: str) -> str:
            hash1 = 0x15051505
            hash2 = hash1
            length = len(input_str)
            
            for i in range(length-1, -1, -1):
                char_code = ord(input_str[i])
                if (length - i) % 2 == 1:
                    hash1 = (hash1 ^ (char_code << ((length - i) % 30))) & 0x7FFFFFFF
                else:
                    hash2 = (hash2 ^ (char_code << (i % 30))) & 0x7FFFFFFF
            return f"{hash1 + hash2:x}"

        sorted_data = sorted(data.items())
        encoded_str = '&'.join(f"{k}={v}" for k, v in sorted_data)
        return custom_hash(encoded_str)

    @staticmethod
    def generate_secure_params() -> Dict:
        """生成动态安全参数"""
        ts = int(time.time() * 1000)
        return {
            "ts": ts,
            "rn": random.randint(0, 1000),
            "ct": int(ts / 1000),
            "sg": hashlib.sha256(f"{ts}{random.random()}".encode()).hexdigest()[:32]
        }

# ======================
# 请求处理器
# ======================
class RequestHandler:
    RETRY_LIMIT = 3
    BASE_DELAY = 30  # 基础间隔时间（秒）

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(headers)
        self.session.cookies.update(cookies)

    def execute_request(self, Dict) -> bool:
        """执行带重试机制的请求"""
        attempt = 0
        while attempt < self.RETRY_LIMIT:
            try:
                response = self.session.post(
                    "https://weread.qq.com/web/book/read",
                    json=data,
                    timeout=15
                )
                if response.json().get('succ', 0) == 1:
                    return True
                
                if 'expired' in response.text:
                    self.refresh_credentials()
                    
            except Exception as e:
                logger.error(f"请求异常: {str(e)}")
            
            attempt += 1
            self.random_delay(multiplier=attempt)
        
        return False

    def refresh_credentials(self):
        """刷新会话凭证"""
        try:
            response = self.session.post(
                "https://weread.qq.com/web/login/renewal",
                json={"rq": "/web/book/read"}
            )
            new_cookies = response.cookies.get_dict()
            self.session.cookies.update(new_cookies)
            logger.info("会话凭证已刷新")
        except Exception as e:
            logger.error(f"凭证刷新失败: {str(e)}")

    @staticmethod
    def random_delay(multiplier: int = 1):
        """智能延迟控制"""
        base = random.randint(25, 35)
        time.sleep(base * multiplier)

# ======================
# 推送服务
# ======================
class NotificationService:
    @staticmethod
    def send(message: str):
        method = PUSH_CONFIG['method']
        try:
            if method == 'pushplus':
                return NotificationService._pushplus(message)
            elif method == 'telegram':
                return NotificationService._telegram(message)
            elif method == 'wxpusher':
                return NotificationService._wxpusher(message)
        except Exception as e:
            logger.error(f"推送失败: {str(e)}")

    @staticmethod
    def _pushplus(message: str):
        params = {
            "token": PUSH_CONFIG['pushplus'],
            "title": "微信读书状态通知",
            "content": message
        }
        requests.post("https://www.pushplus.plus/send", json=params)

    @staticmethod
    def _telegram(message: str):
        bot_token, chat_id = PUSH_CONFIG['telegram']
        params = {
            "chat_id": chat_id,
            "text": message,
            "disable_notification": False
        }
        requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", json=params)

    @staticmethod
    def _wxpusher(message: str):
        requests.post(
            "https://wxpusher.zjiecode.com/api/send/message",
            json={
                "appToken": PUSH_CONFIG['wxpusher'],
                "content": message,
                "contentType": 1
            }
        )

# ======================
# 主流程
# ======================
def main():
    logger.info("🚀 启动微信读书自动化程序")
    total = int(os.getenv('READ_NUM', 120))
    handler = RequestHandler()
    
    for count in range(1, total+1):
        try:
            # 生成动态请求数据
            request_data = REQUEST_TEMPLATE.copy()
            request_data.update(SecurityEngine.generate_secure_params())
            request_data["b"] = random.choice(B_VALUES)
            request_data["s"] = SecurityEngine.generate_signature(request_data)
            
            # 执行请求
            logger.info(f"📖 正在执行第 {count}/{total} 次阅读...")
            if handler.execute_request(request_data):
                logger.info(f"✅ 成功完成第 {count} 次阅读")
            else:
                logger.warning(f"⚠️ 第 {count} 次阅读失败")
            
            # 智能间隔
            handler.random_delay()
            
        except KeyboardInterrupt:
            logger.warning("用户主动中断")
            break
        except Exception as e:
            logger.error(f"严重错误: {str(e)}")
            NotificationService.send(f"❌ 程序异常终止: {str(e)}")
            break

    logger.info("🎉 任务执行完毕")
    if PUSH_CONFIG['method']:
        NotificationService.send(f"✅ 阅读任务完成，共执行 {count} 次有效阅读")

if __name__ == "__main__":
    main()
