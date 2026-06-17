import os
import json
import hashlib

from agents.resume_agent import resume_agent
from agents.role_research_agent import role_research_agent
from agents.skill_gap_agent import skill_gap_agent
from agents.career_twin_agent import career_twin_agent
from agents.strategy_agent import strategy_agent
from agents.roadmap_agent import roadmap_agent
from agents.project_agent import project_agent
from agents.interview_agent import interview_agent
from agents.readiness_agent import readiness_agent
from agents.base_agent import AgentResult
from orchestrator.trace import log_step

# Whole-pipeline cache, keyed by (profile, target_role, hours_per_week).
# Per-agent caching in base_agent.py can't reliably hit for downstream
# agents since their prompts include upstream LLM outputs that shift
# slightly between runs. Caching the full pipeline result means a repeated
# end-to-end test (same resume, same role, same hours) skips all 9 agents
# and every API call entirely, regardless of what any single agent returns.
_PIPELINE_CACHE_PATH = os.path.join(os.path.dirname(__file__), "..", ".pipeline_cache.json")


def _pipeline_cache_key(profile: dict, target_role: str, hours_per_week: int) -> str:
    raw = json.dumps(
        {"profile": profile, "target_role": target_role, "hours_per_week": hours_per_week},
        sort_keys=True,
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _load_pipeline_cache() -> dict:
    if os.path.exists(_PIPELINE_CACHE_PATH):
        try:
            with open(_PIPELINE_CACHE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def _save_pipeline_cache(cache: dict) -> None:
    try:
        with open(_PIPELINE_CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump(cache, f)
    except Exception as e:
        print(f"[orchestrator] Failed to write pipeline cache: {e}")


def _fallback(name: str, output: dict) -> AgentResult:
    """
    Used when an agent's call_llm exhausts every provider (Groq + Gemini +
    OpenRouter all rate-limited/timed-out simultaneously). Returns a clearly
    marked placeholder instead of letting the exception crash the whole
    pipeline — the dashboard renders with this one section degraded rather
    than a 500 for the entire request.
    """
    return AgentResult(
        agent_name=name,
        output=output,
        confidence=0.0,
        reasoning="All LLM providers were unavailable (free-tier quota exhausted) this run — showing placeholder content for this section.",
        assumptions=[],
        missing_data=["Live AI-generated content unavailable this run due to provider quota limits."],
    )


async def _run_with_fallback(name: str, coro, fallback_output: dict) -> AgentResult:
    try:
        return await coro
    except Exception as e:
        print(f"[orchestrator] {name} failed, using placeholder fallback: {e}")
        return _fallback(name, fallback_output)


async def run_career_pipeline(session_id: str, profile: dict, target_role: str, hours_per_week: int) -> dict:
    """
    Runs the full 9-agent CareerOS pipeline sequentially, passing context
    from each agent to the next. Returns the aggregated dashboard payload.
    """
    cache_key = _pipeline_cache_key(profile, target_role, hours_per_week)
    pipeline_cache = _load_pipeline_cache()
    if cache_key in pipeline_cache:
        print(f"[orchestrator] Pipeline cache hit for target_role={target_role} — skipping all 9 agents, zero API calls")
        cached_result = dict(pipeline_cache[cache_key])
        cached_result["session_id"] = session_id
        return cached_result

    trace = []

    # Step 1: Resume profile is already parsed (passed in), wrap for trace consistency
    # We re-run resume_agent only if profile wasn't pre-parsed; here we assume it was.
    resume_result_output = profile

    # Step 2: Role Research
    role_research = await _run_with_fallback(
        "role_research_agent",
        role_research_agent.run(target_role),
        {"role_blueprint": {"required_skills": [], "tools": [], "responsibilities": [], "hiring_signals": []}},
    )
    trace.append(log_step("role_research_agent", role_research))

    # Step 3: Skill Gap
    skill_gap = await _run_with_fallback(
        "skill_gap_agent",
        skill_gap_agent.run(resume_result_output, role_research.output["role_blueprint"], target_role),
        {"strengths": [], "missing_skills": [], "partial_skills": [], "priority_gaps": []},
    )
    trace.append(log_step("skill_gap_agent", skill_gap))

    # Step 4: Career Twin
    career_twin = await _run_with_fallback(
        "career_twin_agent",
        career_twin_agent.run(resume_result_output, skill_gap.output, target_role),
        {"current_you": [], "future_you": [], "transformation_highlights": []},
    )
    trace.append(log_step("career_twin_agent", career_twin))

    # Step 5: Strategy
    strategy = await _run_with_fallback(
        "strategy_agent",
        strategy_agent.run(resume_result_output, skill_gap.output, target_role, hours_per_week),
        {},
    )
    trace.append(log_step("strategy_agent", strategy))

    # Step 6: Roadmap
    roadmap = await _run_with_fallback(
        "roadmap_agent",
        roadmap_agent.run(skill_gap.output, strategy.output, hours_per_week),
        {},
    )
    trace.append(log_step("roadmap_agent", roadmap))

    # Step 7: Projects
    projects = await _run_with_fallback(
        "project_agent",
        project_agent.run(skill_gap.output, roadmap.output, target_role),
        {"projects": []},
    )
    trace.append(log_step("project_agent", projects))

    # Step 8: Interview Prep
    interview_prep = await _run_with_fallback(
        "interview_agent",
        interview_agent.run(resume_result_output, target_role, projects.output),
        {},
    )
    trace.append(log_step("interview_agent", interview_prep))

    # Step 9: Readiness
    readiness = await _run_with_fallback(
        "readiness_agent",
        readiness_agent.run(resume_result_output, skill_gap.output, strategy.output, roadmap.output, hours_per_week),
        {},
    )
    trace.append(log_step("readiness_agent", readiness))

    result = {
        "session_id": session_id,
        "profile_summary": resume_result_output,
        "role_blueprint": role_research.output["role_blueprint"],
        "readiness": readiness.output,
        "career_twin": career_twin.output,
        "skill_gap": skill_gap.output,
        "strategy": strategy.output,
        "roadmap": roadmap.output,
        "projects": projects.output.get("projects", []),
        "interview_prep": interview_prep.output,
        "agent_trace": trace,
    }

    used_fallback = any(
        r.confidence == 0.0
        for r in (role_research, skill_gap, career_twin, strategy, roadmap, projects, interview_prep, readiness)
    )

    if used_fallback:
        print("[orchestrator] One or more sections used a placeholder fallback — not caching this result")
    else:
        pipeline_cache[cache_key] = result
        _save_pipeline_cache(pipeline_cache)

    return result