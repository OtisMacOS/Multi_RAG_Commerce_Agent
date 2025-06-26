#!/usr/bin/env python3
"""
数据初始化脚本
用于加载示例数据到向量数据库
"""

import json
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.models.knowledge import KnowledgeItem
from app.services.rag_service import rag_service
from app.config import settings

def load_json_data(file_path: str) -> list:
    """加载JSON数据文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"加载文件 {file_path} 失败: {e}")
        return []

def convert_to_knowledge_items(data: list) -> list:
    """将JSON数据转换为KnowledgeItem对象"""
    knowledge_items = []
    
    for item in data:
        try:
            knowledge_item = KnowledgeItem(
                id=item['id'],
                content=item['content'],
                title=item.get('title', ''),
                category=item['category'],
                language=item['language'],
                metadata=item.get('metadata', {})
            )
            knowledge_items.append(knowledge_item)
        except Exception as e:
            print(f"转换数据项失败: {e}")
            continue
    
    return knowledge_items

def init_knowledge_base():
    """初始化知识库"""
    print("开始初始化知识库...")
    
    # 数据文件路径
    data_dir = project_root / "data"
    faq_file = data_dir / "faq.json"
    products_file = data_dir / "products.json"
    
    # 检查文件是否存在
    if not faq_file.exists():
        print(f"FAQ文件不存在: {faq_file}")
        return False
    
    if not products_file.exists():
        print(f"商品文件不存在: {products_file}")
        return False
    
    # 加载数据
    print("加载FAQ数据...")
    faq_data = load_json_data(faq_file)
    print(f"加载了 {len(faq_data)} 条FAQ数据")
    
    print("加载商品数据...")
    products_data = load_json_data(products_file)
    print(f"加载了 {len(products_data)} 条商品数据")
    
    # 转换为KnowledgeItem
    print("转换数据格式...")
    faq_items = convert_to_knowledge_items(faq_data)
    product_items = convert_to_knowledge_items(products_data)
    
    all_items = faq_items + product_items
    print(f"总共 {len(all_items)} 条数据待处理")
    
    # 清空现有知识库
    print("清空现有知识库...")
    rag_service.clear_knowledge()
    
    # 添加到向量数据库
    print("添加到向量数据库...")
    success = rag_service.add_knowledge(all_items)
    
    if success:
        print("知识库初始化成功！")
        
        # 获取知识库信息
        info = rag_service.get_collection_info()
        print(f"知识库信息: {info}")
        
        return True
    else:
        print("知识库初始化失败！")
        return False

def test_search():
    """测试搜索功能"""
    print("\n测试搜索功能...")
    
    test_queries = [
        "这个商品支持发往德国吗？",
        "退货政策是什么？",
        "智能手表有什么功能？",
        "How long is the delivery time?",
        "What is the warranty period?"
    ]
    
    for query in test_queries:
        print(f"\n查询: {query}")
        try:
            context = rag_service.get_relevant_context(query, top_k=2)
            if context:
                print(f"找到相关内容: {context[:200]}...")
            else:
                print("未找到相关内容")
        except Exception as e:
            print(f"搜索失败: {e}")

def main():
    """主函数"""
    print("=" * 50)
    print("多语言检索增强商品问答 Agent - 数据初始化")
    print("=" * 50)
    
    # 检查环境变量
    if not settings.OPENAI_API_KEY:
        print("错误: 未设置 OPENAI_API_KEY 环境变量")
        print("请创建 .env 文件并设置您的 OpenAI API 密钥")
        return False
    
    # 初始化知识库
    if init_knowledge_base():
        # 测试搜索功能
        test_search()
        print("\n数据初始化完成！")
        return True
    else:
        print("数据初始化失败！")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 