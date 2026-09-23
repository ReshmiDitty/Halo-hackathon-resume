"""
AI Mock Interview Question Generator Module.

This module generates tailored interview questions based on candidate background,
identified skill gaps, and job responsibilities using Groq LLM inference.
"""

import json
import re
from typing import Any, Dict, List
from extractor import get_groq_client, DEFAULT_MODEL

QUESTION_PROMPT: str = """Based on this candidate's resume and the job description below, generate 5 targeted mock interview questions.

Question Distribution:
- 2-3 Technical Questions (targeting missing required skills or deep-diving into matched core skills).
- 1-2 Behavioral Questions (evaluating past projects, collaboration, or leadership).
- 1 Role-Fit Question (evaluating alignment with key job responsibilities and company objectives).

Return ONLY valid JSON (no markdown formatting, no code fences) as a list of objects:
[
  {{
    "question": "The interview question text",
    "type": "technical" | "behavioral" | "role-fit",
    "tests": "Brief one-line explanation of what capability or trait this question evaluates"
  }}
]

Candidate Experience Summary:
{resume_summary}

Identified Skill Gaps (Missing Skills):
{missing_skills}

Job Responsibilities:
{responsibilities}
"""


def generate_mock_questions(
    resume_data: Dict[str, Any],
    jd_data: Dict[str, Any],
    missing_skills: List[str],
    model: str = DEFAULT_MODEL,
) -> List[Dict[str, str]]:
    """
    Generate targeted interview questions based on candidate data and skill gaps.

    Args:
        resume_data: Structured resume dictionary containing experience and skills.
        jd_data: Structured job description dictionary with responsibilities.
        missing_skills: List of skills missing from candidate profile.
        model: Target Groq LLM model name.

    Returns:
        List[Dict[str, str]]: List of question dictionaries with 'question',
                             'type', and 'tests' fields.
    """
    resume_summary = json.dumps(resume_data.get("experience", []))[:2000]
    missing_str = ", ".join(missing_skills) if missing_skills else "None (Candidate matches all required skills)"
    resp_str = ", ".join(jd_data.get("key_responsibilities", []))[:1000] or "General engineering responsibilities"

    prompt = QUESTION_PROMPT.format(
        resume_summary=resume_summary,
        missing_skills=missing_str,
        responsibilities=resp_str,
    )

    try:
        client = get_groq_client()
        response = client.chat.completions.create(
            model=model,
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        raw_text = response.choices[0].message.content or ""
        cleaned_text = raw_text.strip()
        if cleaned_text.startswith("```"):
            cleaned_text = re.sub(r"^```(?:json)?\s*", "", cleaned_text, flags=re.IGNORECASE)
            cleaned_text = re.sub(r"\s*```$", "", cleaned_text)

        parsed = json.loads(cleaned_text.strip())
        if isinstance(parsed, list):
            return parsed
        return [{"question": "Failed to parse question list format.", "type": "error", "tests": ""}]
    except Exception as exc:
        return [
            {
                "question": f"Could not generate questions due to an error: {str(exc)}",
                "type": "error",
                "tests": "Please check your Groq API key and network connection.",
            }
        ]