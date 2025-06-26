from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage, SystemMessage
from langchain.agents import initialize_agent, AgentType, Tool
from langchain.memory import ConversationBufferMemory
from typing import List, Dict, Any, Optional
import json
from ..config import settings
from ..models.chat import ChatRequest, ChatResponse, Language
from .rag_service import rag_service

class AgentService:
    """智能Agent服务"""
    
    def __init__(self):
        # 初始化LLM
        self.llm = ChatOpenAI(
            openai_api_key=settings.OPENAI_API_KEY,
            model_name=settings.OPENAI_MODEL,
            temperature=settings.TEMPERATURE,
            max_tokens=settings.MAX_TOKENS
        )
        
        # 初始化记忆
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # 定义工具
        self.tools = self._create_tools()
        
        # 初始化Agent
        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True
        )
        
        # 提示词模板
        self.system_prompt = self._create_system_prompt()
        self.chat_prompt = self._create_chat_prompt()
    
    def _create_tools(self) -> List[Tool]:
        """创建Agent工具"""
        tools = [
            Tool(
                name="knowledge_search",
                func=self._search_knowledge,
                description="搜索商品知识库，获取商品信息、物流政策、使用方法等"
            ),
            Tool(
                name="language_detection",
                func=self._detect_language,
                description="检测用户输入的语言（中文/英文）"
            )
        ]
        return tools
    
    def _create_system_prompt(self) -> str:
        """创建系统提示词"""
        return """你是一个专业的跨境电商客服Agent，具备以下能力：

1. 多语言支持：能够理解并回应中英文问题
2. 商品知识：熟悉商品信息、物流政策、使用方法等
3. 上下文记忆：能够记住对话历史，提供连贯的回答
4. 专业友好：回答准确、专业、友好

请根据用户问题提供准确、有用的回答。如果涉及商品信息，请使用knowledge_search工具获取最新信息。"""

    def _create_chat_prompt(self) -> str:
        """创建聊天提示词模板"""
        return """基于以下信息回答用户问题：

相关上下文：
{context}

对话历史：
{history}

用户问题：{question}

请用{language}回答，回答要准确、专业、友好。"""

    def _search_knowledge(self, query: str) -> str:
        """搜索知识库工具"""
        try:
            context = rag_service.get_relevant_context(query, top_k=3)
            return context if context else "未找到相关信息"
        except Exception as e:
            return f"搜索失败: {str(e)}"

    def _detect_language(self, text: str) -> str:
        """语言检测工具"""
        # 简单的语言检测逻辑
        chinese_chars = sum(1 for char in text if '\u4e00' <= char <= '\u9fff')
        total_chars = len(text)
        
        if chinese_chars / total_chars > 0.3:
            return "zh"
        else:
            return "en"

    def process_chat(self, chat_request: ChatRequest) -> ChatResponse:
        """处理聊天请求"""
        try:
            # 语言检测
            detected_language = self._detect_language(chat_request.message)
            user_language = chat_request.language or detected_language
            
            # 获取相关上下文
            context = rag_service.get_relevant_context(
                chat_request.message, 
                top_k=settings.TOP_K_RETRIEVAL
            )
            
            # 构建提示词
            prompt = self.chat_prompt.format(
                context=context,
                history=self._get_conversation_history(chat_request.session_id),
                question=chat_request.message,
                language="中文" if user_language == "zh" else "English"
            )
            
            # 生成回答
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=prompt)
            ]
            
            response = self.llm(messages)
            answer = response.content
            
            # 更新记忆
            self._update_memory(chat_request.session_id, chat_request.message, answer)
            
            # 构建响应
            chat_response = ChatResponse(
                response=answer,
                language=Language(user_language),
                confidence=0.9,  # 可以根据实际需要调整
                session_id=chat_request.session_id or "default",
                sources=self._extract_sources(context)
            )
            
            return chat_response
            
        except Exception as e:
            print(f"处理聊天请求失败: {e}")
            return ChatResponse(
                response="抱歉，我现在无法回答您的问题，请稍后再试。",
                language=Language("zh"),
                confidence=0.0,
                session_id=chat_request.session_id or "default"
            )

    def _get_conversation_history(self, session_id: str) -> str:
        """获取对话历史"""
        # 这里可以集成更复杂的记忆管理
        # 目前使用简单的内存存储
        return ""

    def _update_memory(self, session_id: str, user_message: str, assistant_message: str):
        """更新对话记忆"""
        # 这里可以集成更复杂的记忆管理
        # 目前使用简单的内存存储
        pass

    def _extract_sources(self, context: str) -> List[str]:
        """提取信息来源"""
        sources = []
        if context:
            # 简单的来源提取逻辑
            lines = context.split('\n')
            for line in lines:
                if line.startswith('来源:'):
                    source = line.replace('来源:', '').strip()
                    if source:
                        sources.append(source)
        return sources

    def get_agent_info(self) -> Dict[str, Any]:
        """获取Agent信息"""
        return {
            "model": settings.OPENAI_MODEL,
            "temperature": settings.TEMPERATURE,
            "max_tokens": settings.MAX_TOKENS,
            "tools": [tool.name for tool in self.tools]
        }

# 创建全局Agent服务实例
agent_service = AgentService() 