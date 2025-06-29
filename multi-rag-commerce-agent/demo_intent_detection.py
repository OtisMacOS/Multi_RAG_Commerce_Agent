#!/usr/bin/env python3
"""
意图识别演示脚本
展示LLM意图识别和RAG检索的完整流程
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.services.agent_service import agent_service
from app.models.chat import ChatRequest

def demo_chat_flow():
    """演示聊天流程"""
    
    # 测试消息
    test_messages = [
        "你好，请问怎么称呼？",  # 闲聊
        "这个商品多少钱？",      # 业务问题
        "谢谢你的帮助",          # 闲聊
        "物流要多久能到？",      # 业务问题
        "今天天气怎么样？",      # 闲聊
        "可以退货吗？",          # 业务问题
    ]
    
    print("=== 聊天流程演示 ===\n")
    
    for i, message in enumerate(test_messages, 1):
        print(f"用户消息 {i}: {message}")
        print("-" * 40)
        
        try:
            # 创建聊天请求
            chat_request = ChatRequest(
                message=message,
                session_id="demo_session",
                user_id="demo_user"
            )
            
            # 处理聊天请求
            response = agent_service.process_chat(chat_request)
            
            print(f"AI回复: {response.response}")
            print(f"语言: {response.language.value}")
            print(f"置信度: {response.confidence}")
            print(f"信息来源: {response.sources}")
            
        except Exception as e:
            print(f"处理失败: {e}")
        
        print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    demo_chat_flow() 