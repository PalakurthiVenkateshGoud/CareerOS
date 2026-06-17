from agents.base_agent import BaseAgent, AgentResult

class RoadmapAgent(BaseAgent):
    name = "roadmap_agent"
    system_prompt = (
        "You are the Learning Roadmap Agent. Convert skill gaps and strategy milestones "
        "into a concrete week-by-week learning plan (group into months if duration > 8 weeks). "
        "For each item include topic, recommended resource type (course/docs/practice), "
        "estimated hours, and which skill gap it addresses."
    )

    async def run(self, skill_gap: dict, strategy: dict, hours_per_week: int) -> AgentResult:
        schema = '{"timeline": [{"period": "", "focus_skills": [], "tasks": [{"title":"","resource_type":"","hours":0}]}], "estimated_completion_weeks": 0}'
        prompt = f"Hours/week: {hours_per_week}\nSkill gaps: {skill_gap}\nStrategy: {strategy}"

        raw = await self.call_llm(prompt, schema)
        

        return AgentResult(
            agent_name=self.name,
            output={
                "timeline": raw.get("timeline", []),
                "estimated_completion_weeks": raw.get(
                    "estimated_completion_weeks",
                    12
                ),
            },
            confidence=raw.get("confidence", 0.7),
            reasoning=raw.get("reasoning", ""),
            assumptions=raw.get("assumptions", []),
            missing_data=raw.get("missing_data", []),
        )

roadmap_agent = RoadmapAgent()