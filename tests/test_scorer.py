"""
Unit tests for the Candidate Scoring and Skill Matching Engine (scorer.py).
"""

import unittest
from scorer import (
    normalize_skill,
    compute_skill_overlap,
    compute_skill_score,
    compute_experience_score,
    compute_education_score,
    calculate_match_score,
)


class TestScorer(unittest.TestCase):
    """Test suite for candidate matching and scoring calculations."""

    def test_normalize_skill(self):
        """Verify skill normalization trims whitespace and lowercases."""
        self.assertEqual(normalize_skill(" Python "), "python")
        self.assertEqual(normalize_skill("React.JS"), "react.js")
        self.assertEqual(normalize_skill("Docker"), "docker")

    def test_compute_skill_overlap(self):
        """Verify skill categorization into matched, missing required, and missing preferred."""
        resume_skills = ["Python", "Docker", "Git", "FastAPI"]
        required_skills = ["Python", "Kubernetes", "Docker"]
        preferred_skills = ["FastAPI", "AWS"]

        overlap = compute_skill_overlap(resume_skills, required_skills, preferred_skills)

        self.assertIn("python", overlap["matched"])
        self.assertIn("docker", overlap["matched"])
        self.assertIn("fastapi", overlap["matched"])
        self.assertEqual(overlap["missing_required"], ["kubernetes"])
        self.assertEqual(overlap["missing_preferred"], ["aws"])

    def test_compute_skill_score_full_match(self):
        """Verify 100% skill score when all required skills are present."""
        required = {"python", "sql"}
        matched = {"python", "sql", "docker"}
        score = compute_skill_score(required, matched)
        self.assertEqual(score, 100.0)

    def test_compute_skill_score_partial_match(self):
        """Verify 50% skill score when half of required skills are present."""
        required = {"python", "kubernetes"}
        matched = {"python"}
        score = compute_skill_score(required, matched)
        self.assertEqual(score, 50.0)

    def test_compute_experience_score(self):
        """Verify experience score caps at 100% and calculates ratios correctly."""
        # 3 years out of 5 required -> 60%
        self.assertAlmostEqual(compute_experience_score(3, 5), 60.0)
        # 6 years out of 5 required -> 100% (capped)
        self.assertEqual(compute_experience_score(6, 5), 100.0)
        # 0 required years -> 100%
        self.assertEqual(compute_experience_score(2, 0), 100.0)

    def test_compute_education_score(self):
        """Verify education score matching against degree requirements."""
        education = [
            {"degree": "Bachelor of Science in Computer Science", "institution": "Tech University", "year": "2023"}
        ]
        # Matching keyword
        self.assertEqual(compute_education_score(education, "Computer Science"), 100.0)
        # Non-matching keyword (fallback score)
        self.assertEqual(compute_education_score(education, "Master of Business Administration"), 50.0)
        # Empty requirement
        self.assertEqual(compute_education_score(education, ""), 100.0)

    def test_calculate_match_score_pipeline(self):
        """Verify complete scoring pipeline output structure and score bounds."""
        resume_data = {
            "skills": ["Python", "SQL", "Git"],
            "education": [{"degree": "B.Tech Computer Science", "institution": "MIT", "year": "2022"}],
            "experience": [{"title": "Software Engineer", "company": "Tech Corp", "duration": "2 years"}],
            "total_years_experience": 2,
        }
        jd_data = {
            "required_skills": ["Python", "SQL"],
            "preferred_skills": ["Docker"],
            "required_experience_years": 2,
            "education_requirement": "Computer Science",
            "key_responsibilities": ["Develop REST APIs", "Manage databases"],
        }
        resume_text = "Software Engineer with Python and SQL experience. B.Tech in Computer Science."
        jd_text = "Looking for a Software Engineer with Python, SQL, and Docker. Degree in Computer Science."

        result = calculate_match_score(resume_data, jd_data, resume_text, jd_text)

        self.assertIn("final_score", result)
        self.assertIn("breakdown", result)
        self.assertIn("skill_gap", result)

        self.assertGreaterEqual(result["final_score"], 0.0)
        self.assertLessEqual(result["final_score"], 100.0)
        self.assertEqual(result["breakdown"]["skill_match"], 100.0)
        self.assertEqual(result["breakdown"]["experience_match"], 100.0)
        self.assertEqual(result["breakdown"]["education_match"], 100.0)


if __name__ == "__main__":
    unittest.main()
