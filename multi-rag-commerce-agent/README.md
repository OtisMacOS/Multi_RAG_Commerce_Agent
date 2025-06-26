# Multi-RAG Commerce Agent

多语言检索增强商品问答智能体系统

## 项目概述

这是一个基于RAG（检索增强生成）技术的多语言商品问答系统，支持中英文混合输入、上下文记忆和多轮对话。

## 功能特性

- 🌍 多语言支持（中文/英文）
- 🧠 上下文记忆管理
- 🔍 RAG检索增强
- 🤖 智能Agent响应
- 📊 实时对话历史
- ⚡ 快速响应（<3秒）

## 技术栈

- **Web框架**: FastAPI
- **LLM框架**: LangChain
- **向量数据库**: ChromaDB
- **语言模型**: OpenAI GPT-4
- **Embedding模型**: OpenAI Embedding
- **数据验证**: Pydantic

## 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd multi-rag-commerce-agent

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 环境变量配置

创建 `.env` 文件并配置以下变量：

```env
# OpenAI配置
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_EMBEDDING_MODEL=text-embedding-ada-002

# 向量数据库配置
CHROMA_PERSIST_DIRECTORY=./chroma_db
CHROMA_COLLECTION_NAME=commerce_knowledge

# 应用配置
DEBUG=False
MAX_TOKENS=1000
TEMPERATURE=0.7
TOP_K_RETRIEVAL=5
MAX_HISTORY_LENGTH=10
```

### 4. 运行应用

```bash
# 开发模式
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 5. 访问API文档

打开浏览器访问：http://localhost:8000/docs

## API接口

### 主要接口

| 接口 | 方法 | 描述 |
|------|------|------|
| `/chat` | POST | 主要聊天接口 |
| `/history` | GET | 获取对话历史 |
| `/memory` | POST | 记忆管理 |
| `/health` | GET | 健康检查 |

### 聊天接口示例

```bash
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{
       "message": "这个商品支持发往德国吗？",
       "user_id": "user123",
       "session_id": "session456"
     }'
```

## 项目结构

```
multi-rag-commerce-agent/
├── app/
│   ├── main.py              # FastAPI主应用
│   ├── config.py            # 配置文件
│   ├── models/              # 数据模型
│   ├── services/            # 核心服务
│   ├── api/                 # API路由
│   └── utils/               # 工具函数
├── data/                    # 示例数据
├── requirements.txt         # 依赖包
└── README.md               # 项目说明
```

## 开发计划

本项目按照5小时开发计划进行，分为5个阶段：

1. **项目初始化** (30分钟) - 环境搭建
2. **核心服务开发** (2小时) - RAG、Agent、语言处理
3. **API接口开发** (1小时) - FastAPI应用
4. **数据准备与测试** (1小时) - 示例数据和测试
5. **部署与优化** (30分钟) - 性能优化

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证

MIT License

## 联系方式

如有问题，请提交 Issue 或联系开发团队。 