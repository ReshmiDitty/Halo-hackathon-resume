"""
SQLite Database Module for Candidate Management & Pipeline Tracking.

Manages persistent candidate records, match scoring history, skill gaps,
and interview assessment metrics for the HALO Recruitment Dashboard.
"""

import json
import sqlite3
import os
from typing import Any, Dict, List, Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "candidates.db")

DEMO_CANDIDATES = [
    {
        "name": "John Doe",
        "role": "Senior Full Stack Engineer",
        "match_score": 88.5,
        "skill_match": 92.0,
        "experience_match": 100.0,
        "education_match": 100.0,
        "semantic_similarity": 82.0,
        "missing_skills": ["Kubernetes", "GraphQL"],
        "assessment_score": 85.0,
        "status": "Assessed",
        "experience_years": 6.5,
        "education": "B.S. Computer Science"
    },
    {
        "name": "Sarah Jenkins",
        "role": "Lead Backend Developer",
        "match_score": 84.2,
        "skill_match": 85.0,
        "experience_match": 90.0,
        "education_match": 100.0,
        "semantic_similarity": 78.0,
        "missing_skills": ["Kubernetes", "CI/CD"],
        "assessment_score": 78.0,
        "status": "Assessed",
        "experience_years": 5.0,
        "education": "M.S. Software Engineering"
    },
    {
        "name": "Alex Rivera",
        "role": "DevOps / Platform Engineer",
        "match_score": 81.0,
        "skill_match": 80.0,
        "experience_match": 85.0,
        "education_match": 100.0,
        "semantic_similarity": 75.0,
        "missing_skills": ["Power BI", "Tableau"],
        "assessment_score": 92.0,
        "status": "Assessed",
        "experience_years": 4.5,
        "education": "B.Tech Information Technology"
    },
    {
        "name": "Emily Zhang",
        "role": "Frontend React Specialist",
        "match_score": 82.5,
        "skill_match": 88.0,
        "experience_match": 80.0,
        "education_match": 100.0,
        "semantic_similarity": 74.0,
        "missing_skills": ["Kubernetes", "C", "CI/CD"],
        "assessment_score": 0.0,
        "status": "Screened",
        "experience_years": 4.0,
        "education": "B.S. Computer Science"
    },
    {
        "name": "Michael Chang",
        "role": "Data Engineer / Python Dev",
        "match_score": 80.0,
        "skill_match": 78.0,
        "experience_match": 85.0,
        "education_match": 100.0,
        "semantic_similarity": 80.0,
        "missing_skills": ["Power BI", "Kubernetes", "CI/CD"],
        "assessment_score": 68.0,
        "status": "Assessed",
        "experience_years": 5.0,
        "education": "B.S. Mathematics & Computing"
    },
    {
        "name": "Priya Sharma",
        "role": "Full Stack Developer",
        "match_score": 83.0,
        "skill_match": 86.0,
        "experience_match": 80.0,
        "education_match": 100.0,
        "semantic_similarity": 79.0,
        "missing_skills": ["Kubernetes", "Tableau"],
        "assessment_score": 72.0,
        "status": "Assessed",
        "experience_years": 4.0,
        "education": "B.E. Computer Engineering"
    },
    {
        "name": "David Kim",
        "role": "Cloud Architect",
        "match_score": 79.5,
        "skill_match": 76.0,
        "experience_match": 90.0,
        "education_match": 100.0,
        "semantic_similarity": 76.0,
        "missing_skills": ["Power BI", "C"],
        "assessment_score": 0.0,
        "status": "Screened",
        "experience_years": 6.0,
        "education": "B.S. Computer Science"
    },
    {
        "name": "Jessica Taylor",
        "role": "Backend Engineer",
        "match_score": 78.0,
        "skill_match": 75.0,
        "experience_match": 85.0,
        "education_match": 100.0,
        "semantic_similarity": 72.0,
        "missing_skills": ["Kubernetes", "CI/CD", "Power BI"],
        "assessment_score": 0.0,
        "status": "Screened",
        "experience_years": 3.5,
        "education": "B.S. Software Engineering"
    },
    {
        "name": "Carlos Gomez",
        "role": "UI/UX Software Engineer",
        "match_score": 76.5,
        "skill_match": 72.0,
        "experience_match": 80.0,
        "education_match": 100.0,
        "semantic_similarity": 75.0,
        "missing_skills": ["Kubernetes", "Tableau", "C"],
        "assessment_score": 0.0,
        "status": "Screened",
        "experience_years": 3.0,
        "education": "B.A. Interactive Media"
    },
    {
        "name": "Amina Al-Mansoor",
        "role": "AI / ML Systems Engineer",
        "match_score": 88.0,
        "skill_match": 90.0,
        "experience_match": 95.0,
        "education_match": 100.0,
        "semantic_similarity": 84.0,
        "missing_skills": ["Power BI"],
        "assessment_score": 0.0,
        "status": "Screened",
        "experience_years": 5.5,
        "education": "M.S. Artificial Intelligence"
    }
]


def get_db_connection() -> sqlite3.Connection:
    """Create and return a database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(force_seed: bool = False) -> None:
    """Initialize database tables and populate demo data if empty."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS candidates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                role TEXT NOT NULL,
                match_score REAL NOT NULL,
                skill_match REAL NOT NULL,
                experience_match REAL NOT NULL,
                education_match REAL NOT NULL,
                semantic_similarity REAL NOT NULL,
                missing_skills TEXT NOT NULL,
                assessment_score REAL DEFAULT 0.0,
                status TEXT DEFAULT 'Screened',
                experience_years REAL DEFAULT 0.0,
                education TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

        cursor.execute("SELECT COUNT(*) FROM candidates")
        count = cursor.fetchone()[0]
        if count == 0 or force_seed:
            if force_seed:
                cursor.execute("DELETE FROM candidates")
            for c in DEMO_CANDIDATES:
                cursor.execute("""
                    INSERT INTO candidates (
                        name, role, match_score, skill_match, experience_match,
                        education_match, semantic_similarity, missing_skills,
                        assessment_score, status, experience_years, education
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    c["name"],
                    c["role"],
                    c["match_score"],
                    c["skill_match"],
                    c["experience_match"],
                    c["education_match"],
                    c["semantic_similarity"],
                    json.dumps(c["missing_skills"]),
                    c["assessment_score"],
                    c["status"],
                    c["experience_years"],
                    c["education"]
                ))
            conn.commit()


def get_all_candidates() -> List[Dict[str, Any]]:
    """Fetch all candidate records from the database."""
    init_db()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM candidates ORDER BY id DESC")
        rows = cursor.fetchall()
        result = []
        for r in rows:
            d = dict(r)
            try:
                d["missing_skills"] = json.loads(d["missing_skills"])
            except Exception:
                d["missing_skills"] = []
            result.append(d)
        return result


def add_candidate(
    name: str,
    role: str,
    match_score: float,
    skill_match: float,
    experience_match: float,
    education_match: float,
    semantic_similarity: float,
    missing_skills: List[str],
    experience_years: float = 0.0,
    education: str = "",
    status: str = "Screened",
    assessment_score: float = 0.0,
) -> int:
    """Insert a new analyzed candidate into the database."""
    init_db()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO candidates (
                name, role, match_score, skill_match, experience_match,
                education_match, semantic_similarity, missing_skills,
                assessment_score, status, experience_years, education
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            name,
            role,
            match_score,
            skill_match,
            experience_match,
            education_match,
            semantic_similarity,
            json.dumps(missing_skills),
            assessment_score,
            status,
            experience_years,
            education
        ))
        conn.commit()
        return cursor.lastrowid


def update_candidate_assessment(candidate_id: int, assessment_score: float, status: str = "Assessed") -> None:
    """Update assessment score for a candidate."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE candidates
            SET assessment_score = ?, status = ?
            WHERE id = ?
        """, (assessment_score, status, candidate_id))
        conn.commit()


def delete_candidate(candidate_id: int) -> None:
    """Delete candidate from database by ID."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM candidates WHERE id = ?", (candidate_id,))
        conn.commit()


def reset_database() -> None:
    """Reset database to initial demo state."""
    init_db(force_seed=True)
