"""
Candidate Scoring & Skill Matching Engine.

This module evaluates candidate fit against job requirements using a multi-factor
weighted algorithm:
1. Skill Match (50% weight): Exact & normalized overlap with required/preferred skills.
2. Experience Match (25% weight): Ratio of candidate years of experience to required years.
3. Education Match (15% weight): Degree and specialization relevance.
4. Semantic Similarity (10% weight): Dense vector cosine similarity via SentenceTransformer.
"""

from typing import Any, Dict, List, Optional, Set
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Global singleton cache for the embedding model
_model: Optional[SentenceTransformer] = None


def get_embedding_model() -> SentenceTransformer:
    """
    Retrieve or initialize the singleton SentenceTransformer embedding model.

    Returns:
        SentenceTransformer: Loaded 'all-MiniLM-L6-v2' model instance.
    """
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def normalize_skill(skill: str) -> str:
    """
    Normalize skill string for case-insensitive and whitespace-invariant comparison.

    Args:
        skill: Raw skill string (e.g., ' Python ', 'React.js').

    Returns:
        str: Normalized, lowercase, trimmed skill string.
    """
    return skill.strip().lower()


def compute_skill_overlap(
    resume_skills: List[str],
    required_skills: List[str],
    preferred_skills: Optional[List[str]] = None,
) -> Dict[str, List[str]]:
    """
    Calculate matched, missing required, and missing preferred skills.

    Args:
        resume_skills: List of skills extracted from candidate resume.
        required_skills: List of mandatory skills from job description.
        preferred_skills: List of optional/bonus skills from job description.

    Returns:
        Dict[str, List[str]]: Dictionary with 'matched', 'missing_required',
                             and 'missing_preferred' skill lists.
    """
    if preferred_skills is None:
        preferred_skills = []

    resume_set: Set[str] = {normalize_skill(s) for s in resume_skills if s.strip()}
    required_set: Set[str] = {normalize_skill(s) for s in required_skills if s.strip()}
    preferred_set: Set[str] = {normalize_skill(s) for s in preferred_skills if s.strip()}

    matched = resume_set & (required_set | preferred_set)
    missing_required = required_set - resume_set
    missing_preferred = preferred_set - resume_set

    return {
        "matched": sorted(matched),
        "missing_required": sorted(missing_required),
        "missing_preferred": sorted(missing_preferred),
    }


def compute_skill_score(required_set: Set[str], matched_set: Set[str]) -> float:
    """
    Calculate percentage match for required skills.

    Args:
        required_set: Set of normalized required skills.
        matched_set: Set of normalized candidate matched skills.

    Returns:
        float: Score between 0.0 and 100.0.
    """
    if not required_set:
        return 100.0
    matched_required = matched_set & required_set
    return (len(matched_required) / len(required_set)) * 100.0


def compute_experience_score(resume_years: float, required_years: float) -> float:
    """
    Calculate experience match score based on candidate years vs required years.

    Args:
        resume_years: Total years of professional experience from resume.
        required_years: Minimum years of experience required by job description.

    Returns:
        float: Score between 0.0 and 100.0 (capped at 100.0).
    """
    try:
        r_years = float(resume_years)
    except (ValueError, TypeError):
        r_years = 0.0

    try:
        req_years = float(required_years)
    except (ValueError, TypeError):
        req_years = 0.0

    if req_years <= 0:
        return 100.0

    ratio = r_years / req_years
    return min(ratio, 1.0) * 100.0


def compute_education_score(
    resume_education: List[Dict[str, str]],
    jd_requirement: str,
) -> float:
    """
    Calculate education match score based on degree alignment.

    Args:
        resume_education: List of education objects with 'degree', 'institution', 'year'.
        jd_requirement: Education requirements text from job description.

    Returns:
        float: Score between 0.0 and 100.0.
    """
    if not jd_requirement or not jd_requirement.strip():
        return 100.0

    if not resume_education:
        return 40.0

    jd_req_lower = jd_requirement.lower()
    for edu in resume_education:
        degree = edu.get("degree", "").lower()
        if degree and (degree in jd_req_lower or jd_req_lower in degree):
            return 100.0

    # Baseline partial credit for having degree entries even if exact title mismatch
    return 50.0


def compute_semantic_similarity(resume_text: str, jd_text: str) -> float:
    """
    Compute dense vector cosine similarity between resume and job description texts.

    Args:
        resume_text: Raw plain text of candidate resume.
        jd_text: Raw plain text of job description.

    Returns:
        float: Similarity percentage score between 0.0 and 100.0.
    """
    if not resume_text.strip() or not jd_text.strip():
        return 0.0

    model = get_embedding_model()
    embeddings = model.encode([resume_text[:3000], jd_text[:3000]])
    sim = float(cosine_similarity([embeddings[0]], [embeddings[1]])[0][0])
    return max(sim, 0.0) * 100.0


def calculate_match_score(
    resume_data: Dict[str, Any],
    jd_data: Dict[str, Any],
    resume_text: str,
    jd_text: str,
) -> Dict[str, Any]:
    """
    Execute full candidate scoring pipeline combining skill, experience,
    education, and semantic similarity factors.

    Weights:
        - Skills Match: 50%
        - Experience Match: 25%
        - Education Match: 15%
        - Semantic Similarity: 10%

    Args:
        resume_data: Extracted structured resume dictionary.
        jd_data: Extracted structured JD dictionary.
        resume_text: Raw resume text for embedding similarity.
        jd_text: Raw JD text for embedding similarity.

    Returns:
        Dict[str, Any]: Contains 'final_score', 'breakdown', and 'skill_gap'.
    """
    resume_skills = resume_data.get("skills", [])
    required_skills = jd_data.get("required_skills", [])
    preferred_skills = jd_data.get("preferred_skills", [])

    overlap = compute_skill_overlap(resume_skills, required_skills, preferred_skills)
    matched_set = set(overlap["matched"])
    required_set = {normalize_skill(s) for s in required_skills if s.strip()}

    skill_score = compute_skill_score(required_set, matched_set)
    exp_score = compute_experience_score(
        resume_data.get("total_years_experience", 0),
        jd_data.get("required_experience_years", 0),
    )
    edu_score = compute_education_score(
        resume_data.get("education", []),
        jd_data.get("education_requirement", ""),
    )
    semantic_score = compute_semantic_similarity(resume_text, jd_text)

    # Weighted calculation
    final_score = (
        skill_score * 0.50
        + exp_score * 0.25
        + edu_score * 0.15
        + semantic_score * 0.10
    )

    return {
        "final_score": float(round(final_score, 1)),
        "breakdown": {
            "skill_match": round(skill_score, 1),
            "experience_match": round(exp_score, 1),
            "education_match": round(edu_score, 1),
            "semantic_similarity": round(semantic_score, 1),
        },
        "skill_gap": overlap,
    }