from agents.base_agent import BaseAgent, AgentResult

class PredictorAgent(BaseAgent):
    name = "predictor_agent"
    system_prompt = (
        "You are the Career Success Predictor Agent. Synthesize the candidate profile, "
        "skill gaps, strategy, and roadmap into a Career Readiness Score (0-100) for the "
        "current state, and projected scores at 3/6/12 months assuming the roadmap is followed "
        "at the given weekly hours. Provide a clear explanation of the scoring methodology "
        "(e.g. weight given to skill coverage, project portfolio, experience) and what would "
        "most increase the score."
    )

    async def run(self, profile: dict, skill_gap: dict, strategy: dict, roadmap: dict, hours_per_week: int) -> AgentResult:
        schema = ('{"current_readiness": 0, "projected": {"3_months":0,"6_months":0,"12_months":0}, '
                  '"explanation": "", "key_levers": []}')
        prompt = (f"Profile: {profile.get('summary','')}\nSkill gaps: {skill_gap}\n"
                  f"Strategy: {strategy}\nRoadmap: {roadmap}\nHours/week: {hours_per_week}")
        raw = await self.call_llm(prompt, schema)
        return AgentResult(
            agent_name=self.name,
            output={k: raw[k] for k in ["current_readiness","projected","explanation","key_levers"]},
            confidence=raw.get("confidence", 0.7),
            reasoning=raw.get("reasoning", ""),
            assumptions=raw.get("assumptions", []),
            missing_data=raw.get("missing_data", []),
        )

predictor_agent = PredictorAgent()