from agents.base_agent import BaseAgent, AgentResult


class RoleResearchAgent(BaseAgent):
    name = "role_research_agent"

    system_prompt = (
        "You are the Role Research Agent. "
        "Research the target role and produce a role blueprint containing "
        "required skills, tools, responsibilities, and hiring signals. "
        "Return structured JSON only."
    )

    async def run(self, target_role: str) -> AgentResult:

        # The arrays below are EXAMPLE placeholder values showing the
        # required shape only — they are not the expected answer. Using
        # empty arrays here caused weaker fallback models to literally
        # echo the empty structure back as a "valid" response.
        schema = """
        {
            "role_blueprint": {
                "required_skills": ["Example Skill A", "Example Skill B", "Example Skill C"],
                "tools": ["Example Tool A", "Example Tool B", "Example Tool C"],
                "responsibilities": ["Example responsibility A", "Example responsibility B"],
                "hiring_signals": ["Example hiring signal A", "Example hiring signal B"]
            }
        }
        """

        raw = await self.call_llm(
            f"""
            Target role: {target_role}

            Research this role and return:
            - 3 to 5 required_skills (real, specific skill names for this role)
            - 3 to 5 tools (real, specific tools/technologies used in this role)
            - 3 to 5 responsibilities (real, specific day-to-day duties)
            - 3 to 5 hiring_signals (real, specific things employers screen for)

            The example values in the schema are placeholders only.
            You must replace every placeholder with real, specific content
            for this exact role. NEVER return an empty array for any of the
            four lists — every role has skills, tools, responsibilities, and
            hiring signals, even if you must rely on general industry
            knowledge to infer them.

            Keep response concise.
            """,
            schema,
            validate=self._has_real_content,
        )

        assumptions = raw.get("assumptions", [])
        if isinstance(assumptions, str):
            assumptions = [assumptions]

        missing_data = raw.get("missing_data", [])
        if isinstance(missing_data, str):
            missing_data = [missing_data]

        return AgentResult(
            agent_name=self.name,
            output={
                "role_blueprint": raw.get(
                    "role_blueprint",
                    {
                        "required_skills": [],
                        "tools": [],
                        "responsibilities": [],
                        "hiring_signals": [],
                    },
                )
            },
            confidence=float(raw.get("confidence", 0.7)),
            reasoning=str(raw.get("reasoning", "")),
            assumptions=assumptions,
            missing_data=missing_data,
        )

    @staticmethod
    def _has_real_content(result: dict) -> bool:
        """Reject a well-formed but empty role blueprint, or one that just
        echoed the schema's placeholder text back."""
        blueprint = result.get("role_blueprint", {})
        if not isinstance(blueprint, dict):
            return False
        skills = blueprint.get("required_skills")
        if not skills:
            return False
        if any(RoleResearchAgent._looks_like_placeholder(s) for s in skills):
            return False
        return True


role_research_agent = RoleResearchAgent()