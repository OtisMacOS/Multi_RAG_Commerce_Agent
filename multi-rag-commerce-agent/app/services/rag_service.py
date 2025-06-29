import chromadb
from chromadb.config import Settings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
from typing import List, Dict, Any, Optional
import json
import os
import time
from ..config import settings
from ..models.knowledge import KnowledgeItem, SearchResult, SearchRequest, SearchResponse

class RAGService:
    """RAG检索增强服务"""
    
    def __init__(self):
        # 根据配置选择embedding模型
        if settings.USE_OLLAMA_EMBEDDING:
            self.embeddings = OllamaEmbeddings(
                model=settings.OLLAMA_EMBEDDING_MODEL,
                base_url=settings.OLLAMA_BASE_URL
            )
        else:
            self.embeddings = OpenAIEmbeddings(
                openai_api_key=settings.OPENAI_API_KEY,
                openai_api_base=settings.OPENAI_BASE_URL,
                model=settings.OPENAI_EMBEDDING_MODEL
            )
        
        # 初始化ChromaDB
        self.chroma_client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIRECTORY
        )
        
        # 创建或获取集合
        self.collection = self.chroma_client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION_NAME
        )
        
        # 文本分割器
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,  # 可以外置
            chunk_overlap=200,  # 可以外置
            separators=["\n\n", "\n", "。", "！", "？", ".", "!", "?"]
        )
    
    def add_knowledge(self, knowledge_items: List[KnowledgeItem]) -> bool:
        """添加知识库内容"""
        try:
            documents = []
            metadatas = []
            ids = []
            
            for item in knowledge_items:
                # 文本分割  
                chunks = self.text_splitter.split_text(item.content)
                
                for i, chunk in enumerate(chunks):
                    doc_id = f"{item.id}_chunk_{i}"
                    documents.append(chunk)
                    metadatas.append({
                        "source_id": item.id,
                        "title": item.title or "",
                        "category": item.category,
                        "language": item.language,
                        "chunk_index": i
                    })
                    ids.append(doc_id)
            
            # 批量添加到向量数据库
            if documents:
                self.collection.add(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )
            
            return True
            
        except Exception as e:
            print(f"添加知识库失败: {e}")
            return False
    
    def search(self, search_request: SearchRequest) -> SearchResponse:
        """搜索相关内容"""
        try:
            start_time = time.time()
            
            # 构建查询
            query = search_request.query
            
            # 构建过滤条件
            where_filter = {}
            if search_request.category:
                where_filter["category"] = search_request.category
            if search_request.language:
                where_filter["language"] = search_request.language
            
            # 执行搜索
            results = self.collection.query(
                query_texts=[query],
                n_results=search_request.top_k,
                where=where_filter if where_filter else None
            )
            
            # 处理搜索结果
            search_results = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    search_result = SearchResult(
                        content=doc,
                        score=results['distances'][0][i] if results['distances'] else 0.0,
                        source=results['metadatas'][0][i]['source_id'] if results['metadatas'] else "",
                        metadata=results['metadatas'][0][i] if results['metadatas'] else {}
                    )
                    search_results.append(search_result)
            
            processing_time = time.time() - start_time
            
            return SearchResponse(
                results=search_results,
                total_count=len(search_results),
                query=query,
                processing_time=processing_time
            )
            
        except Exception as e:
            print(f"搜索失败: {e}")
            return SearchResponse(
                results=[],
                total_count=0,
                query=search_request.query,
                processing_time=0.0
            )
    
    def get_relevant_context(self, query: str, top_k: int = 5) -> str:
        """获取相关上下文（用于Agent）"""
        search_request = SearchRequest(query=query, top_k=top_k)
        search_response = self.search(search_request)
        
        if search_response.results:
            context_parts = []
            for result in search_response.results:
                context_parts.append(f"内容: {result.content}\n来源: {result.source}")
            
            return "\n\n".join(context_parts)
        
        return ""
    
    def clear_knowledge(self) -> bool:
        """清空知识库"""
        try:
            self.chroma_client.delete_collection(settings.CHROMA_COLLECTION_NAME)
            self.collection = self.chroma_client.create_collection(
                name=settings.CHROMA_COLLECTION_NAME
            )
            return True
        except Exception as e:
            print(f"清空知识库失败: {e}")
            return False
    
    def get_collection_info(self) -> Dict[str, Any]:
        """获取集合信息"""
        try:
            count = self.collection.count()
            return {
                "collection_name": settings.CHROMA_COLLECTION_NAME,
                "document_count": count,
                "embedding_model": settings.OPENAI_EMBEDDING_MODEL
            }
        except Exception as e:
            return {"error": str(e)}

# 创建全局RAG服务实例
rag_service = RAGService() 