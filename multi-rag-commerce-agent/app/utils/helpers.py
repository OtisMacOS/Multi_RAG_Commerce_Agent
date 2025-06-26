import uuid
import hashlib
import json
from typing import Dict, Any, Optional
from datetime import datetime

def generate_session_id() -> str:
    """生成会话ID"""
    return str(uuid.uuid4())

def generate_user_id() -> str:
    """生成用户ID"""
    return f"user_{uuid.uuid4().hex[:8]}"

def hash_text(text: str) -> str:
    """对文本进行哈希"""
    return hashlib.md5(text.encode('utf-8')).hexdigest()

def safe_json_dumps(obj: Any) -> str:
    """安全的JSON序列化"""
    try:
        return json.dumps(obj, ensure_ascii=False, default=str)
    except Exception:
        return str(obj)

def safe_json_loads(text: str) -> Any:
    """安全的JSON反序列化"""
    try:
        return json.loads(text)
    except Exception:
        return None

def format_timestamp(timestamp: datetime) -> str:
    """格式化时间戳"""
    return timestamp.strftime("%Y-%m-%d %H:%M:%S")

def truncate_text(text: str, max_length: int = 100) -> str:
    """截断文本"""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."

def extract_keywords(text: str, max_keywords: int = 5) -> list:
    """提取关键词（简单实现）"""
    # 简单的关键词提取，实际项目中可以使用更复杂的算法
    words = text.lower().split()
    word_count = {}
    
    for word in words:
        if len(word) > 2:  # 过滤短词
            word_count[word] = word_count.get(word, 0) + 1
    
    # 按频率排序
    sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
    return [word for word, count in sorted_words[:max_keywords]]

def validate_email(email: str) -> bool:
    """验证邮箱格式"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def sanitize_input(text: str) -> str:
    """清理用户输入"""
    if not text:
        return ""
    
    # 移除危险字符
    dangerous_chars = ['<', '>', '"', "'", '&']
    for char in dangerous_chars:
        text = text.replace(char, '')
    
    return text.strip()

def calculate_similarity(text1: str, text2: str) -> float:
    """计算文本相似度（简单实现）"""
    if not text1 or not text2:
        return 0.0
    
    # 简单的Jaccard相似度
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    intersection = len(words1.intersection(words2))
    union = len(words1.union(words2))
    
    return intersection / union if union > 0 else 0.0

def get_file_extension(filename: str) -> str:
    """获取文件扩展名"""
    return filename.split('.')[-1].lower() if '.' in filename else ''

def is_valid_filename(filename: str) -> bool:
    """验证文件名"""
    import re
    # 不允许的字符
    invalid_chars = r'[<>:"/\\|?*]'
    return not re.search(invalid_chars, filename)

def format_file_size(size_bytes: int) -> str:
    """格式化文件大小"""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"

def retry_on_failure(func, max_retries: int = 3, delay: float = 1.0):
    """失败重试装饰器"""
    import time
    
    def wrapper(*args, **kwargs):
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                time.sleep(delay)
        return None
    
    return wrapper

def create_error_response(message: str, error_code: str = "UNKNOWN_ERROR") -> Dict[str, Any]:
    """创建错误响应"""
    return {
        "success": False,
        "error": {
            "code": error_code,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
    }

def create_success_response(data: Any, message: str = "Success") -> Dict[str, Any]:
    """创建成功响应"""
    return {
        "success": True,
        "message": message,
        "data": data,
        "timestamp": datetime.now().isoformat()
    } 