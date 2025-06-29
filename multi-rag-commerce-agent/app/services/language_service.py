from typing import Dict, Any, Optional, List, Tuple
import re
from langchain_openai import ChatOpenAI
from ..config import settings
from ..models.chat import Language

class LanguageService:
    """语言处理服务"""
    
    def __init__(self):
        # 中文特征字符
        self.chinese_pattern = re.compile(r'[\u4e00-\u9fff]')
        
        # 语言检测规则
        self.language_rules = {
            'zh': {
                'patterns': [
                    r'[\u4e00-\u9fff]',  # 中文字符
                    r'[，。！？；：""''（）【】]',  # 中文标点
                ],
                'keywords': ['的', '是', '在', '有', '和', '与', '或', '但', '而', '因为', '所以']
            },
            'en': {
                'patterns': [
                    r'[a-zA-Z]',  # 英文字母
                    r'[,.!?;:""''()\[\]]',  # 英文标点
                ],
                'keywords': ['the', 'is', 'are', 'in', 'on', 'at', 'and', 'or', 'but', 'because', 'so']
            }
        }
        
        self.llm = ChatOpenAI(
            openai_api_key=settings.OPENAI_API_KEY,
            openai_api_base=settings.OPENAI_BASE_URL,
            model=settings.OPENAI_MODEL,
            temperature=0.1
        )
    
    def detect_language(self, text: str) -> str:
        """检测文本语言"""
        if not text or not text.strip():
            return 'zh'  # 默认中文
        
        text = text.strip()
        
        # 计算各语言特征分数
        scores = {}
        
        for lang, rules in self.language_rules.items():
            score = 0
            
            # 模式匹配分数
            for pattern in rules['patterns']:
                matches = len(re.findall(pattern, text))
                score += matches
            
            # 关键词匹配分数
            for keyword in rules['keywords']:
                if keyword.lower() in text.lower():
                    score += 2
            
            scores[lang] = score
        
        # 返回得分最高的语言
        if scores['zh'] > scores['en']:
            return 'zh'
        elif scores['en'] > scores['zh']:
            return 'en'
        else:
            # 平局时，检查中文字符数量
            chinese_chars = len(self.chinese_pattern.findall(text))
            return 'zh' if chinese_chars > 0 else 'en'
    
    def is_mixed_language(self, text: str) -> bool:
        """检测是否为混合语言"""
        chinese_chars = len(self.chinese_pattern.findall(text))
        english_chars = len(re.findall(r'[a-zA-Z]', text))
        
        # 如果中英文字符都有且比例接近，认为是混合语言
        if chinese_chars > 0 and english_chars > 0:
            total_chars = chinese_chars + english_chars
            chinese_ratio = chinese_chars / total_chars
            english_ratio = english_chars / total_chars
            
            # 如果两种语言的比例都在20%-80%之间，认为是混合语言
            return 0.2 <= chinese_ratio <= 0.8 and 0.2 <= english_ratio <= 0.8
        
        return False
    
    def get_language_info(self, text: str) -> Dict[str, Any]:
        """获取语言信息"""
        detected_lang = self.detect_language(text)
        is_mixed = self.is_mixed_language(text)
        
        # 统计字符信息
        chinese_chars = len(self.chinese_pattern.findall(text))
        english_chars = len(re.findall(r'[a-zA-Z]', text))
        total_chars = len(text)
        
        return {
            'detected_language': detected_lang,
            'is_mixed_language': is_mixed,
            'chinese_chars': chinese_chars,
            'english_chars': english_chars,
            'total_chars': total_chars,
            'chinese_ratio': chinese_chars / total_chars if total_chars > 0 else 0,
            'english_ratio': english_chars / total_chars if total_chars > 0 else 0
        }
    
    def adapt_response_language(self, response: str, target_language: str) -> str:
        """适配响应语言"""
        if not response:
            return response
        
        current_language = self.detect_language(response)
        
        # 如果当前语言与目标语言一致，直接返回
        if current_language == target_language:
            return response
        
        # 这里可以集成翻译服务
        # 目前返回原响应，并添加语言提示
        if target_language == 'zh':
            return f"[英文回答] {response}\n\n[中文翻译] 抱歉，当前回答为英文，建议使用中文提问。"
        else:
            return f"[中文回答] {response}\n\n[English translation] Sorry, the current answer is in Chinese. Please ask in English."
    
    def get_language_prompt(self, language: str) -> str:
        """获取语言特定的提示词"""
        prompts = {
            'zh': "请用中文回答，回答要准确、专业、友好。",
            'en': "Please answer in English, be accurate, professional and friendly."
        }
        return prompts.get(language, prompts['zh'])
    
    def validate_language(self, language: str) -> bool:
        """验证语言代码是否有效"""
        valid_languages = ['zh', 'en']
        return language in valid_languages

# 创建全局语言服务实例
language_service = LanguageService() 