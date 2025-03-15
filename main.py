# main.py 核心逻辑
import sys
import time
import random
import hashlib
import logging
from typing import Dict, Optional
from config import headers, cookies, B_VALUES

# ======================
# 日志配置
# ======================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('WXReadCore')

# ======================
# 加密引擎
# ======================
class SecurityEngine:
    """安全参数生成器"""
    
    @staticmethod
    def generate_sg(ts: int, rn: int, key: str = "") -> str:
        """生成二级哈希签名"""
        seed = f"{ts}{rn}{key}".encode()
        return hashlib.sha256(seed).hexdigest()[:32]

    @staticmethod
    def generate_signature(Dict) -> str:
        """核心签名算法（保持与官方一致）"""
        def custom_hash(input_str: str) -> int:
            # 保持原有哈希逻辑
            hash1 = 0x15051505
            hash2 = hash1
            length = len(input_str)
            
            for i in range(length-1, -1, -1):
                char = ord(input_str[i])
                if (length - i) % 2 == 1:
                    hash1 ^= (char << ((length - i) % 30))
                else:
                    hash2 ^= (char << (i % 30))
            
            return (hash1 + hash2) & 0x7FFFFFFF

        sorted_items = sorted(data.items(), key=lambda x: x[0])
        query_str = '&'.join(f"{k}={v}" for k, v in sorted_items)
        return f"{custom_hash(query_str):x}"

# ======================
# 请求处理器
# ======================
class RequestHandler:
    """带自动恢复机制的请求处理器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(headers)
        self.session.cookies.update(cookies)
        self.retry_limit = 3
        self.cookie_refreshed = False
        
    def execute(self, payload: Dict) -> bool:
        """执行带自动恢复机制的请求"""
        for attempt in range(self.retry_limit):
            try:
                response = self._safe_post(payload)
                
                if response.json().get('succ') == 1:
                    return True
                    
                if self._handle_special_case(response, attempt):
                    continue
                    
            except requests.exceptions.RequestException as e:
                logger.warning(f"请求异常: {str(e)}")
                self._random_delay(attempt)
                
        return False

    def _safe_post(self, payload: Dict) -> requests.Response:
        """安全POST请求"""
        try:
            return self.session.post(
                "https://weread.qq.com/web/book/read",
                json=payload,
                timeout=(3.05, 15)
            )
        except Exception as e:
            logger.error(f"请求失败: {str(e)}")
            raise

    def _handle_special_case(self, response: requests.Response, attempt: int) -> bool:
        """处理特殊响应"""
        if 'expired' in response.text and not self.cookie_refreshed:
            logger.warning("检测到会话过期，尝试刷新凭证...")
            return self._refresh_credentials()
            
        logger.warning(f"异常响应 [{response.status_code}]: {response.text[:200]}")
        self._random_delay(attempt)
        return False

    def _refresh_credentials(self) -> bool:
        """刷新会话凭证"""
        try:
            resp = self.session.post(
                "https://weread.qq.com/web/login/renewal",
                json={"rq": "/web/book/read"},
                timeout=5
            )
            new_cookies = resp.cookies.get_dict()
            self.session.cookies.update(new_cookies)
            self.cookie_refreshed = True
            logger.info("凭证刷新成功")
            return True
        except Exception as e:
            logger.error(f"凭证刷新失败: {str(e)}")
            return False

    def _random_delay(self, attempt: int):
        """智能延迟策略"""
        base = random.randint(25, 35)
        time.sleep(base * (attempt + 1))

# ======================
# 核心业务逻辑
# ======================
class WXReadService:
    """微信读书自动化服务"""
    
    def __init__(self):
        self.handler = RequestHandler()
        self.total = int(os.getenv('READ_NUM', 120))
        self.executed = 0
        
    def run(self):
        """执行阅读任务"""
        logger.info(f"🚀 启动任务，计划执行 {self.total} 次阅读")
        
        for count in range(1, self.total + 1):
            book_id = self._select_book()
            payload = self._build_payload(book_id)
            
            if self._execute_single(count, payload):
                self.executed += 1
                
            self._smart_delay(count)
            
        logger.info(f"🎉 任务完成，成功执行 {self.executed}/{self.total} 次")

    def _select_book(self) -> str:
        """随机选择书籍ID"""
        return random.choice(B_VALUES)

    def _build_payload(self, book_id: str) -> Dict:
        """构造请求负载"""
        ts = int(time.time() * 1000)
        rn = random.randint(0, 1000)
        
        return {
            "b": book_id,
            "ts": ts,
            "rn": rn,
            "sg": SecurityEngine.generate_sg(ts, rn),
            "ct": int(ts / 1000),
            "s": SecurityEngine.generate_signature({
                "b": book_id,
                "ts": ts,
                "rn": rn
            })
        }

    def _execute_single(self, count: int, payload: Dict) -> bool:
        """执行单次请求"""
        logger.info(f"📖 正在执行第 {count}/{self.total} 次阅读 [{payload['b'][:4]}...]")
        success = self.handler.execute(payload)
        
        if success:
            logger.info(f"✅ 第 {count} 次阅读成功")
        else:
            logger.warning(f"⚠️ 第 {count} 次阅读失败")
            
        return success

    def _smart_delay(self, count: int):
        """动态延迟策略"""
        if count % 10 == 0:
            delay = random.randint(45, 60)
        else:
            delay = random.randint(25, 35)
            
        logger.debug(f"随机延迟 {delay} 秒")
        time.sleep(delay)

if __name__ == "__main__":
    try:
        service = WXReadService()
        service.run()
    except KeyboardInterrupt:
        logger.warning("🛑 用户主动中断任务")
        sys.exit(130)
    except Exception as e:
        logger.critical(f"‼️ 系统异常: {str(e)}")
        sys.exit(1)
    finally:
        logger.info("🛂 清理会话资源...")
