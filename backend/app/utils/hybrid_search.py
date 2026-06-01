import numpy as np
from rank_bm25 import BM25Okapi
import jieba
from ..database import get_knowledge_collection
from .embedding import encode_text


class HybridSearchService:
    """混合检索服务：向量检索 + BM25 关键词检索 + RRF 融合"""

    def __init__(self, rrf_k: int = 60):
        self.rrf_k = rrf_k
        self._bm25_index = None
        self._documents = None
        self._doc_ids = None

    def _build_bm25_index(self):
        """构建 BM25 索引"""
        collection = get_knowledge_collection()
        result = collection.get(include=["documents", "metadatas"])

        if not result["ids"]:
            self._documents = []
            self._doc_ids = []
            self._bm25_index = None
            return

        self._doc_ids = result["ids"]
        self._documents = result["documents"]

        # 中文分词
        tokenized_docs = [list(jieba.cut(doc)) for doc in self._documents]
        self._bm25_index = BM25Okapi(tokenized_docs)

    def _ensure_index(self):
        """确保索引已构建"""
        if self._bm25_index is None:
            self._build_bm25_index()

    async def search(self, query: str, domain: str = None, top_k: int = 20) -> list[dict]:
        """混合检索：向量 + BM25 + RRF 融合"""
        self._ensure_index()

        # 向量检索
        vector_results = self._vector_search(query, domain, top_k)

        # BM25 关键词检索
        keyword_results = self._keyword_search(query, domain, top_k)

        # RRF 融合
        fused = self._rrf_fusion(vector_results, keyword_results, top_k)

        return fused

    def _vector_search(self, query: str, domain: str, top_k: int) -> list[dict]:
        """向量语义检索"""
        collection = get_knowledge_collection()
        query_embedding = encode_text(query)

        where_filter = {"domain": domain} if domain else None
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, collection.count()),
            where=where_filter,
            include=["documents", "metadatas", "distances"]
        )

        docs = []
        if results["ids"] and results["ids"][0]:
            for i, doc_id in enumerate(results["ids"][0]):
                docs.append({
                    "id": doc_id,
                    "content": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i]
                })
        return docs

    def _keyword_search(self, query: str, domain: str, top_k: int) -> list[dict]:
        """BM25 关键词检索"""
        if not self._bm25_index or not self._documents:
            return []

        # 中文分词
        tokens = list(jieba.cut(query))
        scores = self._bm25_index.get_scores(tokens)

        # 获取 top_k 索引
        top_indices = np.argsort(scores)[-top_k:][::-1]

        results = []
        for idx in top_indices:
            if scores[idx] > 0:
                results.append({
                    "id": self._doc_ids[idx],
                    "content": self._documents[idx],
                    "score": float(scores[idx])
                })
        return results

    def _rrf_fusion(self, vector_results: list[dict], keyword_results: list[dict], top_k: int) -> list[dict]:
        """Reciprocal Rank Fusion 融合"""
        scores = {}
        doc_map = {}

        # 向量检索结果
        for rank, doc in enumerate(vector_results):
            doc_id = doc["id"]
            scores[doc_id] = scores.get(doc_id, 0) + 1 / (self.rrf_k + rank + 1)
            doc_map[doc_id] = doc

        # 关键词检索结果
        for rank, doc in enumerate(keyword_results):
            doc_id = doc["id"]
            scores[doc_id] = scores.get(doc_id, 0) + 1 / (self.rrf_k + rank + 1)
            if doc_id not in doc_map:
                doc_map[doc_id] = doc

        # 按 RRF 分数排序
        sorted_ids = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        results = []
        for doc_id, score in sorted_ids[:top_k]:
            doc = doc_map[doc_id]
            doc["rrf_score"] = score
            results.append(doc)

        return results

    def refresh_index(self):
        """刷新 BM25 索引（文档更新后调用）"""
        self._bm25_index = None
        self._documents = None
        self._doc_ids = None
