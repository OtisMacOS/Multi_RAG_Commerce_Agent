from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage, SystemMessage
from langchain.agents import initialize_agent, AgentType, Tool
from langchain.memory import ConversationBufferMemory
from typing import List, Dict, Any, Optional
import json
from ..config import settings
from ..models.chat import ChatRequest, ChatResponse, Language
from .rag_service import rag_service
from .language_service import language_service
from .memory_service import memory_service

class AgentService:
    """智能Agent服务"""
    
    def __init__(self):
        # 初始化LLM
        self.llm = ChatOpenAI(
            openai_api_key=settings.OPENAI_API_KEY,
            openai_api_base=settings.OPENAI_BASE_URL,
            model=settings.OPENAI_MODEL,
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

请根据用户问题类型提供相应的回答：
- 如果是问候或闲聊，请友好回应，可以简单介绍自己
- 如果是业务问题（商品、物流、售后等），请使用提供的上下文信息给出准确回答
- 如果涉及商品信息，请使用knowledge_search工具获取最新信息

回答要准确、专业、友好，符合客服身份。"""

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

    def _detect_intent_with_llm(self, message: str, language: str = "zh") -> str:
        """使用LLM检测用户意图"""
        try:
            intent_prompt = f"""请分析以下用户消息的意图，只返回 "chat" 或 "business"：

用户消息：{message}

意图说明：
- "chat": 闲聊、问候、感谢、告别等一般性对话
- "business": 询问商品信息、价格、购买、物流、售后、使用方法等业务相关问题

请只返回一个单词："""

            # 使用LLM进行意图识别
            response = self.llm([HumanMessage(content=intent_prompt)])
            intent = response.content.strip().lower()
            
            # 验证返回结果
            if intent in ["chat", "business"]:
                return intent
            else:
                # 如果LLM返回的不是预期值，使用关键词匹配作为备选
                print(f"LLM意图识别返回异常值: {intent}，使用关键词匹配")
                return self._detect_intent_with_keywords(message)
                
        except Exception as e:
            print(f"LLM意图识别失败: {e}，使用关键词匹配")
            return self._detect_intent_with_keywords(message)

    def _detect_intent_with_keywords(self, message: str) -> str:
        """使用关键词匹配检测用户意图（备选方案）"""
        # 闲聊/问候意图的关键词
        chat_keywords = [
            "你好", "您好", "hi", "hello", "早上好", "下午好", "晚上好",
            "怎么称呼", "你叫什么", "你是谁", "介绍一下", "介绍自己",
            "谢谢", "感谢", "再见", "拜拜", "goodbye", "bye",
            "天气", "今天", "心情", "怎么样", "如何"
        ]
        
        # 业务相关意图的关键词
        business_keywords = [
            "商品", "产品", "购买", "价格", "多少钱", "怎么买", "如何购买",
            "物流", "快递", "配送", "发货", "收货", "运输", "运费",
            "退货", "换货", "退款", "售后", "客服", "服务",
            "使用方法", "怎么用", "操作", "安装", "设置",
            "质量", "材质", "规格", "尺寸", "颜色", "型号"
        ]
        
        message_lower = message.lower()
        
        # 检查是否包含业务关键词
        for keyword in business_keywords:
            if keyword in message_lower:
                return "business"
        
        # 检查是否包含闲聊关键词
        for keyword in chat_keywords:
            if keyword in message_lower:
                return "chat"
        
        # 默认返回业务意图（保守策略）
        return "business"

    def _detect_intent(self, message: str) -> str:
        """检测用户意图（主方法）"""
        # 优先使用LLM进行意图识别，失败时自动降级到关键词匹配
        return self._detect_intent_with_llm(message)

    def process_chat(self, chat_request: ChatRequest, detected_language: str = None) -> ChatResponse:
        """处理聊天请求"""
        try:
            # 使用传入的语言检测结果，如果没有则进行检测
            if detected_language is None:
                detected_language = language_service.detect_language(chat_request.message)
            user_language = chat_request.language or detected_language
            
            # 检测用户意图
            intent = self._detect_intent(chat_request.message)
            print(f"用户意图检测: '{chat_request.message}' -> {intent}")
            
            # 根据意图决定是否进行RAG检索
            context = ""
            if intent == "business":
                # 业务问题：进行RAG检索
                print("检测到业务意图，进行RAG检索...")
                context = rag_service.get_relevant_context(
                    chat_request.message, 
                    top_k=settings.TOP_K_RETRIEVAL
                )
            else:
                # 闲聊问题：不进行RAG检索
                print("检测到闲聊意图，跳过RAG检索...")
                context = "这是用户的一般性问候或闲聊，请友好回应。"
            
            # 构建提示词
            prompt = self.chat_prompt.format(
                context=context,
                history=memory_service.get_context_for_session(chat_request.session_id, max_messages=5),
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
            
            # 更新记忆（通过memory_service）
            memory_service.add_message(
                session_id=chat_request.session_id,
                user_id=chat_request.user_id,
                role="assistant",
                content=answer,
                language=user_language
            )
            
            # 构建响应
            chat_response = ChatResponse(
                response=answer,
                language=Language(user_language),
                confidence=0.9,  # 可以根据实际需要调整
                session_id=chat_request.session_id or "default",
                sources=self._extract_sources(context) if intent == "business" else []
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