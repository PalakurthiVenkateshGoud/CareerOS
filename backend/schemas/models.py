from pydantic import BaseModel
from typing import Optional

class AgentResult(BaseModel):
    """Standard output contract every agent returns."""
    agent_name: str
    output: dict
    confidence: float
    reasoning: str
    assumptions: list[str] = []
    missing_data: list[str] = []


class TraceStep(BaseModel):
    agent: str
    summary: str
    confidence: float
    reasoning: str
    assumptions: list[str] = []
    missing_data: list[str] = []