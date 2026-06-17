from agents.base_agent import BaseAgent, AgentResult

class InterviewAgent(BaseAgent):
    name = "interview_agent"
    system_prompt = (
        "You are the Interview Coach Agent. Generate an interview preparation pack "
        "tailored to the target role, candidate profile, and recommended projects: "
        "HR/behavioral questions, technical/conceptual questions, and project-based "
        "questions (referencing the candidate's actual or recommended projects). "
        "For each question include a brief 'what_interviewer_is_assessing' note."
    )

    async def run(self, profile: dict, target_role: str, projects: dict) -> AgentResult:
        schema = ('{"hr_questions": [{"question":"","what_interviewer_is_assessing":""}], '
                  '"technical_questions": [{"question":"","what_interviewer_is_assessing":""}], '
                  '"project_questions": [{"question":"","what_interviewer_is_assessing":""}]}')
        prompt = f"Target role: {target_role}\nProfile summary: {profile.get('summary','')}\nProjects: {projects}"
        raw = await self.call_llm(prompt, schema)
        return AgentResult(
            agent_name=self.name,
            output={k: raw[k] for k in ["hr_questions","technical_questions","project_questions"]},
            confidence=raw.get("confidence", 0.7),
            reasoning=raw.get("reasoning", ""),
            assumptions=raw.get("assumptions", []),
            missing_data=raw.get("missing_data", []),
        )

interview_agent = InterviewAgent()