# main.py 主逻辑：包括字段拼接、模拟请求
import json
import time
import random
import logging
import hashlib
import requests
from push import push
from config import data, headers, cookies, READ_NUM, PUSH_METHOD, book_mapping, random_b_value

# 配置日志
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)-8s - %(message)s")

# 常量
KEY = "3c5c8717f3daf09iop3423zafeqoi"
READ_URL = "https://weread.qq.com/web/book/read"
RENEW_URL = "https://weread.qq.com/web/login/renewal"


def cal_hash(input_string):
    """计算哈希值"""
    _7032f5 = 0x15051505
    _cc1055 = _7032f5
    length = len(input_string)
    _19094e = length - 1

    while _19094e > 0:
        _7032f5 = 0x7fffffff & (_7032f5 ^ ord(input_string[_19094e]) << (length - _19094e) % 30)
        _cc1055 = 0x7fffffff & (_cc1055 ^ ord(input_string[_19094e - 1]) << _19094e % 30)
        _19094e -= 2

    return hex(_7032f5 + _cc1055)[2:].lower()


def get_wr_skey():
    """刷新 wr_skey"""
    response = requests.post(RENEW_URL, headers=headers, cookies=cookies)
    for cookie in response.headers.get('Set-Cookie', '').split(';'):
        if "wr_skey" in cookie:
            return cookie.split('=')[-1][:8]
    return None


# 输出当前阅读的书籍
logging.info(f"📖 本次阅读书籍: {book_mapping.get(random_b_value, '未知书籍')} (b值: {random_b_value})")

index = 1
while index <= READ_NUM:
    data["ct"] = int(time.time())
    data["ts"] = int(time.time() * 1000)
    data["rn"] = random.randint(0, 1000)
    data["sg"] = hashlib.sha256(f"{data['ts']}{data['rn']}{KEY}".encode()).hexdigest()
    data["s"] = cal_hash(json.dumps(data, separators=(",", ":")))

    logging.info(f"⏱️ 第 {index} 次阅读...")
    response = requests.post(READ_URL, headers=headers, cookies=cookies, data=json.dumps(data, separators=(",", ":")))
    res_data = response.json()

    if "succ" in res_data:
        index += 1
        time.sleep(30)
        logging.info(f"✅ 阅读成功，累计 {index * 0.5} 分钟")
    else:
        logging.warning("❌ Cookie 可能已过期，尝试刷新...")
        new_skey = get_wr_skey()
        if new_skey:
            cookies["wr_skey"] = new_skey
            logging.info(f"✅ 新密钥: {new_skey}")
        else:
            ERROR_MSG = "❌ 无法获取新密钥，终止运行。"
            logging.error(ERROR_MSG)
            push(ERROR_MSG, PUSH_METHOD)
            raise Exception(ERROR_MSG)

logging.info("🎉 阅读任务完成！")

if PUSH_METHOD:
    push(f"🎉 自动阅读完成！📖 {book_mapping[random_b_value]} ⏱️ {READ_NUM * 0.5} 分钟", PUSH_METHOD)