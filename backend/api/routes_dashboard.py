from fastapi import APIRouter
from pydantic import BaseModel
from orchestrator.orchestrator import run_career_pipeline
from db.database import get_session_data, save_dashboard

router = APIRouter()

class ConfigureRequest(BaseModel):
    session_id: str
    target_role: str
    hours_per_week: int

@router.post("/career/analyze")
async def analyze(req: ConfigureRequest):
    profile = get_session_data(req.session_id)["parsed_profile"]
    result = await run_career_pipeline(
        req.session_id, profile, req.target_role, req.hours_per_week
    )
    save_dashboard(req.session_id, result)
    return result

@router.get("/career/dashboard/{session_id}")
async def get_dashboard(session_id: str):
    return get_session_data(session_id).get("dashboard")