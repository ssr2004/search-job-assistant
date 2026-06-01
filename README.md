# 智能求职助手

一个面向求职者的智能助手平台，覆盖从"面试准备"到"简历投递"的完整求职流程。

## 功能特性

- **智能对话**：SSE 流式响应 + Tool Calling，支持 LLM 自主调用知识库检索
- **知识库管理**：文档上传（PDF/MD/TXT）→ 智能分块 → 向量化存储 → 混合检索
- **简历筛选**：上传简历 + JD → 多维度匹配评分 → 生成筛选报告
- **技能差距分析**：自动识别候选人与 JD 的技能差距 → 生成学习推荐
- **RAGAS 评估**：四指标评估（Faithfulness / Context Precision / Recall / Relevancy）

## 技术架构

```
┌─────────────────────────────────────────────────────────┐
│                    前端 (React + TypeScript)              │
│    智能对话 │ 知识库 │ 简历筛选 │ 评估报告 │ 技能差距     │
└────────────────────────┬────────────────────────────────┘
                         │ REST API + SSE
┌────────────────────────▼────────────────────────────────┐
│                    后端 (FastAPI + Python)                │
│                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │  RAG 引擎    │  │  对话服务    │  │  匹配引擎    │     │
│  │             │  │             │  │             │     │
│  │ • 文档解析   │  │ • SSE 流式  │  │ • 硬性条件   │     │
│  │ • 混合检索   │  │ • Tool Call │  │ • 语义匹配   │     │
│  │ • Re-ranking│  │ • 多轮对话  │  │ • 综合评分   │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
│                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │  评估服务    │  │  差距分析    │  │  LLM 服务    │     │
│  │             │  │             │  │             │     │
│  │ • RAGAS     │  │ • 差距识别   │  │ • 通义千问   │     │
│  │ • 四指标    │  │ • 学习推荐   │  │ • Embedding │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  基础设施：SQLite │ ChromaDB │ Jina AI Re-ranking│   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

## 技术栈

### 后端
| 技术 | 用途 |
|------|------|
| Python 3.11+ | 主语言 |
| FastAPI | Web 框架（原生异步 + SSE） |
| ChromaDB | 向量数据库 |
| SQLite | 业务数据存储 |
| dashscope | 通义千问 SDK（LLM + Embedding） |
| Jina AI | Re-ranking 精排 |
| rank-bm25 | BM25 关键词检索 |
| jieba | 中文分词 |
| PyMuPDF | PDF 解析 |

### 前端
| 技术 | 用途 |
|------|------|
| React 18 | UI 框架 |
| TypeScript | 类型安全 |
| Ant Design 5 | 组件库 |
| Vite 6 | 构建工具 |
| react-markdown | Markdown 渲染 |

## 快速开始

### 环境要求
- Python 3.11+
- Node.js 18+
- Docker（可选，用于运行后端）

### 1. 克隆项目
```bash
git clone https://github.com/ssr2004/search-job-assistant.git
cd search-job-assistant
```

### 2. 配置 API Key
编辑 `backend/.env`，填入你的 API Key：
```env
# 通义千问（必填）
LLM_API_KEY=你的dashscope_api_key

# Jina AI Re-ranking（可选，不填则跳过精排）
JINA_API_KEY=你的jina_api_key
```

获取 API Key：
- 通义千问：https://bailian.console.aliyun.com/
- Jina AI：https://jina.ai/reranker/

### 3. 启动后端

**方式一：Docker（推荐）**
```bash
# 构建并启动
docker-compose up -d backend

# 查看日志
docker-compose logs -f backend
```

**方式二：本地运行**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 4. 启动前端
```bash
cd frontend
npm install
npm run dev
```

访问 http://localhost:5173

## API 文档

启动后端后访问 http://localhost:8000/docs 查看 Swagger 文档。

### 主要接口

| 模块 | 接口 | 说明 |
|------|------|------|
| 对话 | `POST /api/chat/stream` | SSE 流式对话 |
| 知识库 | `POST /api/knowledge/documents` | 上传文档 |
| 知识库 | `GET /api/knowledge/search` | 混合检索 |
| 简历 | `POST /api/resume/upload` | 上传简历 |
| JD | `POST /api/jd/create` | 创建 JD |
| 匹配 | `POST /api/match` | 执行匹配 |
| 评估 | `POST /api/eval/experiments` | 创建评估实验 |
| 差距 | `POST /api/gap/analyze` | 技能差距分析 |

## RAG 检索流水线

```
用户提问 → 查询改写(可选) → 混合检索(向量+BM25+RRF) → Re-ranking精排 → LLM生成回答
```

1. **向量检索**：通义千问 Embedding → ChromaDB 语义搜索
2. **BM25 检索**：jieba 分词 → rank-bm25 关键词匹配
3. **RRF 融合**：Reciprocal Rank Fusion 融合两路结果
4. **Re-ranking**：Jina AI Reranker 精排（可选）
5. **LLM 生成**：通义千问生成最终回答

## 匹配算法

简历与 JD 的多维度匹配：

| 维度 | 权重 | 说明 |
|------|------|------|
| 硬性条件 | 30% | 学历、工作年限 |
| 技能匹配 | 30% | Embedding 语义相似度 |
| 经验匹配 | 20% | 关键词匹配 |
| 项目匹配 | 20% | 技术栈匹配 |

## 项目结构

```
search-job-assistant/
├── backend/                    # 后端
│   ├── app/
│   │   ├── api/               # API 路由（7个）
│   │   ├── services/          # 业务逻辑（4个）
│   │   ├── utils/             # 工具类
│   │   │   ├── document_parser.py   # 文档解析
│   │   │   ├── embedding.py         # Embedding
│   │   │   ├── hybrid_search.py     # 混合检索
│   │   │   ├── reranker.py          # Re-ranking
│   │   │   ├── llm.py               # LLM 服务
│   │   │   ├── tools.py             # Tool Calling
│   │   │   ├── matching.py          # 匹配引擎
│   │   │   └── ragas.py             # RAGAS 评估
│   │   ├── models/            # 数据模型
│   │   ├── config.py          # 配置
│   │   └── database.py        # 数据库
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                   # 前端
│   ├── src/
│   │   ├── pages/             # 页面（5个）
│   │   ├── components/        # 组件
│   │   ├── api/               # API 封装
│   │   └── types/             # 类型定义
│   └── package.json
├── docker-compose.yml
└── README.md
```

## 简历写法参考

> **智能求职助手** | Python / FastAPI / React / LangChain
> - 实现四阶段 RAG 检索流水线（查询改写 → 混合检索（向量+关键词 RRF 融合）→ Cross-Encoder Re-ranking 精排 → LLM 生成），基于 RAGAS 框架评估
> - 设计多维度简历匹配算法（硬性条件过滤 + 技能语义匹配 + 经验匹配 + 综合加权评分）
> - 实现 SSE 流式响应 + Tool Calling，支持 LLM 自主调用知识库检索工具
> - 构建技能差距分析模块，自动识别候选人与 JD 的技能差距并生成个性化学习推荐

## License

MIT
