import tempfile
import uuid
from pathlib import Path
from fastapi import UploadFile
from ..database import get_sqlite
from ..models.knowledge import DocumentResponse, KnowledgeStats
from ..utils.document_parser import DocumentParser


class RAGService:
    """RAG 服务"""

    def __init__(self):
        self.parser = DocumentParser()

    async def upload_document(self, file: UploadFile, domain: str = None) -> DocumentResponse:
        """上传文档并解析分块"""
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

            # TODO: 步骤5 - 将 chunks 存入 ChromaDB

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
