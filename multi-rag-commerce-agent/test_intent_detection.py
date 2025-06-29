#!/usr/bin/env python3
"""
意图识别测试脚本
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.services.agent_service import agent_service

def test_intent_detection():
    """测试意图识别功能"""
    
    # 测试用例
    test_cases = [
        # 闲聊/问候类
        ("你好", "chat"),
        ("您好，请问怎么称呼？", "chat"),
        ("hi, how are you?", "chat"),
        ("谢谢你的帮助", "chat"),
        ("再见", "chat"),
        ("今天天气真不错", "chat"),
        
        # 业务相关类
        ("这个商品多少钱？", "business"),
        ("怎么购买？", "business"),
        ("物流要多久？", "business"),
        ("可以退货吗？", "business"),
        ("商品质量怎么样？", "business"),
        ("怎么使用这个产品？", "business"),
        ("这个产品有什么特点？", "business"),
        
        # 边界情况
        ("今天天气怎么样？", "chat"),
        ("这个产品今天有优惠吗？", "business"),
        ("我想了解一下你们的产品", "business"),
        ("你叫什么名字？", "chat"),
    ]
    
    print("=== LLM意图识别测试 ===\n")
    
    for i, (message, expected_intent) in enumerate(test_cases, 1):
        print(f"测试 {i}: '{message}'")
        print(f"期望意图: {expected_intent}")
        
        try:
            detected_intent = agent_service._detect_intent(message)
            status = "✅" if detected_intent == expected_intent else "❌"
            print(f"检测意图: {detected_intent} {status}")
        except Exception as e:
            print(f"❌ 测试失败: {e}")
        
        print("-" * 50)

def test_keyword_fallback():
    """测试关键词匹配备选方案"""
    print("\n=== 关键词匹配备选方案测试 ===\n")
    
    test_cases = [
        ("你好", "chat"),
        ("商品价格", "business"),
        ("物流配送", "business"),
        ("谢谢", "chat"),
    ]
    
    for message, expected_intent in test_cases:
        detected_intent = agent_service._detect_intent_with_keywords(message)
        status = "✅" if detected_intent == expected_intent else "❌"
        
        print(f"{status} 消息: '{message}'")
        print(f"   期望意图: {expected_intent}")
        print(f"   检测意图: {detected_intent}")
        print()

if __name__ == "__main__":
    test_intent_detection()
    test_keyword_fallback() 