from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class Language(str, Enum):
    """支持的语言枚举"""
    CHINESE = "zh"
    ENGLISH = "en"

class Message(BaseModel):
    """消息模型"""
    role: str = Field(..., description="消息角色: user/assistant")
    content: str = Field(..., description="消息内容")
    timestamp: datetime = Field(default_factory=datetime.now, description="消息时间戳")
    language: Optional[Language] = Field(None, description="消息语言")

class ChatRequest(BaseModel):
    """聊天请求模型"""
    message: str = Field(..., description="用户输入的消息")
    user_id: Optional[str] = Field(None, description="用户ID")
    session_id: Optional[str] = Field(None, description="会话ID")
    language: Optional[Language] = Field(None, description="用户语言偏好")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="上下文信息")

class ChatResponse(BaseModel):
    """聊天响应模型"""
    response: str = Field(..., description="AI回复内容")
    language: Language = Field(..., description="回复语言")
    confidence: float = Field(..., description="回答置信度", ge=0.0, le=1.0)
    sources: Optional[List[str]] = Field(default_factory=list, description="信息来源")
    session_id: str = Field(..., description="会话ID")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间戳")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="元数据")

class ConversationHistory(BaseModel):
    """对话历史模型"""
    session_id: str = Field(..., description="会话ID")
    user_id: Optional[str] = Field(None, description="用户ID")
    messages: List[Message] = Field(default_factory=list, description="消息列表")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间") 