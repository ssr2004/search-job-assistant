from pydantic import BaseModel
from typing import Optional


class EvalExperimentCreate(BaseModel):
    name: str


class EvalExperimentResponse(BaseModel):
    id: int
    name: str
    status: str
    faithfulness: Optional[float]
    context_precision: Optional[float]
    context_recall: Optional[float]
    answer_relevancy: Optional[float]
    details: Optional[dict]
    created_at: str


class GapAnalysisRequest(BaseModel):
    resume_id: int
    jd_id: int


class GapAnalysisResponse(BaseModel):
    required_match_rate: float
    preferred_match_rate: float
    overall_match_rate: float
    matched_required: list[str]
    missing_required: list[str]
    matched_preferred: list[str]
    missing_preferred: list[str]
    recommendations: list[dict]
