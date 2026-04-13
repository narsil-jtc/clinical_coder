"""
Prompt templates for the explanation generation step.

Explanations are written for the human coder who will review each code suggestion.
They must be concise, reference the exact documentation, and explain why this code
was chosen over alternatives.
"""

EXPLANATION_SYSTEM = """\
You are explaining clinical coding decisions to a human clinical coder who will \
review and accept or reject each suggested code.

For each code in the provided list, write a brief explanation that:
1. States what condition or procedure the code represents in plain English
2. Identifies the specific text in the clinical note that drives this code choice
3. Explains briefly why the alternatives were not selected (when alternatives exist)

Keep each explanation under 60 words. Use the same clinical terminology the \
clinician used in the note — do not introduce new jargon.

Return ONLY valid JSON matching this exact schema — no prose, no markdown fences:

{
  "explanations": [
    {
      "code": "<the ICD-10 code>",
      "plain_english": "<plain explanation, ≤ 60 words>",
      "key_documentation": "<the specific phrase or sentence in the note that supports this code>",
      "why_not_alternatives": "<brief reason alternatives were not chosen, or empty string if no alternatives>"
    }
  ]
}
"""


def build_explanation_user_prompt(
    code_candidates_json: str,
    note_excerpt: str,
) -> str:
    """
    Build the user-turn prompt for explanation generation.

    Args:
        code_candidates_json: JSON string of code candidates to explain.
        note_excerpt: The relevant portion of the clinical note (assessment + plan sections).
    """
    return f"""\
CLINICAL NOTE EXCERPT:
---
{note_excerpt}
---

CODE CANDIDATES TO EXPLAIN:
{code_candidates_json}

Write an explanation for each code. Return ONLY valid JSON. No additional text.\
"""
