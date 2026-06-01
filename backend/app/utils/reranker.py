import httpx
from ..config import get_settings

settings = get_settings()

JINA_RERANK_URL = "https://api.jina.ai/v1/rerank"


async def rerank(query: str, documents: list[dict], top_k: int = 5) -> list[dict]:
    """Jina AI Re-ranking 精排"""
    if not documents:
        return []

    if not settings.jina_api_key:
        # 没有配置 Jina API Key，跳过精排，直接返回 top_k
        return documents[:top_k]

    texts = [doc["content"] for doc in documents]

    async with httpx.AsyncClient() as client:
        response = await client.post(
            JINA_RERANK_URL,
            headers={
                "Authorization": f"Bearer {settings.jina_api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "jina-reranker-v2-base-multilingual",
                "query": query,
                "documents": texts,
                "top_n": top_k,
                "return_documents": False
            },
            timeout=30.0
        )

    if response.status_code != 200:
        # API 调用失败，降级返回 top_k
        return documents[:top_k]

    result = response.json()
    reranked = []
    for item in result["results"]:
        idx = item["index"]
        doc = documents[idx].copy()
        doc["rerank_score"] = item["relevance_score"]
        reranked.append(doc)

    return reranked
