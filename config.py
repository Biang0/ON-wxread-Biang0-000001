# config.py 自定义配置,包括阅读次数、推送token的填写
import os
import re
import json
import random

# ===== 可配置区域 =====
READ_NUM = int(os.getenv('READ_NUM', 120))  # 默认120次（60分钟）
PUSH_METHOD = os.getenv('PUSH_METHOD', '')  # 推送方式，可选 pushplus/wxpusher/telegram
PUSHPLUS_TOKEN = os.getenv("PUSHPLUS_TOKEN", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
WXPUSHER_SPT = os.getenv("WXPUSHER_SPT", "")

# ===== 书籍信息 =====
b_values = [
    "ce032b305a9bc1ce0b0dd2a",  # 三体1  
    "3a8321c0813ab7839g011bd5",  # 三体2
    "f623242072a191daf6294db",  # 三体3
]

book_mapping = {
    "ce032b305a9bc1ce0b0dd2a": "三体1：地球往事",
    "3a8321c0813ab7839g011bd5": "三体2：黑暗森林",
    "f623242072a191daf6294db": "三体3：死神永生",
}

random_b_value = random.choice(b_values)  # 随机选择一本书

# ===== 请求数据 =====
data = {
    "appId": "wb182564874663h152492176",
    "b": random_b_value,
    "c": "7cb321502467cbbc409e62d",
    "ci": 70,
    "co": 0,
    "sm": "示例章节",
    "pr": 74,
    "rt": 30,
    "ts": 1727660516749,
    "rn": 31,
    "sg": "991118cc229871a5442993ecb08b5d2844d7f001dbad9a9bc7b2ecf73dc8db7e",
    "ct": 1727660516,
    "ps": "b1d32a307a4c3259g016b67",
    "pc": "080327b07a4c3259g018787",
}

# ===== Headers 和 Cookies 解析 =====
def convert(curl_command):
    """提取bash接口中的headers与cookies
    支持 -H 'Cookie: xxx' 和 -b 'xxx' 两种方式的cookie提取
    """
    # 提取 headers
    headers_temp = {}
    for match in re.findall(r"-H '([^:]+): ([^']+)'", curl_command):
        headers_temp[match[0]] = match[1]

    # 提取 cookies
    cookies = {}
    
    # 从 -H 'Cookie: xxx' 提取
    cookie_header = next((v for k, v in headers_temp.items() 
                         if k.lower() == 'cookie'), '')
    
    # 从 -b 'xxx' 提取
    cookie_b = re.search(r"-b '([^']+)'", curl_command)
    cookie_string = cookie_b.group(1) if cookie_b else cookie_header
    
    # 解析 cookie 字符串
    if cookie_string:
        for cookie in cookie_string.split('; '):  
            if '=' in cookie:
                key, value = cookie.split('=', 1)
                cookies[key.strip()] = value.strip()
    
    # 移除 headers 中的 Cookie/cookie
    headers = {k: v for k, v in headers_temp.items() 
              if k.lower() != 'cookie'}

    return headers, cookies


headers, cookies = convert(curl_str) if curl_str else (headers, cookies)

# ===== GitHub Actions 输出 =====
print(f"📚 书籍映射表: {json.dumps(book_mapping, ensure_ascii=False, indent=2)}")
print(f"📖 可用书籍 b 值: {b_values}")
print(f"🎯 选定书籍: {book_mapping.get(random_b_value, '未知书籍')} (b值: {random_b_value})")
