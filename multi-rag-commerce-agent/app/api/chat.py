from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from ..models.chat import ChatRequest, ChatResponse, ConversationHistory
from ..models.knowledge import SearchRequest, SearchResponse
from ..services.agent_service import agent_service
from ..services.memory_service import memory_service
from ..services.language_service import language_service
from ..services.rag_service import rag_service
from ..utils.helpers import generate_session_id, create_error_response, create_success_response
from ..config import settings

router = APIRouter(prefix="/api/v1", tags=["chat"])

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """主要聊天接口"""
    try:
        # 生成会话ID（如果没有提供）
        if not request.session_id:
            request.session_id = generate_session_id()
        
        # 语言检测
        detected_language = language_service.detect_language(request.message)
        user_language = request.language or detected_language
        
        # 添加用户消息到记忆
        memory_service.add_message(
            session_id=request.session_id,
            user_id=request.user_id,
            role="user",
            content=request.message,
            language=user_language
        )
        
        # 处理聊天请求
        chat_response = agent_service.process_chat(request)
        
        # 添加助手回复到记忆
        memory_service.add_message(
            session_id=request.session_id,
            user_id=request.user_id,
            role="assistant",
            content=chat_response.response,
            language=chat_response.language.value
        )
        
        return chat_response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"聊天处理失败: {str(e)}")

@router.get("/history/{session_id}")
async def get_conversation_history(session_id: str, limit: Optional[int] = 10):
    """获取对话历史"""
    try:
        messages = memory_service.get_conversation_history(session_id, limit=limit)
        return create_success_response({
            "session_id": session_id,
            "messages": [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat(),
                    "language": msg.language.value if msg.language else None
                }
                for msg in messages
            ],
            "total": len(messages)
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取历史记录失败: {str(e)}")

@router.get("/history/{session_id}/summary")
async def get_conversation_summary(session_id: str):
    """获取对话摘要"""
    try:
        summary = memory_service.get_conversation_summary(session_id)
        return create_success_response(summary)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取对话摘要失败: {str(e)}")

@router.delete("/history/{session_id}")
async def clear_conversation_history(session_id: str):
    """清空对话历史"""
    try:
        success = memory_service.clear_conversation(session_id)
        if success:
            return create_success_response({"message": "对话历史已清空"})
        else:
            raise HTTPException(status_code=400, detail="清空对话历史失败")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"清空对话历史失败: {str(e)}")

@router.post("/search")
async def search_knowledge(search_request: SearchRequest):
    """搜索知识库"""
    try:
        search_response = rag_service.search(search_request)
        return create_success_response(search_response.dict())
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")

@router.post("/detect-language")
async def detect_language(text: str):
    """语言检测"""
    try:
        language_info = language_service.get_language_info(text)
        return create_success_response(language_info)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"语言检测失败: {str(e)}")

@router.get("/memory/stats")
async def get_memory_stats():
    """获取记忆统计信息"""
    try:
        stats = memory_service.get_memory_stats()
        return create_success_response(stats)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")

@router.get("/memory/sessions")
async def get_active_sessions():
    """获取活跃会话列表"""
    try:
        sessions = memory_service.get_active_sessions()
        return create_success_response({
            "active_sessions": sessions,
            "count": len(sessions)
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取会话列表失败: {str(e)}")

@router.get("/agent/info")
async def get_agent_info():
    """获取Agent信息"""
    try:
        info = agent_service.get_agent_info()
        return create_success_response(info)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取Agent信息失败: {str(e)}")

@router.get("/knowledge/info")
async def get_knowledge_info():
    """获取知识库信息"""
    try:
        info = rag_service.get_collection_info()
        return create_success_response(info)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取知识库信息失败: {str(e)}")

@router.post("/memory/preferences/{user_id}")
async def update_user_preferences(user_id: str, preferences: Dict[str, Any]):
    """更新用户偏好"""
    try:
        success = memory_service.update_user_preferences(user_id, preferences)
        if success:
            return create_success_response({"message": "用户偏好已更新"})
        else:
            raise HTTPException(status_code=400, detail="更新用户偏好失败")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新用户偏好失败: {str(e)}")

@router.get("/memory/preferences/{user_id}")
async def get_user_preferences(user_id: str):
    """获取用户偏好"""
    try:
        preferences = memory_service.get_user_preferences(user_id)
        return create_success_response(preferences)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用户偏好失败: {str(e)}")

@router.get("/export/{session_id}")
async def export_conversation(session_id: str):
    """导出对话历史"""
    try:
        export_data = memory_service.export_conversation(session_id)
        if export_data:
            return create_success_response({
                "session_id": session_id,
                "export_data": export_data
            })
        else:
            raise HTTPException(status_code=404, detail="会话不存在")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出对话失败: {str(e)}") 