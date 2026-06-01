from ..services.rag_service import RAGService

rag_service = RAGService()

# 工具定义
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "knowledge_search",
            "description": "从知识库中检索相关文档，用于回答用户问题。当用户询问需要参考资料的问题时使用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索查询"
                    },
                    "domain": {
                        "type": "string",
                        "description": "领域过滤（可选）"
                    }
                },
                "required": ["query"]
            }
        }
    }
]


async def execute_tool(tool_name: str, arguments: dict) -> str:
    """执行工具调用"""
    if tool_name == "knowledge_search":
        query = arguments.get("query", "")
        domain = arguments.get("domain")
        results = await rag_service.search(query, domain, top_k=20, rerank_top_k=5)

        if not results:
            return "未找到相关文档。"

        formatted = []
        for i, doc in enumerate(results):
            formatted.append(f"[{i+1}] {doc['content'][:300]}...")

        return "\n\n".join(formatted)

    return f"未知工具: {tool_name}"
