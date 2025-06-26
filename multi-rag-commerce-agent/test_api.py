#!/usr/bin/env python3
"""
API测试脚本
用于测试各个接口功能
"""

import requests
import json
import time
from typing import Dict, Any

# API基础URL
BASE_URL = "http://localhost:8000"

def test_health_check():
    """测试健康检查"""
    print("测试健康检查...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"健康检查失败: {e}")
        return False

def test_app_info():
    """测试应用信息"""
    print("\n测试应用信息...")
    try:
        response = requests.get(f"{BASE_URL}/info")
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 200
    except Exception as e:
        print(f"应用信息测试失败: {e}")
        return False

def test_language_detection():
    """测试语言检测"""
    print("\n测试语言检测...")
    
    test_texts = [
        "这个商品支持发往德国吗？",
        "How long is the delivery time?",
        "智能手表有什么功能？What features does it have?"
    ]
    
    for text in test_texts:
        try:
            response = requests.post(
                f"{BASE_URL}/api/v1/detect-language",
                params={"text": text}
            )
            print(f"文本: {text}")
            print(f"检测结果: {response.json()}")
        except Exception as e:
            print(f"语言检测失败: {e}")

def test_chat():
    """测试聊天功能"""
    print("\n测试聊天功能...")
    
    test_messages = [
        {
            "message": "这个商品支持发往德国吗？",
            "user_id": "test_user_001",
            "session_id": "test_session_001"
        },
        {
            "message": "How long is the delivery time?",
            "user_id": "test_user_002", 
            "session_id": "test_session_002"
        },
        {
            "message": "智能手表有什么功能？",
            "user_id": "test_user_001",
            "session_id": "test_session_001"
        }
    ]
    
    for msg in test_messages:
        try:
            print(f"\n发送消息: {msg['message']}")
            response = requests.post(
                f"{BASE_URL}/api/v1/chat",
                json=msg,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"回复: {result['response']}")
                print(f"语言: {result['language']}")
                print(f"置信度: {result['confidence']}")
            else:
                print(f"请求失败: {response.status_code}")
                print(f"错误信息: {response.text}")
                
        except Exception as e:
            print(f"聊天测试失败: {e}")

def test_search():
    """测试搜索功能"""
    print("\n测试搜索功能...")
    
    search_queries = [
        {
            "query": "德国配送",
            "top_k": 3,
            "language": "zh"
        },
        {
            "query": "delivery time",
            "top_k": 3,
            "language": "en"
        }
    ]
    
    for query in search_queries:
        try:
            print(f"\n搜索查询: {query['query']}")
            response = requests.post(
                f"{BASE_URL}/api/v1/search",
                json=query,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"找到 {result['data']['total_count']} 条结果")
                for i, item in enumerate(result['data']['results']):
                    print(f"结果 {i+1}: {item['content'][:100]}...")
            else:
                print(f"搜索失败: {response.status_code}")
                
        except Exception as e:
            print(f"搜索测试失败: {e}")

def test_history():
    """测试历史记录功能"""
    print("\n测试历史记录功能...")
    
    session_id = "test_session_001"
    
    try:
        # 获取历史记录
        response = requests.get(f"{BASE_URL}/api/v1/history/{session_id}")
        if response.status_code == 200:
            result = response.json()
            print(f"历史记录数量: {result['data']['total']}")
            for msg in result['data']['messages']:
                print(f"{msg['role']}: {msg['content'][:50]}...")
        else:
            print(f"获取历史记录失败: {response.status_code}")
            
        # 获取对话摘要
        response = requests.get(f"{BASE_URL}/api/v1/history/{session_id}/summary")
        if response.status_code == 200:
            result = response.json()
            print(f"对话摘要: {result['data']}")
        else:
            print(f"获取对话摘要失败: {response.status_code}")
            
    except Exception as e:
        print(f"历史记录测试失败: {e}")

def test_memory_stats():
    """测试记忆统计"""
    print("\n测试记忆统计...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/memory/stats")
        if response.status_code == 200:
            result = response.json()
            print(f"记忆统计: {json.dumps(result['data'], indent=2, ensure_ascii=False)}")
        else:
            print(f"获取记忆统计失败: {response.status_code}")
            
    except Exception as e:
        print(f"记忆统计测试失败: {e}")

def test_agent_info():
    """测试Agent信息"""
    print("\n测试Agent信息...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/agent/info")
        if response.status_code == 200:
            result = response.json()
            print(f"Agent信息: {json.dumps(result['data'], indent=2, ensure_ascii=False)}")
        else:
            print(f"获取Agent信息失败: {response.status_code}")
            
    except Exception as e:
        print(f"Agent信息测试失败: {e}")

def main():
    """主测试函数"""
    print("=" * 60)
    print("多语言检索增强商品问答 Agent - API测试")
    print("=" * 60)
    
    # 等待服务启动
    print("等待服务启动...")
    time.sleep(2)
    
    # 运行测试
    tests = [
        test_health_check,
        test_app_info,
        test_language_detection,
        test_chat,
        test_search,
        test_history,
        test_memory_stats,
        test_agent_info
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"测试 {test.__name__} 异常: {e}")
    
    print(f"\n测试完成: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！")
    else:
        print("⚠️  部分测试失败，请检查服务状态")

if __name__ == "__main__":
    main() 