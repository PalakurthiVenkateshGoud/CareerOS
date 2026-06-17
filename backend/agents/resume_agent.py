
from agents.base_agent import BaseAgent, AgentResult


class ResumeAgent(BaseAgent):
    name = "resume_agent"

    system_prompt = (
        "You are the Resume Intelligence Agent in CareerOS. "
        "Extract a structured profile: skills (categorized), projects, "
        "education, certifications, experience, and a 2-3 sentence summary. "
        "Do not fabricate skills not evidenced in the text. "
        "Always include all fields even if empty: skills, projects, education, "
        "certifications, experience, summary."
    )

    async def run(self, resume_text: str) -> AgentResult:
        schema = (
            '{"skills":{"technical":[],"soft":[]},'
            '"projects":[],'
            '"education":[],'
            '"certifications":[],'
            '"experience":[],'
            '"summary":""}'
        )

        raw = await self.call_llm(
            f"Resume text:\n{resume_text}",
            schema
        )

        assumptions = raw.get("assumptions", [])
        if isinstance(assumptions, str):
            assumptions = [assumptions]

        missing_data = raw.get("missing_data", [])
        if isinstance(missing_data, str):
            missing_data = [missing_data]

        output = {
            "skills": raw.get(
                "skills",
                {"technical": [], "soft": []}
            ),
            "projects": raw.get("projects", []),
            "education": raw.get("education", []),
            "certifications": raw.get("certifications", []),
            "experience": raw.get("experience", []),
            "summary": raw.get("summary", ""),
        }

        return AgentResult(
            agent_name=self.name,
            output=output,
            confidence=float(raw.get("confidence", 0.7)),
            reasoning=str(raw.get("reasoning", "")),
            assumptions=assumptions,
            missing_data=missing_data,
        )


resume_agent = ResumeAgent()

