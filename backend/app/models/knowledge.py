from pydantic import BaseModel
from typing import Optional


class DocumentUpload(BaseModel):
    domain: Optional[str] = None


class DocumentResponse(BaseModel):
    id: int
    filename: str
    file_type: str
    file_size: int
    chunk_count: int
    domain: Optional[str]
    status: str
    created_at: str


class KnowledgeStats(BaseModel):
    total_documents: int
    total_chunks: int
    domains: list[str]
