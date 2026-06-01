from fastapi import APIRouter
from ..models.resume import JDCreate, JDResponse, JDDetail
from ..services.resume_service import ResumeService

router = APIRouter(prefix="/api/jd", tags=["jd"])
resume_service = ResumeService()


@router.post("/create")
async def create_jd(request: JDCreate) -> JDResponse:
    """创建 JD"""
    return await resume_service.create_jd(request)


@router.get("/list")
async def list_jds() -> list[JDResponse]:
    """获取 JD 列表"""
    return await resume_service.list_jds()


@router.get("/{jd_id}")
async def get_jd(jd_id: int) -> JDDetail:
    """获取 JD 详情"""
    return await resume_service.get_jd_detail(jd_id)
