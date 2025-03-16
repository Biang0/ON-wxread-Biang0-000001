# config.py 自定义配置,包括阅读次数、推送token的填写
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
# 需要推送时可选，可选 pushplus、wxpusher、telegram
PUSH_METHOD = "" or os.getenv('PUSH_METHOD')  
# pushplus 推送时需填
PUSHPLUS_TOKEN = "" or os.getenv("PUSHPLUS_TOKEN")
# telegram 推送时需填
TELEGRAM_BOT_TOKEN = "" or os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = "" or os.getenv("TELEGRAM_CHAT_ID")
# wxpusher 推送时需填
WXPUSHER_SPT = "" or os.getenv("WXPUSHER_SPT")
# read 接口的 bash 命令，本地部署时可对应替换 headers、cookies
curl_str = os.getenv('WXREAD_CURL_BASH')

# ===== 原始 headers 和 cookies（不修改） =====
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

"""
建议保留区域 | 默认读《三体》，其它书籍自行测试时间是否增加
"""

# 书籍映射表
b_values = [
    "66b3227071c0abb966b281b",  # 罪连环（全集）  
    "a57325c05c8ed3a57224187",  # 明朝那些事儿(全集)  
    "39f329907161e25e39f893e",  # 明朝那些事儿(增补版)(套装全九册)  
]

book_mapping = {        
    "66b3227071c0abb966b281b": "罪连环（全集）",  
    "a57325c05c8ed3a57224187": "明朝那些事儿(全集)",  
    "39f329907161e25e39f893e": "明朝那些事儿(增补版)(套装全九册)",  
}

# 随机选择一本书
random_b_value = random.choice(b_values)

# ===== GitHub Actions 输出 =====
print(f"📚 书籍映射表: {json.dumps(book_mapping, ensure_ascii=False, indent=2)}")  
print(f"📖 可用书籍 b 值: {b_values}")
print(f"🎯 选定书籍: {book_mapping.get(random_b_value, '未知书籍')} (b值: {random_b_value})")

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


# ===== 提取 headers 和 cookies（如果有 curl_str）=====
def convert(curl_command):
    """提取 bash 接口中的 headers 与 cookies"""
    # 提取 headers
    headers_temp = {}
    for match in re.findall(r"-H '([^:]+): ([^']+)'", curl_command):
        headers_temp[match[0]] = match[1]

    # 提取 cookies
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


# 如果 curl_str 存在，则解析，否则使用默认的 headers 和 cookies
headers, cookies = convert(curl_str) if curl_str else (headers, cookies)
