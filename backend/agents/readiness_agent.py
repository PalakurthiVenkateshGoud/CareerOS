from agents.base_agent import BaseAgent, AgentResult

class CareerReadinessAgent(BaseAgent):
    name = "readiness_agent"
    system_prompt = (
        "You are the Career Readiness Agent. Synthesize the candidate profile, "
        "skill gaps, strategy, and roadmap into a Current Readiness score (0-100) "
        "and a Learning Progress Projection at 3/6/12 months assuming the roadmap "
        "is followed at the given weekly hours. Provide a methodology explanation "
        "(what factors are weighted: skill coverage vs role blueprint, project "
        "portfolio strength, experience) and 'key_levers' — the top 2-3 actions "
        "that would most increase the score, each with a one-line 'why' explanation."
    )

    async def run(self, profile: dict, skill_gap: dict, strategy: dict, roadmap: dict, hours_per_week: int) -> AgentResult:
        schema = ('{"current_readiness": 0, "projection": {"3_months":0,"6_months":0,"12_months":0}, '
                  '"methodology": "", "key_levers": [{"action":"","why":""}]}')
        prompt = (f"Profile: {profile.get('summary','')}\nSkill gaps: {skill_gap}\n"
                  f"Strategy: {strategy}\nRoadmap: {roadmap}\nHours/week: {hours_per_week}")
        raw = await self.call_llm(prompt, schema)
        return AgentResult(
            agent_name=self.name,
            output={k: raw[k] for k in ["current_readiness","projection","methodology","key_levers"]},
            confidence=raw.get("confidence", 0.7),
            reasoning=raw.get("reasoning", ""),
            assumptions=raw.get("assumptions", []),
            missing_data=raw.get("missing_data", []),
        )

readiness_agent = CareerReadinessAgent()