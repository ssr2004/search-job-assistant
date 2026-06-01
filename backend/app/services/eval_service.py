import json
from ..database import get_sqlite
from ..models.eval import EvalExperimentCreate, EvalExperimentResponse


class EvalService:
    """评估服务 - 骨架实现"""

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
        """运行评估实验 - TODO: 实现 RAGAS 评估"""
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
