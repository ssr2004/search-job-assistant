from fastapi import APIRouter, UploadFile, File, Form, Query
from typing import Optional
from ..models.knowledge import DocumentResponse, KnowledgeStats
from ..services.rag_service import RAGService

router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])
rag_service = RAGService()


@router.post("/documents")
async def upload_document(
    file: UploadFile = File(...),
    domain: Optional[str] = Form(None)
) -> DocumentResponse:
    """上传文档"""
    return await rag_service.upload_document(file, domain)


@router.get("/documents")
async def get_documents() -> list[DocumentResponse]:
    """获取文档列表"""
    return await rag_service.get_documents()


@router.delete("/documents/{doc_id}")
async def delete_document(doc_id: int):
    """删除文档"""
    await rag_service.delete_document(doc_id)


@router.get("/stats")
async def get_stats() -> KnowledgeStats:
    """获取知识库统计"""
    return await rag_service.get_stats()


@router.get("/search")
async def search(
    query: str = Query(..., description="搜索查询"),
    domain: Optional[str] = Query(None, description="领域过滤"),
    top_k: int = Query(20, description="候选数量"),
    rerank_top_k: int = Query(5, description="精排后返回数量")
) -> list[dict]:
    """混合检索 + Re-ranking 精排"""
    return await rag_service.search(query, domain, top_k, rerank_top_k)
