from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from ..models.chat import ChatRequest, ChatSession, ChatMessage
from ..services.chat_service import ChatService

router = APIRouter(prefix="/api/chat", tags=["chat"])
chat_service = ChatService()


@router.post("/stream")
async def chat_stream(request: ChatRequest):
    """SSE 流式对话"""
    async def generate():
        async for chunk in chat_service.stream_chat(request):
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@router.get("/sessions")
async def get_sessions() -> list[ChatSession]:
    """获取会话列表"""
    return await chat_service.get_sessions()


@router.get("/sessions/{session_id}/messages")
async def get_messages(session_id: str) -> list[ChatMessage]:
    """获取会话消息"""
    return await chat_service.get_messages(session_id)
