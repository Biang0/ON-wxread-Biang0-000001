import os
import re
import json
import random

"""
可修改区域
默认使用本地值如果不存在从环境变量中获取值
"""

# 阅读次数 默认120次/60分钟
READ_NUM = int(os.getenv('READ_NUM') or 120)
# 需要推送时可选，可选pushplus、wxpusher、telegram
PUSH_METHOD = os.getenv('PUSH_METHOD', '')
# pushplus推送时需填
PUSHPLUS_TOKEN = os.getenv("PUSHPLUS_TOKEN", "")
# telegram推送时需填
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
# wxpusher推送时需填
WXPUSHER_SPT = os.getenv("WXPUSHER_SPT", "")
# read接口的bash命令，本地部署时可对应替换headers、cookies
curl_str = os.getenv('WXREAD_CURL_BASH')

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
cookies = {
    'RK': 'oxEY1bTnXf',
    'ptcz': '53e3b35a9486dd63c4d06430b05aa169402117fc407dc5cc9329b41e59f62e2b',
    'pac_uid': '0_e63870bcecc18',
    'iip': '0',
    '_qimei_uuid42': '183070d3135100ee797b08bc922054dc3062834291',
    'wr_avatar': 'https%3A%2F%2Fthirdwx.qlogo.cn%2Fmmopen%2Fvi_32%2FeEOpSbFh2Mb1bUxMW9Y3FRPfXwWvOLaNlsjWIkcKeeNg6vlVS5kOVuhNKGQ1M8zaggLqMPmpE5qIUdqEXlQgYg%2F132',
    'wr_gender': '0',
}

headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6,ko;q=0.5',
    'baggage': 'sentry-environment=production,sentry-release=dev-1730698697208,sentry-public_key=ed67ed71f7804a038e898ba54bd66e44,sentry-trace_id=1ff5a0725f8841088b42f97109c45862',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0',
}

# 提取 headers 和 cookies
def convert(curl_command):
    """提取bash接口中的headers与cookies
    支持 -H 'Cookie: xxx' 和 -b 'xxx' 两种方式的cookie提取
    """
    headers_temp = {}
    for match in re.findall(r"-H '([^:]+): ([^']+)'", curl_command):
        headers_temp[match[0]] = match[1]

    cookies = {}
    
    # 从 -H 'Cookie: xxx' 提取
    cookie_header = next((v for k, v in headers_temp.items() if k.lower() == 'cookie'), '')
    
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
    headers = {k: v for k, v in headers_temp.items() if k.lower() != 'cookie'}

    return headers, cookies

headers, cookies = convert(curl_str) if curl_str else (headers, cookies)

# ===== GitHub Actions 输出 =====
print(f"📚 书籍映射表: {json.dumps(book_mapping, ensure_ascii=False, indent=2)}")
print(f"📖 可用书籍 b 值: {b_values}")
print(f"🎯 选定书籍: {book_mapping.get(random_b_value, '未知书籍')} (b值: {random_b_value})")

# GitHub Actions 变量设置
github_env = os.getenv('GITHUB_ENV', '')
if github_env:
    with open(github_env, 'a') as env_file:
        env_file.write(f"SELECTED_BOOK={book_mapping.get(random_b_value, '未知书籍')}\n")
        env_file.write(f"SELECTED_B_VALUE={random_b_value}\n")