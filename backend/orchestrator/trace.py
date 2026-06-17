from schemas.models import AgentResult, TraceStep


def log_step(agent_name: str, result: AgentResult) -> dict:
    """
    Convert an AgentResult into a TraceStep dict for the reasoning trace
    shown in AgentTraceViewer on the frontend.
    """
    summary = _build_summary(agent_name, result.output)

    step = TraceStep(
        agent=agent_name,
        summary=summary,
        confidence=result.confidence,
        reasoning=result.reasoning,
        assumptions=result.assumptions,
        missing_data=result.missing_data,
    )
    return step.model_dump()


def _build_summary(agent_name: str, output: dict) -> str:
    """Produce a short human-readable summary per agent type."""
    summaries = {
        "resume_agent": lambda o: f"Extracted {len(o.get('skills', {}).get('technical', []))} technical skills, "
                                   f"{len(o.get('projects', []))} projects.",
        "role_research_agent": lambda o: f"Built role blueprint with "
                                          f"{len(o.get('role_blueprint', {}).get('core', []))} core skills.",
        "skill_gap_agent": lambda o: f"Identified {len(o.get('gaps', []))} skill gaps, "
                                     f"{len(o.get('matched_skills', []))} matched skills.",
        "career_twin_agent": lambda o: f"Generated Career Twin with "
                                       f"{len(o.get('future_you', []))} future skills.",
        "strategy_agent": lambda o: f"Defined {len(o.get('milestones', []))} strategic milestones.",
        "roadmap_agent": lambda o: f"Created roadmap spanning "
                                   f"{o.get('estimated_completion_weeks', '?')} weeks.",
        "project_agent": lambda o: f"Recommended {len(o.get('projects', []))} portfolio projects.",
        "interview_agent": lambda o: f"Generated "
            f"{len(o.get('hr_questions', [])) + len(o.get('technical_questions', [])) + len(o.get('project_questions', []))} "
            f"interview questions.",
        "readiness_agent": lambda o: f"Current readiness: {o.get('current_readiness', '?')}%, "
                                     f"12-month projection: {o.get('projection', {}).get('12_months', '?')}%.",
    }

    builder = summaries.get(agent_name)
    if builder:
        try:
            return builder(output)
        except Exception:
            return f"{agent_name} completed."
    return f"{agent_name} completed."