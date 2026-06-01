import uuid
from pathlib import Path
from fastapi import UploadFile
from ..database import get_sqlite, knowledge_collection
from ..models.knowledge import DocumentResponse, KnowledgeStats


class RAGService:
    """RAG 服务 - 骨架实现"""

    async def upload_document(self, file: UploadFile, domain: str = None) -> DocumentResponse:
        """上传文档 - TODO: 实现文档解析和向量化"""
        db = await get_sqlite()
        try:
            file_type = Path(file.filename).suffix.lstrip(".")
            content = await file.read()

            cursor = await db.execute(
                """INSERT INTO knowledge_documents (filename, file_type, file_size, domain, status)
                   VALUES (?, ?, ?, ?, ?)""",
                (file.filename, file_type, len(content), domain, "completed")
            )
            await db.commit()
            doc_id = cursor.lastrowid

            return DocumentResponse(
                id=doc_id,
                filename=file.filename,
                file_type=file_type,
                file_size=len(content),
                chunk_count=0,
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
        """删除文档 - TODO: 同时删除 ChromaDB 中的向量"""
        db = await get_sqlite()
        try:
            await db.execute("DELETE FROM knowledge_documents WHERE id = ?", (doc_id,))
            await db.commit()
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
