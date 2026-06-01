import json
import uuid
from ..database import get_sqlite
from ..models.chat import ChatRequest, ChatSession, ChatMessage
from ..utils.llm import chat_stream


class ChatService:
    """对话服务"""

    async def stream_chat(self, request: ChatRequest):
        """SSE 流式对话"""
        # 获取历史消息
        history = await self._get_history(request.session_id)

        # 添加当前用户消息
        history.append({"role": "user", "content": request.message})

        # 保存用户消息
        await self._save_message(request.session_id, "user", request.message)

        # 流式调用 LLM
        full_response = ""
        async for chunk in chat_stream(history, request.domain):
            full_response += chunk
            yield json.dumps({"content": chunk}, ensure_ascii=False)

        # 保存助手消息
        await self._save_message(request.session_id, "assistant", full_response)

    async def _get_history(self, session_id: str) -> list[dict]:
        """获取对话历史"""
        db = await get_sqlite()
        try:
            cursor = await db.execute(
                "SELECT role, content FROM chat_messages WHERE session_id = ? ORDER BY created_at",
                (session_id,)
            )
            rows = await cursor.fetchall()
            return [{"role": r[0], "content": r[1]} for r in rows]
        finally:
            await db.close()

    async def _save_message(self, session_id: str, role: str, content: str):
        """保存消息"""
        db = await get_sqlite()
        try:
            # 确保会话存在
            await db.execute(
                "INSERT OR IGNORE INTO chat_sessions (session_id, title) VALUES (?, ?)",
                (session_id, content[:50])
            )
            await db.execute(
                "INSERT INTO chat_messages (session_id, role, content) VALUES (?, ?, ?)",
                (session_id, role, content)
            )
            await db.commit()
        finally:
            await db.close()

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
