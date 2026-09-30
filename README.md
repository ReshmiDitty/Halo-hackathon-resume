Check out the website:  https://halo-hackathon-resume-lwkywr5eergsmpedgpbhcv.streamlit.app/

# 📄 HALO AI Resume Analyzer & Matcher

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-FF4B4B.svg)](https://streamlit.io/)
[![Groq AI](https://img.shields.io/badge/LLM-Groq%20Cloud-orange.svg)](https://groq.com/)
[![Sentence Transformers](https://img.shields.io/badge/Embeddings-all--MiniLM--L6--v2-green.svg)](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

An intelligent, full-stack recruitment intelligence platform that analyzes candidate resumes against job descriptions (JDs) in real time. It delivers weighted multi-factor match scoring, deep skill gap analytics, interactive cohort distributions, and AI-generated mock interview questions tailored to the candidate's exact profile gaps.

---

## 📚 In-Depth Documentation

- 🛠️ **[Technology Stack Details (TECHSTACK.md)](TECHSTACK.md)**: Deep breakdown of all libraries, frameworks, machine learning models, database schema, and runtime dependencies.
- 📘 **[Architecture & How It Works (HOW_IT_WORKS.md)](HOW_IT_WORKS.md)**: Complete step-by-step pipeline, sequence diagrams, and mathematical scoring formulas.

---

## 🌟 Key Features

- **Multi-Format Document Parsing**: Seamlessly extracts text from **PDF** (via `pdfplumber`), **DOCX** (via `python-docx`), and plain **TXT** files, or accepts direct copy-pasted job descriptions.
- **LLM-Powered Entity Extraction**: Uses Groq-hosted open-weights models (`gpt-oss-120b`, `llama-3.3-70b-versatile`) to reliably parse unstructured resumes and JDs into validated JSON schemas.
- **Multi-Factor Weighted Match Scoring**:
  - 🛠️ **Skill Match (50%)**: Exact & normalized comparison against required and preferred skills.
  - 💼 **Experience Alignment (25%)**: Ratio of candidate's total years of experience against job requirements.
  - 🎓 **Education Alignment (15%)**: Qualification, degree, and specialization relevance scoring.
  - 🧠 **Semantic Similarity (10%)**: Dense vector cosine similarity computed using HuggingFace's `all-MiniLM-L6-v2` embeddings.
- **Interactive Visual Dashboard**:
  - Top 5 KPI Summary Cards (Total Candidates, Average Match %, Assessment Rate, Avg Assessment Score, Total Skill Gaps Flagged).
  - Plotly interactive charts: Match Score Distribution Histogram, Most Frequent Skill Gaps Bar Chart, and Resume Match vs. Assessment Score Scatter Plot.
  - 6 Platform Navigation views (`Dashboard`, `Resume Analyzer`, `Candidate Assessment`, `Recruiter Database`, `Reports & Comparison`, `Settings`).
- **Dynamic AI Mock Interview Generator**: Generates 5 tailored interview questions (Technical, Behavioral, and Role-Fit) with specific evaluation criteria addressing the candidate's detected weaknesses.

---

## 🏗️ System Architecture

```mermaid
flowchart TD
    A[Candidate Resume\nPDF / DOCX / TXT] --> C[parser.py\nDocument Text Extractor]
    B[Job Description\nPDF / DOCX / TXT / Text] --> C

    C -->|Raw Resume Text| D[extractor.py\nGroq LLM Parser]
    C -->|Raw JD Text| D

    D -->|Structured Resume JSON| E[scorer.py\nMulti-Factor Scoring Engine]
    D -->|Structured JD JSON| E
    C -->|Dense Vector Embeddings| E

    E -->|Scores & Skill Gaps| H[(database.py\nSQLite Database)]
    H --> F[app.py\nStreamlit Dashboard & Visuals]
    D -->|Candidate Profile & Gaps| G[interview.py\nMock Interview Generator]
    G -->|Targeted Questions| F
```

---

## 🧮 Scoring Formula Breakdown

$$\text{Final Score} = (S \times 0.50) + (E \times 0.25) + (D \times 0.15) + (M \times 0.10)$$

| Dimension | Weight | Description |
| :--- | :---: | :--- |
| **Skill Match ($S$)** | **50%** | Percentage of mandatory required skills satisfied by the candidate. |
| **Experience ($E$)** | **25%** | Candidate years of experience relative to minimum required years (capped at 100%). |
| **Education ($D$)** | **15%** | Degree alignment against specified qualifications (100% exact match, 50% partial degree). |
| **Semantic Similarity ($M$)** | **10%** | Cosine similarity between resume and JD sentence embeddings. |

---

## 📁 Project Directory Structure

```text
├── .streamlit/
│   ├── secrets.toml            # Private API keys (git-ignored)
│   └── secrets.toml.example    # Configuration template for secrets
├── tests/
│   ├── __init__.py             # Unit test package initializer
│   ├── test_parser.py          # Document text extraction unit tests
│   └── test_scorer.py          # Skill overlap and scoring unit tests
├── .env.example                # Environment variable configuration template
├── .gitignore                  # Git ignore rules for virtualenvs, cache, and secrets
├── app.py                      # Main Streamlit web application & UI dashboard
├── database.py                 # SQLite database storage layer & candidate pipeline
├── extractor.py                # Groq LLM structured JSON entity extractor
├── interview.py                # AI tailored mock interview generator
├── parser.py                   # PDF, DOCX, and TXT document parser
├── requirements.txt            # Python package dependencies
├── scorer.py                   # Weighted multi-factor candidate scoring engine
├── HOW_IT_WORKS.md             # Complete architecture, pipeline & formula documentation
├── TECHSTACK.md                # Comprehensive technology stack reference
└── README.md                   # Main project overview & user guide
```

