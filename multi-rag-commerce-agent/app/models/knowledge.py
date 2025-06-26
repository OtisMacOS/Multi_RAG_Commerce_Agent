from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class KnowledgeItem(BaseModel):
    """知识库项目模型"""
    id: str = Field(..., description="知识库项目ID")
    content: str = Field(..., description="知识内容")
    title: Optional[str] = Field(None, description="标题")
    category: str = Field(..., description="分类: faq/product/shipping/policy")
    language: str = Field(..., description="语言: zh/en")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="元数据")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")

class SearchResult(BaseModel):
    """搜索结果模型"""
    content: str = Field(..., description="检索到的内容")
    score: float = Field(..., description="相似度分数", ge=0.0, le=1.0)
    source: str = Field(..., description="来源")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="元数据")

class SearchRequest(BaseModel):
    """搜索请求模型"""
    query: str = Field(..., description="搜索查询")
    top_k: int = Field(default=5, description="返回结果数量")
    category: Optional[str] = Field(None, description="搜索分类")
    language: Optional[str] = Field(None, description="搜索语言")

class SearchResponse(BaseModel):
    """搜索响应模型"""
    results: List[SearchResult] = Field(default_factory=list, description="搜索结果")
    total_count: int = Field(..., description="总结果数")
    query: str = Field(..., description="原始查询")
    processing_time: float = Field(..., description="处理时间(秒)") 