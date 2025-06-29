#!/usr/bin/env python3
"""
对话功能测试脚本
测试新的统计、总结和洞察功能
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.services.memory_service import memory_service
from app.models.chat import Message, Language

def test_conversation_features():
    """测试对话功能"""
    
    session_id = "test_session_features"
    user_id = "test_user_features"
    
    print("=== 对话功能测试 ===\n")
    
    # 1. 添加测试对话
    print("1. 添加测试对话...")
    test_messages = [
        ("user", "这个商品多少钱？", "zh"),
        ("assistant", "这个商品的价格是299元。", "zh"),
        ("user", "物流要多久能到？", "zh"),
        ("assistant", "一般3-5个工作日送达。", "zh"),
        ("user", "可以退货吗？", "zh"),
        ("assistant", "支持7天无理由退货。", "zh"),
        ("user", "How long is the delivery time?", "en"),
        ("assistant", "Delivery usually takes 3-5 business days.", "en"),
    ]
    
    for role, content, lang in test_messages:
        memory_service.add_message(
            session_id=session_id,
            user_id=user_id,
            role=role,
            content=content,
            language=lang
        )
        print(f"   {role}: {content}")
    
    print("\n2. 测试对话统计功能...")
    statistics = memory_service.get_conversation_statistics(session_id)
    print(f"   总消息数: {statistics.get('total_messages', 0)}")
    print(f"   用户消息数: {statistics.get('user_messages', 0)}")
    print(f"   助手消息数: {statistics.get('assistant_messages', 0)}")
    print(f"   语言统计: {statistics.get('languages', {})}")
    
    print("\n3. 测试对话总结功能...")
    summary = memory_service.get_conversation_summary(session_id)
    print(f"   总结内容: {summary.get('summary', 'N/A')}")
    print(f"   对话长度: {summary.get('conversation_length', 0)}")
    print(f"   主要话题: {summary.get('main_topics', [])}")
    
    print("\n4. 测试对话洞察功能...")
    insights = memory_service.get_conversation_insights(session_id)
    print(f"   统计信息: {insights.get('statistics', {})}")
    print(f"   总结信息: {insights.get('summary', {})}")
    print(f"   上下文长度: {len(insights.get('context', ''))}")
    
    print("\n5. 测试对话历史功能...")
    history = memory_service.get_conversation_history(session_id, limit=3)
    print(f"   最近3条消息:")
    for msg in history:
        print(f"     {msg.role}: {msg.content}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_conversation_features() 