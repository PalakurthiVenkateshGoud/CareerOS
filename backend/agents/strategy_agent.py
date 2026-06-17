from agents.base_agent import BaseAgent, AgentResult

class StrategyAgent(BaseAgent):
    name = "strategy_agent"
    system_prompt = (
        "You are the Career Strategy Agent. Given a profile, skill gaps, target role, "
        "and weekly time availability, design an optimal high-level strategic path: "
        "ordered milestones with estimated effort (weeks), and a short rationale for "
        "why this sequencing is optimal given the gaps and constraints."
    )

    async def run(self, profile: dict, skill_gap: dict, target_role: str, hours_per_week: int) -> AgentResult:
        schema = '{"milestones": [{"title": "", "effort_weeks": 0, "rationale": ""}], "overall_strategy_summary": ""}'
        prompt = (f"Target role: {target_role}\nHours/week available: {hours_per_week}\n"
                  f"Skill gaps: {skill_gap}\nProfile summary: {profile.get('summary','')}")
        raw = await self.call_llm(prompt, schema)
        return AgentResult(
            agent_name=self.name,
            output={k: raw[k] for k in ["milestones","overall_strategy_summary"]},
            confidence=raw.get("confidence", 0.7),
            reasoning=raw.get("reasoning", ""),
            assumptions=raw.get("assumptions", []),
            missing_data=raw.get("missing_data", []),
        )

strategy_agent = StrategyAgent()