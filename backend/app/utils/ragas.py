import json
from ..utils.llm import chat_complete
from ..services.rag_service import RAGService

rag_service = RAGService()


async def evaluate_rag(test_cases: list[dict]) -> dict:
    """RAGAS 评估"""
    results = []

    for case in test_cases:
        question = case["question"]
        ground_truth = case.get("ground_truth", "")
        ground_truth_contexts = case.get("ground_truth_contexts", [])

        # 运行 RAG 获取回答和上下文
        answer, contexts = await run_rag(question)

        # 计算各指标
        faithfulness = await calc_faithfulness(answer, contexts)
        context_precision = await calc_context_precision(question, contexts, ground_truth_contexts)
        context_recall = await calc_context_recall(contexts, ground_truth_contexts)
        answer_relevancy = await calc_answer_relevancy(question, answer)

        results.append({
            "question": question,
            "answer": answer,
            "contexts": contexts,
            "metrics": {
                "faithfulness": faithfulness,
                "context_precision": context_precision,
                "context_recall": context_recall,
                "answer_relevancy": answer_relevancy
            }
        })

    # 汇总
    if results:
        avg_metrics = {
            "faithfulness": sum(r["metrics"]["faithfulness"] for r in results) / len(results),
            "context_precision": sum(r["metrics"]["context_precision"] for r in results) / len(results),
            "context_recall": sum(r["metrics"]["context_recall"] for r in results) / len(results),
            "answer_relevancy": sum(r["metrics"]["answer_relevancy"] for r in results) / len(results),
        }
    else:
        avg_metrics = {"faithfulness": 0, "context_precision": 0, "context_recall": 0, "answer_relevancy": 0}

    return {
        "metrics": avg_metrics,
        "details": results
    }


async def run_rag(question: str) -> tuple:
    """运行 RAG 获取回答和上下文"""
    # 检索相关文档
    search_results = await rag_service.search(question, top_k=20, rerank_top_k=5)
    contexts = [doc["content"] for doc in search_results]

    # 生成回答
    context_text = "\n---\n".join(contexts)
    prompt = f"""基于以下参考资料回答问题。

参考资料：
{context_text}

问题：{question}

请直接回答问题，不要提及"根据参考资料"等字样。"""

    messages = [{"role": "user", "content": prompt}]
    answer = await chat_complete(messages)

    return answer, contexts


async def calc_faithfulness(answer: str, contexts: list[str]) -> float:
    """忠实度：从回答提取声明 → 验证是否有上下文支持"""
    # 提取声明
    claims = await extract_claims(answer)

    if not claims:
        return 1.0

    # 验证每个声明
    supported_count = 0
    for claim in claims:
        is_supported = await verify_claim(claim, contexts)
        if is_supported:
            supported_count += 1

    return supported_count / len(claims)


async def extract_claims(answer: str) -> list[str]:
    """从回答中提取事实性声明"""
    prompt = f"""请从以下回答中提取最多10个核心事实性陈述，以JSON数组格式输出，不要添加其他文字：
{answer}"""

    messages = [{"role": "user", "content": prompt}]
    result = await chat_complete(messages)

    try:
        if "```json" in result:
            result = result.split("```json")[1].split("```")[0]
        elif "```" in result:
            result = result.split("```")[1].split("```")[0]
        return json.loads(result.strip())
    except:
        return []


async def verify_claim(claim: str, contexts: list[str]) -> bool:
    """验证声明是否有上下文支持"""
    context_block = "\n---\n".join(contexts)
    prompt = f"""判断以下陈述是否被参考资料支持。只回答 SUPPORTED 或 NOT_SUPPORTED。

参考资料：
{context_block}

待验证陈述：
{claim}"""

    messages = [{"role": "user", "content": prompt}]
    result = await chat_complete(messages)
    return "SUPPORTED" in result.upper()


async def calc_context_precision(question: str, contexts: list[str], ground_truth_contexts: list[str]) -> float:
    """上下文精确度"""
    if not contexts or not ground_truth_contexts:
        return 0.5

    # 简化实现：检查检索到的上下文中有多少与标准答案相关
    relevant_count = 0
    for ctx in contexts:
        is_relevant = await check_relevance(ctx, ground_truth_contexts)
        if is_relevant:
            relevant_count += 1

    return relevant_count / len(contexts) if contexts else 0


async def calc_context_recall(contexts: list[str], ground_truth_contexts: list[str]) -> float:
    """上下文召回率"""
    if not contexts or not ground_truth_contexts:
        return 0.5

    # 简化实现：检查标准答案中有多少被检索到
    recalled_count = 0
    for gt_ctx in ground_truth_contexts:
        is_recalled = await check_relevance(gt_ctx, contexts)
        if is_recalled:
            recalled_count += 1

    return recalled_count / len(ground_truth_contexts) if ground_truth_contexts else 0


async def calc_answer_relevancy(question: str, answer: str) -> float:
    """回答相关性"""
    prompt = f"""请评估以下回答与问题的相关性，给出 0-1 之间的分数（0 表示完全不相关，1 表示非常相关）。
只输出数字，不要其他文字。

问题：{question}
回答：{answer}"""

    messages = [{"role": "user", "content": prompt}]
    result = await chat_complete(messages)

    try:
        # 提取数字
        import re
        numbers = re.findall(r"0?\.\d+|[01]", result)
        if numbers:
            return float(numbers[0])
        return 0.5
    except:
        return 0.5


async def check_relevance(text: str, reference_texts: list[str]) -> bool:
    """检查文本是否与参考文本相关"""
    for ref in reference_texts:
        # 简单的关键词匹配
        if any(word in text for word in ref.split() if len(word) > 2):
            return True
    return False
