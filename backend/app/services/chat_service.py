import json
import uuid
from ..database import get_sqlite
from ..models.chat import ChatRequest, ChatSession, ChatMessage


class ChatService:
    """对话服务 - 骨架实现"""

    async def stream_chat(self, request: ChatRequest):
        """SSE 流式对话 - TODO: 实现 LLM 调用"""
        # 骨架：返回模拟数据
        yield json.dumps({"content": "这是流式响应的骨架实现，请接入 LLM 服务。"}, ensure_ascii=False)

    async def get_sessions(self) -> list[ChatSession]:
        """获取会话列表"""
        db = await get_sqlite()
        try:
            cursor = await db.execute(
                "SELECT session_id, title, domain FROM chat_sessions ORDER BY created_at DESC"
            )
            rows = await cursor.fetchall()
            return [ChatSession(session_id=r[0], title=r[1], domain=r[2]) for r in rows]
        finally:
            await db.close()

    async def get_messages(self, session_id: str) -> list[ChatMessage]:
        """获取会话消息"""
        db = await get_sqlite()
        try:
            cursor = await db.execute(
                "SELECT role, content FROM chat_messages WHERE session_id = ? ORDER BY created_at",
                (session_id,)
            )
            rows = await cursor.fetchall()
            return [ChatMessage(role=r[0], content=r[1]) for r in rows]
        finally:
            await db.close()
