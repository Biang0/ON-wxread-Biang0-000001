import os
import re

# Modifiable area
# Use local values by default. If not available, get values from environment variables.
# Default reading times: 120 times per 60 minutes
# 尝试从环境变量 READ_NUM 中获取阅读次数，如果环境变量未设置，则使用默认值 120
READ_NUM = int(os.getenv('READ_NUM') or 120)
# Optional when push is needed. Options: pushplus, wxpusher, telegram
# 尝试从环境变量 PUSH_METHOD 中获取推送方法，如果未设置则为空字符串
PUSH_METHOD = os.getenv('PUSH_METHOD') or ""
# Required when using pushplus for pushing
# 尝试从环境变量 PUSHPLUS_TOKEN 中获取 pushplus 推送所需的令牌，如果未设置则为空字符串
PUSHPLUS_TOKEN = os.getenv("PUSHPLUS_TOKEN") or ""
# Required when using telegram for pushing
# 尝试从环境变量 TELEGRAM_BOT_TOKEN 中获取 Telegram 机器人令牌，如果未设置则为空字符串
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or ""
# 尝试从环境变量 TELEGRAM_CHAT_ID 中获取 Telegram 聊天 ID，如果未设置则为空字符串
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID") or ""
# Required when using wxpusher for pushing
# 尝试从环境变量 WXPUSHER_SPT 中获取 wxpusher 推送所需的令牌，如果未设置则为空字符串
WXPUSHER_SPT = os.getenv("WXPUSHER_SPT") or ""
# Bash command for the read interface. Can be replaced with headers and cookies during local deployment.
# 尝试从环境变量 WXREAD_CURL_BASH 中获取 read 接口的 bash 命令，如果未设置则为 None
curl_str = os.getenv('WXREAD_CURL_BASH')

# Headers and cookies are template placeholders, can be replaced during local or Docker deployment.
# 定义请求的 cookies 字典，这些值是示例，可在本地或 Docker 部署时替换
cookies = {
    'RK': 'oxEY1bTnXf',
    'ptcz': '53e3b35a9486dd63c4d06430b05aa169402117fc407dc5cc9329b41e59f62e2b',
    'pac_uid': '0_e63870bcecc18',
    'iip': '0',
    '_qimei_uuid42': '183070d3135100ee797b08bc922054dc3062834291',
    'wr_avatar': 'https%3A%2F%2Fthirdwx.qlogo.cn%2Fmmopen%2Fvi_32%2FeEOpSbFh2Mb1bUxMW9Y3FRPfXwWvOLaNlsjWIkcKeeNg6vlVS5kOVuhNKGQ1M8zaggLqMPmpE5qIUdqEXlQgYg%2F132',
    'wr_gender': '0',
}

# 定义请求的 headers 字典，这些值是示例，可在本地或 Docker 部署时替换
headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6,ko;q=0.5',
    'baggage': 'sentry-environment=production,sentry-release=dev-1730698697208,sentry-public_key=ed67ed71f7804a038e898ba54bd66e44,sentry-trace_id=1ff5a0725f8841088b42f97109c45862',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0',
}

# Recommended to keep. Default reading is "Three-Body Problem". Test other books to see if time increases.
# 定义请求的数据字典，包含一些默认值，可根据实际情况修改
data = {
    "appId": "wb182564874663h776775553",
    "b": "f623242072a191daf6294db",
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

# Get the value of 'b' from GitHub environment variables
# 尝试从 GitHub 环境变量 B_VALUE 中获取 'b' 的值，如果存在则更新 data 字典中的 'b' 值
b_value = os.getenv('B_VALUE')
if b_value:
    data['b'] = b_value


def convert(curl_command):
    """
    Extract headers and cookies from a bash curl command.
    Supports extracting cookies from both -H 'Cookie: xxx' and -b 'xxx' formats.

    Args:
        curl_command (str): The bash curl command.

    Returns:
        tuple: A tuple containing the headers and cookies dictionaries.
    """
    # Extract headers
    # 初始化一个临时字典，用于存储从 curl 命令中提取的 headers
    headers_temp = {}
    # 使用正则表达式从 curl 命令中提取所有 -H 参数的 headers
    for match in re.findall(r"-H '([^:]+): ([^']+)'", curl_command):
        headers_temp[match[0]] = match[1]

    # Extract cookies
    # 初始化一个空字典，用于存储从 curl 命令中提取的 cookies
    cookies = {}
    # 从 headers_temp 中提取 'Cookie' 头的值，如果不存在则为空字符串
    cookie_header = next((v for k, v in headers_temp.items() if k.lower() == 'cookie')， '')
    # 使用正则表达式从 curl 命令中提取 -b 参数的 cookies 字符串
    cookie_b = re.search(r"-b '([^']+)'", curl_command)
    # 如果 -b 参数存在，则使用其值作为 cookies 字符串，否则使用 'Cookie' 头的值
    cookie_string = cookie_b.group(1) if cookie_b else cookie_header

    # Parse the cookie string
    # 如果 cookies 字符串不为空，则解析该字符串并存储到 cookies 字典中
    if cookie_string:
        for cookie in cookie_string.split('; '):
            if '=' in cookie:
                key, value = cookie.split('='， 1)
                cookies[key.strip()] = value.strip()

    # Remove the 'Cookie' header
    # 从 headers_temp 中移除 'Cookie' 头，得到最终的 headers 字典
    headers = {k: v for k, v in headers_temp.items() if k.lower() != 'cookie'}

    return headers, cookies


# 如果 curl_str 不为空，则调用 convert 函数提取 headers 和 cookies，否则使用默认的 headers 和 cookies
headers, cookies = convert(curl_str) if curl_str else (headers, cookies)
    
