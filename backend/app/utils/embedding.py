import dashscope
from dashscope import TextEmbedding
from ..config import get_settings

settings = get_settings()

# 设置 API Key
dashscope.api_key = settings.llm_api_key


def encode_texts(texts: list[str]) -> list[list[float]]:
    """批量编码文本为向量（通义千问 Embedding API）"""
    response = TextEmbedding.call(
        model=TextEmbedding.Models.text_embedding_v3,
        input=texts
    )
    if response.status_code != 200:
        raise Exception(f"Embedding API 调用失败: {response.code} - {response.message}")
    return [item["embedding"] for item in response.output["embeddings"]]


def encode_text(text: str) -> list[float]:
    """编码单个文本为向量"""
    return encode_texts([text])[0]
