# config.py 微信读书自动化配置
import os
import re
import random
from typing import Dict, Tuple

# ======================
# 环境变量配置区
# ======================

# 基础阅读配置
READ_NUM = int(os.getenv('READ_NUM', 120))  # 默认120次/60分钟

# 推送服务配置
PUSH_METHOD = os.getenv('PUSH_METHOD', '')
PUSHPLUS_TOKEN = os.getenv("PUSHPLUS_TOKEN", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
WXPUSHER_SPT = os.getenv("WXPUSHER_SPT", "")

# 必须配置的书籍ID列表
B_VALUES = [b.strip() for b in os.getenv('B_VALUES', '').split(',') if b.strip()]
if not B_VALUES:
    raise ValueError("环境变量 B_VALUES 必须配置，格式示例：export B_VALUES='id1,id2,id3'")

# 请求配置
curl_str = os.getenv('WXREAD_CURL_BASH', '')

# ======================
# 请求头处理函数
# ======================

def parse_curl(curl_command: str) -> Tuple[Dict[str, str], Dict[str, str]]:
    """解析curl命令生成headers和cookies
    
    Args:
        curl_command: 包含认证信息的curl命令字符串
        
    Returns:
        Tuple[headers_dict, cookies_dict]
    """
    headers = {}
    for match in re.findall(r"-H '([^:]+): ([^']+)'", curl_command):
        headers[match[0]] = match[1]

    # 合并Cookie来源：-H 'Cookie:' 和 -b 参数
    cookie_sources = [
        headers.pop('Cookie', '') if 'Cookie' in headers else '',
        re.search(r"-b '([^']*)'", curl_command).group(1) if re.search(r"-b ", curl_command) else ''
    ]
    
    # 解析Cookies
    cookies = {}
    for source in cookie_sources:
        for cookie in filter(None, source.split(';')):
            if '=' in cookie:
                key, val = cookie.split('=', 1)
                cookies[key.strip()] = val.strip()

    return headers, cookies

# ======================
# 初始化配置
# ======================

# 默认headers/cookies（会被curl命令覆盖）
default_headers = {
    'accept': 'application/json, text/plain, */*',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0',
}

default_cookies = {
    'RK': 'oxEY1bTnXf',
    'ptcz': '53e3b35a9486dd63c4d06430b05aa169402117fc407dc5cc9329b41e59f62e2b',
}

# 优先使用curl命令配置
if curl_str:
    headers, cookies = parse_curl(curl_str)
else:
    headers = default_headers.copy()
    cookies = default_cookies.copy()

# ======================
# 动态请求体
# ======================

data = {
    "appId": "wb182564874663h776775553",
    "b": random.choice(B_VALUES),  # 动态选择书籍ID
    "c": "17c32d00329e17c276c8288",
    "ci": 137,
    "co": 7098,
    "sm": "其实领导也挺不好当的。”我笑了笑，说",
    "pr": 55,
    "rt": 30,
    "ts": 1739673850629,
    "rn": 412,
    "sg": "41b43c2f8b6b065530e28001b91c6f2ba36e70eb397ca016e891645bf18b27d8",
    "ct": 1739673850,
    "ps": "ca5326207a5e8814g01704b",
    "pc": "f2332e707a5e8814g0181e0",
}
