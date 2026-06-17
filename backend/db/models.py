from pydantic import BaseModel
from typing import Optional, Any

class SessionResponse(BaseModel):
    session_id: str

class ResumeUploadResponse(BaseModel):
    session_id: str
    parsed_profile: dict

class CareerConfigRequest(BaseModel):
    session_id: str
    target_role: str
    hours_per_week: int

class DashboardResponse(BaseModel):
    session_id: str
    profile_summary: Optional[dict] = None
    role_blueprint: Optional[dict] = None
    readiness: Optional[dict] = None
    career_twin: Optional[dict] = None
    skill_gap: Optional[dict] = None
    strategy: Optional[dict] = None
    roadmap: Optional[dict] = None
    projects: Optional[Any] = None
    interview_prep: Optional[dict] = None
    agent_trace: Optional[list] = None