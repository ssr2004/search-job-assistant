from fastapi import APIRouter, UploadFile, File
from ..models.resume import ResumeResponse, ResumeDetail
from ..services.resume_service import ResumeService

router = APIRouter(prefix="/api/resume", tags=["resume"])
resume_service = ResumeService()


@router.post("/upload")
async def upload_resume(file: UploadFile = File(...)) -> ResumeResponse:
    """上传简历"""
    return await resume_service.upload(file)


@router.get("/list")
async def list_resumes() -> list[ResumeResponse]:
    """获取简历列表"""
    return await resume_service.list_all()


@router.get("/{resume_id}")
async def get_resume(resume_id: int) -> ResumeDetail:
    """获取简历详情"""
    return await resume_service.get_detail(resume_id)
