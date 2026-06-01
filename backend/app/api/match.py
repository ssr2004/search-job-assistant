from fastapi import APIRouter
from ..models.resume import MatchRequest, MatchResult
from ..services.resume_service import ResumeService

router = APIRouter(prefix="/api/match", tags=["match"])
resume_service = ResumeService()


@router.post("")
async def run_match(request: MatchRequest) -> MatchResult:
    """执行匹配"""
    return await resume_service.match(request.resume_id, request.jd_id)


@router.get("/results")
async def get_results() -> list[MatchResult]:
    """获取匹配结果列表"""
    return await resume_service.get_match_results()
