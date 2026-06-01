from fastapi import APIRouter
from ..models.eval import GapAnalysisRequest, GapAnalysisResponse
from ..services.resume_service import ResumeService

router = APIRouter(prefix="/api/gap", tags=["gap"])
resume_service = ResumeService()


@router.post("/analyze")
async def analyze_gap(request: GapAnalysisRequest) -> GapAnalysisResponse:
    """分析技能差距"""
    return await resume_service.analyze_gap(request.resume_id, request.jd_id)
