from agents.base_agent import BaseAgent, AgentResult


class CareerTwinAgent(BaseAgent):
    name = "career_twin_agent"

    system_prompt = (
        "You are the Career Twin Agent. Create a Current You vs Future You comparison."
    )

    async def run(
        self,
        profile: dict,
        skill_gap: dict,
        target_role: str,
    ) -> AgentResult:

        # Field names below MUST match what CareerTwin.tsx reads:
        # current_you[0].title / .description, future_you[0].title / .description,
        # and each transformation_highlights item needs skill / status / description / importance.
        schema = (
            '{'
            '"current_you":[{"title":"Example current-state title","description":"One sentence describing the candidate now"}],'
            '"future_you":[{"title":"Example future-state title","description":"One sentence describing the candidate once role-ready"}],'
            '"transformation_highlights":[{'
            '"skill":"Example skill or theme name",'
            '"status":"Example short status label such as Priority Gap, Strength, or Future Focus",'
            '"description":"One sentence describing this specific transformation",'
            '"importance":8'
            '}]'
            '}'
        )

        prompt = (
            f"Target role: {target_role}\n"
            f"Profile skills: {profile.get('skills', {})}\n"
            f"Skill gaps: {skill_gap}\n\n"
            "The example values above are placeholders showing the required "
            "shape only. Replace every placeholder with real, specific "
            "content based on the actual profile, skill gaps, and target "
            "role given.\n"
            "Return exactly 1 item in current_you and exactly 1 item in "
            "future_you, each with a non-empty 'title' and a non-empty "
            "'description'.\n"
            "Return 3 to 6 transformation_highlights. Every highlight MUST "
            "include a non-empty 'skill', a non-empty 'status', a non-empty "
            "'description', and an 'importance' integer from 1 to 10 — "
            "never omit any of these four fields and never leave "
            "'importance' blank or null."
        )

        raw = await self.call_llm(
            prompt,
            schema,
            validate=self._has_real_content,
        )

        assumptions = raw.get("assumptions", [])
        missing_data = raw.get("missing_data", [])

        if isinstance(assumptions, str):
            assumptions = [assumptions]

        if isinstance(missing_data, str):
            missing_data = [missing_data]

        return AgentResult(
            agent_name=self.name,
            output={
                "current_you": raw.get("current_you", []),
                "future_you": raw.get("future_you", []),
                "transformation_highlights": raw.get(
                    "transformation_highlights",
                    []
                ),
            },
            confidence=float(raw.get("confidence", 0.7)),
            reasoning=str(raw.get("reasoning", "")),
            assumptions=assumptions,
            missing_data=missing_data,
        )

    @staticmethod
    def _has_real_content(result: dict) -> bool:
        """Reject a well-formed but empty/blank career twin result, and
        reject any result that just echoed the schema's placeholder text
        back instead of replacing it with real content."""
        current = result.get("current_you", [])
        future = result.get("future_you", [])
        highlights = result.get("transformation_highlights", [])

        if not current or not isinstance(current[0], dict) or not current[0].get("description"):
            return False
        if CareerTwinAgent._looks_like_placeholder(current[0].get("title")):
            return False
        if CareerTwinAgent._looks_like_placeholder(current[0].get("description")):
            return False

        if not future or not isinstance(future[0], dict) or not future[0].get("description"):
            return False
        if CareerTwinAgent._looks_like_placeholder(future[0].get("title")):
            return False
        if CareerTwinAgent._looks_like_placeholder(future[0].get("description")):
            return False

        if not highlights:
            return False

        for item in highlights:
            if not isinstance(item, dict):
                return False
            if not item.get("skill") or not item.get("description"):
                return False
            if CareerTwinAgent._looks_like_placeholder(item.get("skill")):
                return False
            if CareerTwinAgent._looks_like_placeholder(item.get("description")):
                return False
            if item.get("importance") is None:
                return False

        return True


career_twin_agent = CareerTwinAgent()