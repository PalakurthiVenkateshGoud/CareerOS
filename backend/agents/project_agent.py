from agents.base_agent import BaseAgent, AgentResult

class ProjectAgent(BaseAgent):
    name = "project_agent"
    system_prompt = (
        "You are the Project Recommendation Agent. Suggest 3-5 portfolio projects "
        "tailored to the target role and skill gaps, ranked by resume/interview impact. "
        "Each project: title, description, skills_demonstrated, difficulty, "
        "estimated_hours, and relevance_explanation tying it to the skill gaps and roadmap."
    )

    async def run(self, skill_gap: dict, roadmap: dict, target_role: str) -> AgentResult:
        schema = '{"projects": [{"title":"","description":"","skills_demonstrated":[],"difficulty":"","estimated_hours":0,"relevance_explanation":"","impact_rank":0}]}'
        prompt = f"Target role: {target_role}\nSkill gaps: {skill_gap}\nRoadmap: {roadmap}"
        raw = await self.call_llm(prompt, schema)
        return AgentResult(
            agent_name=self.name,
            output={"projects": raw["projects"]},
            confidence=raw.get("confidence", 0.7),
            reasoning=raw.get("reasoning", ""),
            assumptions=raw.get("assumptions", []),
            missing_data=raw.get("missing_data", []),
        )

project_agent = ProjectAgent()