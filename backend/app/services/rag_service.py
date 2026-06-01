import tempfile
import uuid
from pathlib import Path
from fastapi import UploadFile
from ..database import get_sqlite, get_knowledge_collection
from ..models.knowledge import DocumentResponse, KnowledgeStats
from ..utils.document_parser import DocumentParser
from ..utils.embedding import encode_texts
from ..utils.hybrid_search import HybridSearchService
from ..utils.reranker import rerank


class RAGService:
    """RAG 服务"""

    def __init__(self):
        self.parser = DocumentParser()
        self.search_service = HybridSearchService()

    async def upload_document(self, file: UploadFile, domain: str = None) -> DocumentResponse:
        """上传文档、解析分块、向量化存储"""
        db = await get_sqlite()
        try:
            file_type = Path(file.filename).suffix.lstrip(".")
            content = await file.read()

            # 保存临时文件并解析
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_type}") as tmp:
                tmp.write(content)
                tmp_path = tmp.name

            chunks = self.parser.parse(tmp_path)
            Path(tmp_path).unlink(missing_ok=True)

            # 插入数据库记录
            cursor = await db.execute(
                """INSERT INTO knowledge_documents (filename, file_type, file_size, chunk_count, domain, status)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (file.filename, file_type, len(content), len(chunks), domain, "completed")
            )
            await db.commit()
            doc_id = cursor.lastrowid

            # 将 chunks 存入 ChromaDB
            if chunks:
                collection = get_knowledge_collection()
                texts = [c["content"] for c in chunks]
                embeddings = encode_texts(texts)
                ids = [f"doc_{doc_id}_chunk_{i}" for i in range(len(chunks))]
                metadatas = [
                    {"document_id": str(doc_id), "domain": domain or "", "chunk_index": i, "source": file.filename}
                    for i in range(len(chunks))
                ]
                collection.add(
                    ids=ids,
                    embeddings=embeddings,
                    documents=texts,
                    metadatas=metadatas,
                )

            # 刷新搜索索引
            self.search_service.refresh_index()

            return DocumentResponse(
                id=doc_id,
                filename=file.filename,
                file_type=file_type,
                file_size=len(content),
                chunk_count=len(chunks),
                domain=domain,
                status="completed",
                created_at=""
            )
        finally:
            await db.close()

    async def get_documents(self) -> list[DocumentResponse]:
        """获取文档列表"""
        db = await get_sqlite()
        try:
            cursor = await db.execute(
                "SELECT id, filename, file_type, file_size, chunk_count, domain, status, created_at FROM knowledge_documents ORDER BY created_at DESC"
            )
            rows = await cursor.fetchall()
            return [DocumentResponse(
                id=r[0], filename=r[1], file_type=r[2], file_size=r[3],
                chunk_count=r[4], domain=r[5], status=r[6], created_at=str(r[7])
            ) for r in rows]
        finally:
            await db.close()

    async def delete_document(self, doc_id: int):
        """删除文档及 ChromaDB 中的向量"""
        db = await get_sqlite()
        try:
            # 从 ChromaDB 删除该文档的所有 chunks
            collection = get_knowledge_collection()
            collection.delete(where={"document_id": str(doc_id)})

            # 从 SQLite 删除记录
            await db.execute("DELETE FROM knowledge_documents WHERE id = ?", (doc_id,))
            await db.commit()

            # 刷新搜索索引
            self.search_service.refresh_index()
        finally:
            await db.close()

    async def get_stats(self) -> KnowledgeStats:
        """获取知识库统计"""
        db = await get_sqlite()
        try:
            cursor = await db.execute("SELECT COUNT(*), SUM(chunk_count) FROM knowledge_documents")
            row = await cursor.fetchone()
            total_docs = row[0] or 0
            total_chunks = row[1] or 0

            cursor = await db.execute("SELECT DISTINCT domain FROM knowledge_documents WHERE domain IS NOT NULL")
            domains = [r[0] for r in await cursor.fetchall()]

            return KnowledgeStats(
                total_documents=total_docs,
                total_chunks=total_chunks,
                domains=domains
            )
        finally:
            await db.close()

    async def search(self, query: str, domain: str = None, top_k: int = 20, rerank_top_k: int = 5) -> list[dict]:
        """混合检索 + Re-ranking 精排"""
        # 混合检索
        candidates = await self.search_service.search(query, domain, top_k)

        # Re-ranking 精排
        reranked = await rerank(query, candidates, rerank_top_k)

        return reranked
