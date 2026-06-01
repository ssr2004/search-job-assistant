from fastapi import APIRouter
from ..models.eval import EvalExperimentCreate, EvalExperimentResponse
from ..services.eval_service import EvalService

router = APIRouter(prefix="/api/eval", tags=["eval"])
eval_service = EvalService()


@router.post("/experiments")
async def create_experiment(request: EvalExperimentCreate) -> EvalExperimentResponse:
    """创建评估实验"""
    return await eval_service.create_experiment(request)


@router.post("/experiments/{exp_id}/run")
async def run_experiment(exp_id: int) -> EvalExperimentResponse:
    """运行评估实验"""
    return await eval_service.run_experiment(exp_id)


@router.get("/experiments/{exp_id}")
async def get_experiment(exp_id: int) -> EvalExperimentResponse:
    """获取实验结果"""
    return await eval_service.get_experiment(exp_id)
