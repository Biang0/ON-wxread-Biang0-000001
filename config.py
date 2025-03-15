# config.py 安全配置中心
import os
import re
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
    """安全配置加载与验证器"""
    
    @staticmethod
    def load_books() -> List[str]:
        """验证并加载书籍ID列表"""
        raw_ids = os.getenv('B_VALUES', '')
        logger.debug(f"原始B_VALUES值: {raw_ids[:20]}...")  # 调试日志
        
        if not raw_ids:
            logger.critical("❌ 未检测到B_VALUES环境变量")
            raise ValueError("B_VALUES 环境变量未配置")

        valid_ids = []
        error_ids = []
        
        for bid in raw_ids.split(','):
            clean_bid = bid.strip()
            if SecurityConfig._is_valid_book_id(clean_bid):
                valid_ids.append(clean_bid)
            else:
                error_ids.append(clean_bid)
                
        if error_ids:
            logger.warning(f"发现{len(error_ids)}个无效书籍ID，样例: {error_ids[:3]}")
            
        if not valid_ids:
            logger.critical("❌ 无有效书籍ID")
            raise ValueError("书籍ID格式验证失败")
            
        logger.info(f"✅ 成功加载{len(valid_ids)}个有效书籍ID")
        return valid_ids

    @staticmethod
    def _is_valid_book_id(book_id: str) -> bool:
        """验证单个书籍ID格式"""
        return len(book_id) == 32 and book_id.isalnum()

class CurlParser:
    """CURL命令解析器"""
    
    @staticmethod
    def parse(curl_command: str) -> Tuple[Dict, Dict]:
        """安全解析CURL命令"""
        logger.debug("开始解析CURL命令...")
        
        if not curl_command.startswith('curl'):
            logger.error("❌ CURL命令必须以'curl'开头")
            return {}, {}

        try:
            headers = CurlParser._extract_headers(curl_command)
            cookies = CurlParser._extract_cookies(curl_command)
            return headers, cookies
        except Exception as e:
            logger.error(f"❌ CURL解析异常: {str(e)}")
            return {}, {}

    @staticmethod
    def _extract_headers(curl: str) -> Dict[str, str]:
        """提取请求头信息"""
        headers = {}
        pattern = re.compile(r"-H&#92;s+'([^']+?):&#92;s*([^']*)'")
        
        for match in pattern.findall(curl):
            key = match[0].strip()
            value = match[1].strip()
            if key.lower() == 'cookie':
                continue  # 跳过Cookie头
            headers[key] = value
            logger.debug(f"识别到请求头: {key}=****")
            
        return headers

    @staticmethod
    def _extract_cookies(curl: str) -> Dict[str, str]:
        """提取并合并Cookie信息"""
        cookies = {}
        
        # 从-b参数提取
        if b_match := re.search(r"-b&#92;s+'([^']+)'", curl):
            for pair in b_match.group(1).split(';'):
                CurlParser._add_cookie_pair(pair, cookies)
                
        # 从Cookie头提取
        if c_match := re.search(r"-H&#92;s+'Cookie:&#92;s*([^']*)'", curl):
            for pair in c_match.group(1).split(';'):
                CurlParser._add_cookie_pair(pair, cookies)
                
        logger.debug(f"解析到{len(cookies)}个Cookie")
        return cookies

    @staticmethod
    def _add_cookie_pair(pair: str, cookie_dict: Dict):
        """安全添加单个Cookie"""
        pair = pair.strip()
        if '=' in pair:
            k, v = pair.split('=', 1)
            cookie_dict[k.strip()] = v.strip()
        elif pair:
            logger.warning(f"⚠️ 忽略无效Cookie段: {pair}")

# ======================
# 配置初始化
# ======================
try:
    # 书籍ID配置
    book_ids = SecurityConfig.load_books()
    
    # CURL配置解析
    curl_command = os.getenv('WXREAD_CURL_BASH', '')
    headers, cookies = CurlParser.parse(curl_command)
    
    if not headers or not cookies:
        logger.critical("❌ CURL配置解析失败，请检查格式")
        raise ValueError("无效的CURL配置")
        
    logger.info("✅ 配置初始化完成")

except Exception as e:
    logger.critical("‼️ 配置加载失败，程序终止")
    raise

# 导出配置
B_VALUES: List[str] = book_ids
headers: Dict[str, str] = headers
cookies: Dict[str, str] = cookies
