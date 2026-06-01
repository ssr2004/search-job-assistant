from pydantic import BaseModel
from typing import Optional


class ResumeUpload(BaseModel):
    pass


class ResumeResponse(BaseModel):
    id: int
    filename: str
    created_at: str


class ResumeDetail(BaseModel):
    id: int
    filename: str
    raw_text: str
    parsed_content: Optional[dict]
    created_at: str


class JDCreate(BaseModel):
    title: str
    raw_text: str


class JDResponse(BaseModel):
    id: int
    title: str
    created_at: str


class JDDetail(BaseModel):
    id: int
    title: str
    raw_text: str
    parsed_content: Optional[dict]
    created_at: str


class MatchRequest(BaseModel):
    resume_id: int
    jd_id: int


class MatchResult(BaseModel):
    id: int
    resume_id: int
    jd_id: int
    final_score: float
    hard_score: float
    skill_score: float
    exp_score: float
    project_score: float
    details: dict
    created_at: str
