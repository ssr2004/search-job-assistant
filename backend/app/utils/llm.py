import json
import dashscope
from dashscope import Generation
from ..config import get_settings
from .tools import TOOLS, execute_tool

settings = get_settings()

# 设置 API Key
dashscope.api_key = settings.llm_api_key

SYSTEM_PROMPT = """你是一个专业的求职助手，帮助用户准备面试、回答技术问题。
你可以使用知识库检索工具来查找相关文档，帮助回答用户的问题。
当用户的问题需要参考资料或专业知识时，请使用 knowledge_search 工具。"""


async def chat_stream(messages: list[dict], domain: str = None):
    """流式对话（通义千问），支持 Tool Calling"""
    system_prompt = SYSTEM_PROMPT
    if domain:
        system_prompt += f"\n当前领域：{domain}。请专注于该领域的知识。"

    full_messages = [{"role": "system", "content": system_prompt}] + messages

    # 第一次调用，检查是否需要工具
    response = Generation.call(
        model=settings.llm_model,
        messages=full_messages,
        tools=TOOLS,
        result_format="message"
    )

    if response.status_code != 200:
        yield f"\n[错误: {response.code} - {response.message}]"
        return

    choice = response.output.choices[0]

    # 检查是否有工具调用
    try:
        tool_calls = choice.message.tool_calls
    except (KeyError, AttributeError):
        tool_calls = None

    if tool_calls:
        # 执行工具调用
        for tool_call in choice.message.tool_calls:
            tool_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)

            # 执行工具
            tool_result = await execute_tool(tool_name, arguments)

            # 添加工具调用和结果到消息
            full_messages.append({
                "role": "assistant",
                "content": None,
                "tool_calls": [tool_call]
            })
            full_messages.append({
                "role": "tool",
                "content": tool_result,
                "tool_call_id": tool_call.id
            })

        # 第二次调用，流式输出最终回答
        responses = Generation.call(
            model=settings.llm_model,
            messages=full_messages,
            result_format="message",
            stream=True,
            incremental_output=True
        )

        for resp in responses:
            if resp.status_code == 200:
                content = resp.output.choices[0].message.content
                if content:
                    yield content
            else:
                yield f"\n[错误: {resp.code} - {resp.message}]"
                break
    else:
        # 没有工具调用，直接流式输出
        content = choice.message.content
        if content:
            yield content


async def chat_complete(messages: list[dict], domain: str = None) -> str:
    """非流式对话（通义千问），支持 Tool Calling"""
    system_prompt = SYSTEM_PROMPT
    if domain:
        system_prompt += f"\n当前领域：{domain}。请专注于该领域的知识。"

    full_messages = [{"role": "system", "content": system_prompt}] + messages

    # 第一次调用，检查是否需要工具
    response = Generation.call(
        model=settings.llm_model,
        messages=full_messages,
        tools=TOOLS,
        result_format="message"
    )

    if response.status_code != 200:
        raise Exception(f"LLM 调用失败: {response.code} - {response.message}")

    choice = response.output.choices[0]

    # 检查是否有工具调用
    try:
        tool_calls = choice.message.tool_calls
    except (KeyError, AttributeError):
        tool_calls = None

    if tool_calls:
        # 执行工具调用
        for tool_call in choice.message.tool_calls:
            tool_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)

            # 执行工具
            tool_result = await execute_tool(tool_name, arguments)

            # 添加工具调用和结果到消息
            full_messages.append({
                "role": "assistant",
                "content": None,
                "tool_calls": [tool_call]
            })
            full_messages.append({
                "role": "tool",
                "content": tool_result,
                "tool_call_id": tool_call.id
            })

        # 第二次调用，获取最终回答
        response = Generation.call(
            model=settings.llm_model,
            messages=full_messages,
            result_format="message"
        )

        if response.status_code == 200:
            return response.output.choices[0].message.content
        else:
            raise Exception(f"LLM 调用失败: {response.code} - {response.message}")
    else:
        # 没有工具调用，直接返回
        return choice.message.content
