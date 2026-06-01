from pydantic import BaseModel
from typing import Optional


class ChatRequest(BaseModel):
    session_id: str
    message: str
    domain: Optional[str] = None


class ChatSession(BaseModel):
    session_id: str
    title: Optional[str] = None
    domain: Optional[str] = None


class ChatMessage(BaseModel):
    role: str
    content: str
