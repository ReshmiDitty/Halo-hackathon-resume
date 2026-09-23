"""
LLM-Powered Entity & Information Extraction Module.

This module leverages the Groq API to extract structured information (skills,
work experience, education, job requirements, responsibilities) from raw text
using prompt engineering and schema-enforced JSON parsing.
"""

import json
import os
import re
from typing import Any, Dict, Optional
import streamlit as st
from groq import Groq

# Default model configuration for Groq inference
DEFAULT_MODEL: str = "openai/gpt-oss-120b"

RESUME_SCHEMA_PROMPT: str = """You are an expert resume parsing AI. Extract structured data from the resume text below.

Return ONLY valid JSON (no markdown formatting, no code fences, no introductory or concluding text) matching this exact schema:
{{
  "skills": ["skill1", "skill2"],
  "education": [{{"degree": "Degree Title", "institution": "University / College", "year": "Graduation Year"}}],
  "experience": [{{"title": "Job Title", "company": "Company Name", "duration": "Years / Months", "description": "Short summary of responsibilities"}}],
  "total_years_experience": 0
}}

Resume text:
{text}
"""

JD_SCHEMA_PROMPT: str = """You are an expert job description parsing AI. Extract structured requirements from the job description below.

Return ONLY valid JSON (no markdown formatting, no code fences, no introductory or concluding text) matching this exact schema:
{{
  "required_skills": ["skill1", "skill2"],
  "preferred_skills": ["skill1", "skill2"],
  "required_experience_years": 0,
  "education_requirement": "Required Degree or Field of Study",
  "key_responsibilities": ["responsibility 1", "responsibility 2"]
}}

Job description text:
{text}
"""


def get_groq_api_key() -> Optional[str]:
    """
    Retrieve the Groq API key from Streamlit secrets or environment variables.

    Returns:
        Optional[str]: The API key string if found, otherwise None.
    """
    try:
        if "GROQ_API_KEY" in st.secrets:
            return st.secrets["GROQ_API_KEY"]
    except Exception:
        pass
    return os.environ.get("GROQ_API_KEY")


def get_groq_client() -> Groq:
    """
    Initialize and return a Groq client instance.

    Returns:
        Groq: Initialized Groq client.

    Raises:
        ValueError: If no GROQ_API_KEY is found in Streamlit secrets or environment.
    """
    api_key = get_groq_api_key()
    if not api_key or not api_key.strip():
        raise ValueError(
            "Groq API Key not found! Please set 'GROQ_API_KEY' in '.streamlit/secrets.toml' "
            "or as an environment variable."
        )
    return Groq(api_key=api_key.strip())


def _clean_json_response(raw_content: str) -> str:
    """
    Clean markdown code blocks and whitespace from LLM response to isolate JSON.

    Args:
        raw_content: Raw text string from the LLM.

    Returns:
        str: Sanitized JSON string.
    """
    cleaned = raw_content.strip()
    # Remove markdown code blocks if present
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    return cleaned.strip()


def _call_groq(prompt: str, model: str = DEFAULT_MODEL, max_tokens: int = 2000) -> Dict[str, Any]:
    """
    Send prompt to Groq API and parse response as a dictionary.

    Args:
        prompt: Formatted prompt string for the LLM.
        model: Target LLM model identifier on Groq.
        max_tokens: Maximum tokens in completion response.

    Returns:
        Dict[str, Any]: Parsed JSON data.

    Raises:
        ValueError: If JSON parsing fails or the LLM returns invalid output.
        RuntimeError: If Groq API request fails.
    """
    client = get_groq_client()
    try:
        response = client.chat.completions.create(
            model=model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
        )
        raw_text = response.choices[0].message.content or ""
        cleaned_text = _clean_json_response(raw_text)
        return json.loads(cleaned_text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Failed to parse LLM response into JSON:\n{raw_text[:400]}") from exc
    except Exception as exc:
        raise RuntimeError(f"Groq API call error: {str(exc)}") from exc


def extract_resume_data(resume_text: str) -> Dict[str, Any]:
    """
    Parse unstructured resume text into a structured dictionary.

    Args:
        resume_text: Raw plain text of the candidate's resume.

    Returns:
        Dict[str, Any]: Dictionary containing skills, education, experience,
                        and total_years_experience.
    """
    prompt = RESUME_SCHEMA_PROMPT.format(text=resume_text[:8000])
    return _call_groq(prompt)


def extract_jd_data(jd_text: str) -> Dict[str, Any]:
    """
    Parse unstructured job description text into a structured dictionary.

    Args:
        jd_text: Raw plain text of the job description.

    Returns:
        Dict[str, Any]: Dictionary containing required_skills, preferred_skills,
                        required_experience_years, education_requirement,
                        and key_responsibilities.
    """
    prompt = JD_SCHEMA_PROMPT.format(text=jd_text[:8000])
    return _call_groq(prompt)