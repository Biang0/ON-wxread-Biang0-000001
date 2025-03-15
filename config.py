# config.py 安全配置中心
import os
import re
import random
import logging
from typing import Dict, Tuple, List

# ======================
# 日志初始化
# ======================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('WXReadConfig')

# ======================
# 安全配置加载器
# ======================
class SecurityConfig:
    @staticmethod
    def load_books() -> List[str]:
        """验证并加载书籍ID列表"""
        raw_ids = os.getenv('B_VALUES', '')
        if not raw_ids:
            raise ValueError("B_VALUES 环境变量未配置")
            
        valid_ids = []
        for bid in raw_ids.split(','):
            clean_bid = bid.strip()
            if len(clean_bid) == 32 and clean_bid.isalnum():
                valid_ids.append(clean_bid)
            else:
                logger.warning(f"忽略无效书籍ID: {bid}")
        
        if not valid_ids:
            raise ValueError("无有效书籍ID，请检查B_VALUES格式")
        return valid_ids

    @staticmethod
    def parse_curl(curl: str) -> Tuple[Dict, Dict]:
        """安全解析CURL命令"""
        def extract(pattern, text):
            return re.findall(pattern, text, re.DOTALL)

        # 清理命令格式
        curl = re.sub(r'&#92;s+', ' ', curl.replace('&#92;&#92;', '')).strip()
        
        # 提取headers
        headers = {}
        for h in extract(r"-H&#92;s+'([^']+?)'", curl):
            if ':' in h:
                k, v = h.split(':', 1)
                headers[k.strip()] = v.strip()

        # 合并cookies来源
        cookies = {}
        cookie_sources = [
            headers.pop('Cookie', ''),
            next(iter(extract(r"-b&#92;s+'([^']+?)'", curl)), '')
        ]
        
        for source in cookie_sources:
            for pair in filter(None, source.split(';')):
                if '=' in pair:
                    k, v = pair.split('=', 1)
                    cookies[k.strip()] = v.strip()

        return headers, cookies

# ======================
# 动态配置初始化
# ======================
# 必需参数
B_VALUES = SecurityConfig.load_books()

# 请求配置
curl_command = os.getenv('WXREAD_CURL_BASH', '')
headers, cookies = SecurityConfig.parse_curl(curl_command) if curl_command else ({}, {})

# 推送配置
PUSH_CONFIG = {
    'method': os.getenv('PUSH_METHOD', '').lower(),
    'pushplus': os.getenv('PUSHPLUS_TOKEN'),
    'telegram': (os.getenv('TG_BOT_TOKEN'), os.getenv('TG_CHAT_ID')),
    'wxpusher': os.getenv('WXPUSHER_TOKEN')
}

# 请求模板（动态字段由主程序填充）
REQUEST_TEMPLATE = {
    "appId": os.getenv('APP_ID', 'wb_default_app_id'),
    "b": None,
    "c": os.getenv('C_VALUE', 'default_c_value'),
    "ci": int(os.getenv('CI_VALUE', 137)),
    "co": int(os.getenv('CO_VALUE', 7098)),
    "sm": "经典段落示例...",
    "pr": 55,
    "rt": 30,
    "ts": None,
    "rn": None,
    "sg": None,
    "ct": None,
    "ps": os.getenv('PS_VALUE', 'default_ps'),
    "pc": os.getenv('PC_VALUE', 'default_pc'),
}
