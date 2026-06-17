"""
Central reference for shared prompt fragments.
Individual agents define their own system_prompt, but reuse these
fragments to keep output contracts consistent across the pipeline.
"""

COMMON_OUTPUT_CONTRACT = (
    "Always respond with ONLY valid JSON. Include 'confidence' (0-1), "
    "'reasoning' (a short explanation of your logic), 'assumptions' "
    "(a list of assumptions you made), and 'missing_data' (a list of "
    "information that would improve this output if available)."
)

EXPLANATION_INSTRUCTION = (
    "Every recommendation, gap, or suggestion must include an 'explanation' "
    "field describing the reasoning behind it in plain language. "
    "Do not invent statistics, percentages, or market data you cannot "
    "verify. Use qualitative phrasing such as "
    "'Commonly expected for {role} roles and absent from your profile.'"
)

SAFETY_INSTRUCTION = (
    "Do not hallucinate skills, experience, or facts not present in the "
    "input data. If information is insufficient, state this in "
    "'missing_data' rather than guessing."
)