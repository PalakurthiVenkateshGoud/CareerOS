from agents.base_agent import BaseAgent, AgentResult


class SkillGapAgent(BaseAgent):
    name = "skill_gap_agent"

    system_prompt = (
        "You are the Skill Gap Analysis Agent. "
        "Compare the candidate profile against the target role blueprint. "
        "Identify strengths, missing skills, partially developed skills, "
        "and rank gaps by importance."
    )

    async def run(
        self,
        profile: dict,
        role_blueprint: dict,
        target_role: str,
    ) -> AgentResult:

        # Field names below MUST match what SkillGapChart.tsx reads:
        # strengths / missing_skills / partial_skills are plain skill-name
        # strings, and each priority_gaps item needs skill / importance / description.
        schema = """
        {
          "strengths": ["Example matched skill the candidate already has"],
          "missing_skills": ["Example missing skill name"],
          "partial_skills": ["Example partially developed skill name"],
          "priority_gaps": [
            {"skill": "Example skill name", "importance": 7, "description": "Why this matters and what to do about it"}
          ]
        }
        """

        prompt = (
            f"Target Role: {target_role}\n\n"
            f"Profile:\n{profile}\n\n"
            f"Role Blueprint:\n{role_blueprint}\n\n"
            "The example values above are placeholders showing the required "
            "shape only. Replace every placeholder with real, specific "
            "skill names based on the actual profile and role blueprint "
            "given. Never echo back the literal placeholder text.\n"
            "strengths, missing_skills, and partial_skills must be plain "
            "skill-name strings (not objects).\n"
            "priority_gaps is the most important field — it drives the "
            "dashboard's main skill gap display. Return 2 to 6 "
            "priority_gaps no matter what; this list must never be left "
            "empty even if strengths/missing_skills/partial_skills are "
            "thin. Every priority_gaps item MUST include a non-empty "
            "'skill', an 'importance' integer from 1 to 10, and a "
            "non-empty 'description' — never omit any of these three "
            "fields."
        )

        raw = await self.call_llm(
            prompt,
            schema,
            validate=self._has_real_content,
        )

        assumptions = raw.get("assumptions", [])
        if isinstance(assumptions, str):
            assumptions = [assumptions]

        missing_data = raw.get("missing_data", [])
        if isinstance(missing_data, str):
            missing_data = [missing_data]

        output = {
            "strengths": raw.get("strengths", []),
            "missing_skills": raw.get("missing_skills", []),
            "partial_skills": raw.get("partial_skills", []),
            "priority_gaps": raw.get("priority_gaps", []),
        }

        return AgentResult(
            agent_name=self.name,
            output=output,
            confidence=float(raw.get("confidence", 0.7)),
            reasoning=str(raw.get("reasoning", "")),
            assumptions=assumptions,
            missing_data=missing_data,
        )

    @staticmethod
    def _has_real_content(result: dict) -> bool:
        """
        priority_gaps is what SkillGapChart.tsx actually renders as the main
        gap display — a result where only strengths/partial_skills has
        content but priority_gaps is empty must be rejected, not accepted
        just because "some" field was non-empty.
        """
        priority_gaps = result.get("priority_gaps", [])
        if not priority_gaps:
            return False

        for gap in priority_gaps:
            if not isinstance(gap, dict):
                return False
            skill = gap.get("skill")
            if not skill or SkillGapAgent._looks_like_placeholder(skill):
                return False
            if gap.get("importance") is None:
                return False

        # A real analysis almost always finds either some matched skills or
        # some genuinely missing ones (or both) — both being empty alongside
        # a non-empty priority_gaps is a sign of a thin/lazy response.
        if not result.get("strengths") and not result.get("missing_skills"):
            return False

        return True


skill_gap_agent = SkillGapAgent()