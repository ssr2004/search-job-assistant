import dashscope
from dashscope import Generation
from ..config import get_settings

settings = get_settings()

# 设置 API Key
dashscope.api_key = settings.llm_api_key


async def chat_stream(messages: list[dict], domain: str = None):
    """流式对话（通义千问）"""
    system_prompt = "你是一个专业的求职助手，帮助用户准备面试、回答技术问题。"
    if domain:
        system_prompt += f"当前领域：{domain}。请专注于该领域的知识。"

    full_messages = [{"role": "system", "content": system_prompt}] + messages

    responses = Generation.call(
        model=settings.llm_model,
        messages=full_messages,
        result_format="message",
        stream=True,
        incremental_output=True
    )

    for response in responses:
        if response.status_code == 200:
            content = response.output.choices[0].message.content
            if content:
                yield content
        else:
            yield f"\n[错误: {response.code} - {response.message}]"
            break


async def chat_complete(messages: list[dict], domain: str = None) -> str:
    """非流式对话（通义千问）"""
    system_prompt = "你是一个专业的求职助手，帮助用户准备面试、回答技术问题。"
    if domain:
        system_prompt += f"当前领域：{domain}。请专注于该领域的知识。"

    full_messages = [{"role": "system", "content": system_prompt}] + messages

    response = Generation.call(
        model=settings.llm_model,
        messages=full_messages,
        result_format="message"
    )

    if response.status_code == 200:
        return response.output.choices[0].message.content
    else:
        raise Exception(f"LLM 调用失败: {response.code} - {response.message}")
