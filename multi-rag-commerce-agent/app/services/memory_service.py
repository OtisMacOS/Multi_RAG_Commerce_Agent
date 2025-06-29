from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
from ..models.chat import Message, ConversationHistory
from ..config import settings

class MemoryService:
    """记忆管理服务"""
    
    def __init__(self):
        # 内存存储（生产环境建议使用Redis或数据库）
        # [mark] 为何使用Redis？ 还有其他选项吗？supabase是否是其中之一？
        self.conversations: Dict[str, ConversationHistory] = {}
        self.user_preferences: Dict[str, Dict[str, Any]] = {}
        
        # 清理过期对话的时间间隔（小时）
        self.cleanup_interval = 24
    
    def add_message(self, session_id: str, user_id: Optional[str], 
                   role: str, content: str, language: Optional[str] = None) -> bool:
        """添加消息到对话历史"""
        try:
            # 获取或创建对话历史
            if session_id not in self.conversations:
                self.conversations[session_id] = ConversationHistory(
                    session_id=session_id,
                    user_id=user_id,
                    messages=[]
                )
            
            # 创建消息
            message = Message(
                role=role,
                content=content,
                language=language
            )
            
            # 添加到对话历史
            self.conversations[session_id].messages.append(message)
            self.conversations[session_id].updated_at = datetime.now()
            
            # 限制对话历史长度
            self._limit_conversation_length(session_id)
            
            return True
            
        except Exception as e:
            print(f"添加消息失败: {e}")
            return False
    
    def get_conversation_history(self, session_id: str, 
                                limit: Optional[int] = None) -> List[Message]:
        """获取对话历史"""
        if session_id not in self.conversations:
            return []
        
        messages = self.conversations[session_id].messages
        
        if limit:
            messages = messages[-limit:]
        
        return messages
    
    def get_conversation_statistics(self, session_id: str) -> Dict[str, Any]:
        """获取对话统计信息"""
        if session_id not in self.conversations:
            return {}
        
        conv = self.conversations[session_id]
        messages = conv.messages
        
        # 统计信息
        user_messages = [msg for msg in messages if msg.role == "user"]
        assistant_messages = [msg for msg in messages if msg.role == "assistant"]
        
        # 语言统计
        languages = {}
        for msg in messages:
            if msg.language:
                lang = msg.language.value if hasattr(msg.language, 'value') else str(msg.language)
                languages[lang] = languages.get(lang, 0) + 1
        
        return {
            "session_id": session_id,
            "user_id": conv.user_id,
            "total_messages": len(messages),
            "user_messages": len(user_messages),
            "assistant_messages": len(assistant_messages),
            "languages": languages,
            "created_at": conv.created_at.isoformat(),
            "updated_at": conv.updated_at.isoformat(),
            "last_message": messages[-1].content if messages else None
        }
    
    def get_conversation_summary(self, session_id: str) -> Dict[str, Any]:
        """获取对话内容总结（使用LLM生成）"""
        if session_id not in self.conversations:
            return {}
        
        messages = self.get_conversation_history(session_id)
        if not messages:
            return {"summary": "无对话内容"}
        
        try:
            # 生成简单总结（临时实现，后续可集成LLM）
            summary = self._generate_simple_summary(messages)
            
            return {
                "session_id": session_id,
                "summary": summary,
                "conversation_length": len(messages),
                "main_topics": self._extract_main_topics(messages)
            }
            
        except Exception as e:
            print(f"生成对话总结失败: {e}")
            return {"summary": "总结生成失败", "error": str(e)}

    def get_conversation_insights(self, session_id: str) -> Dict[str, Any]:
        """获取对话洞察（包含统计、总结和上下文）"""
        return {
            "statistics": self.get_conversation_statistics(session_id),
            "summary": self.get_conversation_summary(session_id),
            "context": self.get_context_for_session(session_id, max_messages=10)
        }

    def _generate_simple_summary(self, messages: List[Message]) -> str:
        """生成简单总结（临时实现）"""
        if not messages:
            return "无对话内容"
        
        user_messages = [msg.content for msg in messages if msg.role == "user"]
        if not user_messages:
            return "用户未发送消息"
        
        # 简单的关键词提取
        keywords = []
        for msg in user_messages:
            if any(word in msg for word in ["价格", "多少钱", "费用"]):
                keywords.append("价格咨询")
            if any(word in msg for word in ["物流", "快递", "配送", "发货"]):
                keywords.append("物流问题")
            if any(word in msg for word in ["退货", "换货", "退款"]):
                keywords.append("售后服务")
            if any(word in msg for word in ["商品", "产品", "功能"]):
                keywords.append("商品信息")
        
        if keywords:
            unique_keywords = list(set(keywords))
            return f"用户主要咨询：{', '.join(unique_keywords)}"
        else:
            return "一般性咨询"

    def _extract_main_topics(self, messages: List[Message]) -> List[str]:
        """提取主要话题"""
        topics = []
        for msg in messages:
            if msg.role == "user":
                content = msg.content.lower()
                if any(word in content for word in ["价格", "多少钱"]):
                    topics.append("价格咨询")
                elif any(word in content for word in ["物流", "快递"]):
                    topics.append("物流问题")
                elif any(word in content for word in ["退货", "换货"]):
                    topics.append("售后服务")
                elif any(word in content for word in ["商品", "产品"]):
                    topics.append("商品信息")
        
        return list(set(topics))  # 去重
    
    def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """获取用户偏好"""
        return self.user_preferences.get(user_id, {})
    
    def update_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> bool:
        """更新用户偏好"""
        try:
            if user_id not in self.user_preferences:
                self.user_preferences[user_id] = {}
            
            self.user_preferences[user_id].update(preferences)
            return True
            
        except Exception as e:
            print(f"更新用户偏好失败: {e}")
            return False
    
    def get_context_for_session(self, session_id: str, max_messages: int = 5) -> str:
        """获取会话上下文（用于Agent）"""
        messages = self.get_conversation_history(session_id, limit=max_messages)
        
        if not messages:
            return ""
        
        context_parts = []
        for msg in messages:
            role = "用户" if msg.role == "user" else "助手"
            context_parts.append(f"{role}: {msg.content}")
        
        return "\n".join(context_parts)
    
    def clear_conversation(self, session_id: str) -> bool:
        """清空对话历史"""
        try:
            if session_id in self.conversations:
                del self.conversations[session_id]
            return True
        except Exception as e:
            print(f"清空对话失败: {e}")
            return False
    
    def cleanup_expired_conversations(self) -> int:
        """清理过期的对话"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=self.cleanup_interval)
            expired_sessions = []
            
            for session_id, conv in self.conversations.items():
                if conv.updated_at < cutoff_time:
                    expired_sessions.append(session_id)
            
            # 删除过期对话
            for session_id in expired_sessions:
                del self.conversations[session_id]
            
            return len(expired_sessions)
            
        except Exception as e:
            print(f"清理过期对话失败: {e}")
            return 0
    
    def get_active_sessions(self) -> List[str]:
        """获取活跃会话列表"""
        return list(self.conversations.keys())
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """获取记忆统计信息"""
        total_conversations = len(self.conversations)
        total_users = len(set(conv.user_id for conv in self.conversations.values() if conv.user_id))
        total_messages = sum(len(conv.messages) for conv in self.conversations.values())
        
        return {
            "total_conversations": total_conversations,
            "total_users": total_users,
            "total_messages": total_messages,
            "active_sessions": len(self.get_active_sessions()),
            "user_preferences": len(self.user_preferences)
        }
    
    def _limit_conversation_length(self, session_id: str):
        """限制对话历史长度"""
        if session_id in self.conversations:
            messages = self.conversations[session_id].messages
            max_length = settings.MAX_HISTORY_LENGTH
            
            if len(messages) > max_length:
                # 保留最新的消息
                self.conversations[session_id].messages = messages[-max_length:]
    
    def export_conversation(self, session_id: str) -> Optional[str]:
        """导出对话历史"""
        if session_id not in self.conversations:
            return None
        
        try:
            conv = self.conversations[session_id]
            export_data = {
                "session_id": conv.session_id,
                "user_id": conv.user_id,
                "created_at": conv.created_at.isoformat(),
                "updated_at": conv.updated_at.isoformat(),
                "messages": [
                    {
                        "role": msg.role,
                        "content": msg.content,
                        "timestamp": msg.timestamp.isoformat(),
                        "language": msg.language.value if msg.language else None
                    }
                    for msg in conv.messages
                ]
            }
            
            return json.dumps(export_data, ensure_ascii=False, indent=2)
            
        except Exception as e:
            print(f"导出对话失败: {e}")
            return None

# 创建全局记忆服务实例
memory_service = MemoryService() 