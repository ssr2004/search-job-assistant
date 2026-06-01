import json
from ..database import get_sqlite
from ..models.eval import EvalExperimentCreate, EvalExperimentResponse
from ..utils.ragas import evaluate_rag


class EvalService:
    """评估服务"""

    # 默认测试用例
    DEFAULT_TEST_CASES = [
        {
            "question": "Python 的主要特点是什么？",
            "ground_truth": "Python 是一种解释型、面向对象、动态数据类型的高级程序设计语言",
            "ground_truth_contexts": ["Python 是一种解释型、面向对象、动态数据类型的高级程序设计语言"]
        },
        {
            "question": "什么是 RAG？",
            "ground_truth": "RAG（检索增强生成）是一种结合检索和生成的技术",
            "ground_truth_contexts": ["RAG（检索增强生成）是一种结合检索和生成的技术"]
        }
    ]

    async def create_experiment(self, request: EvalExperimentCreate) -> EvalExperimentResponse:
        """创建评估实验"""
        db = await get_sqlite()
        try:
            cursor = await db.execute(
                "INSERT INTO eval_experiments (name, status) VALUES (?, ?)",
                (request.name, "pending")
            )
            await db.commit()
            return EvalExperimentResponse(
                id=cursor.lastrowid, name=request.name, status="pending",
                faithfulness=None, context_precision=None, context_recall=None,
                answer_relevancy=None, details=None, created_at=""
            )
        finally:
            await db.close()

    async def run_experiment(self, exp_id: int) -> EvalExperimentResponse:
        """运行评估实验"""
        # 获取实验信息
        db = await get_sqlite()
        try:
            cursor = await db.execute("SELECT name FROM eval_experiments WHERE id = ?", (exp_id,))
            row = await cursor.fetchone()
            if not row:
                raise ValueError("Experiment not found")

            # 更新状态为运行中
            await db.execute("UPDATE eval_experiments SET status = 'running' WHERE id = ?", (exp_id,))
            await db.commit()
        finally:
            await db.close()

        # 运行 RAGAS 评估
        result = await evaluate_rag(self.DEFAULT_TEST_CASES)

        # 保存结果
        db = await get_sqlite()
        try:
            await db.execute(
                """UPDATE eval_experiments
                   SET status = 'completed', faithfulness = ?, context_precision = ?,
                       context_recall = ?, answer_relevancy = ?, details = ?
                   WHERE id = ?""",
                (result["metrics"]["faithfulness"],
                 result["metrics"]["context_precision"],
                 result["metrics"]["context_recall"],
                 result["metrics"]["answer_relevancy"],
                 json.dumps(result, ensure_ascii=False),
                 exp_id)
            )
            await db.commit()
        finally:
            await db.close()

        return await self.get_experiment(exp_id)

    async def get_experiment(self, exp_id: int) -> EvalExperimentResponse:
        """获取实验结果"""
        db = await get_sqlite()
        try:
            cursor = await db.execute(
                "SELECT id, name, status, faithfulness, context_precision, context_recall, answer_relevancy, details, created_at FROM eval_experiments WHERE id = ?",
                (exp_id,)
            )
            row = await cursor.fetchone()
            if not row:
                raise ValueError("Experiment not found")
            details = json.loads(row[7]) if row[7] else None
            return EvalExperimentResponse(
                id=row[0], name=row[1], status=row[2],
                faithfulness=row[3], context_precision=row[4],
                context_recall=row[5], answer_relevancy=row[6],
                details=details, created_at=str(row[8])
            )
        finally:
            await db.close()
