# 🛠️ HALO Recruitment Platform — Technology Stack

This document provides a comprehensive technical breakdown of all frameworks, libraries, machine learning models, cloud services, and tools powering the **HALO AI Resume Analyzer & Talent Screening Platform**.

---

## 🏛️ High-Level Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            PRESENTATION LAYER                               │
│  Streamlit 1.35+ • Custom CSS Design System • Plotly Interactive Charts     │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
┌──────────────────────────────────────▼──────────────────────────────────────┐
│                            APPLICATION ENGINE                               │
│  Multi-Page Controller • Pipeline State Manager • SQLite Storage Layer      │
└──────────────┬───────────────────────┬───────────────────────┬──────────────┘
               │                       │                       │
┌──────────────▼───────┐ ┌─────────────▼─────────┐ ┌───────────▼──────────────┐
│  DOCUMENT PARSING    │ │    LLM INFERENCE      │ │   EMBEDDINGS & SCORING   │
│  • pdfplumber        │ │  • Groq Cloud API     │ │  • Sentence Transformers │
│  • python-docx       │ │  • gpt-oss-120b       │ │  • all-MiniLM-L6-v2      │
│  • io & utf-8 codecs │ │  • llama-3.3-70b      │ │  • scikit-learn Cosine   │
└──────────────────────┘ └───────────────────────┘ └──────────────────────────┘
```

---

## 💻 1. Core Framework & Web Presentation

| Technology | Version | Purpose & Rationale |
| :--- | :---: | :--- |
| **Python** | `3.10+` | Primary programming language providing robust data science and NLP ecosystem support. |
| **Streamlit** | `1.35.0+` | Full-stack reactive web application framework. Enables rapid UI rendering, reactive state management, and seamless Python backend integration without frontend-backend separation friction. |
| **Plotly Graph Objects** | `5.20.0+` | High-performance interactive data visualization library used for candidate score histograms, skill gap horizontal bar charts, scatter plots, and multi-axis radar charts. |
| **Pandas** | `2.2.0+` | High-performance data manipulation library powering candidate pipeline tables, sorting, searching, and CSV export. |
| **Custom Vanilla CSS** | Custom | Custom design system implementing Google Fonts (*Inter*), responsive KPI metric cards, badge indicators, subtle glassmorphic container styling, and light/dark theme tokens. |

---

## 🤖 2. Artificial Intelligence & Large Language Models (LLMs)

| Component | Specification | Description & Role |
| :--- | :---: | :--- |
| **Inference Engine** | **Groq Cloud API** | Ultra-low latency LPU (Language Processing Unit) inference platform delivering sub-second JSON response generation for candidate parsing. |
| **Primary LLM** | `openai/gpt-oss-120b` | High-capacity reasoning model utilized for parsing unstructured resumes and job descriptions into validated JSON schemas. |
| **Alternative Models** | `llama-3.3-70b-versatile`<br>`llama-3.1-8b-instant`<br>`mixtral-8x7b-32768` | Configurable fallback models for fast, cost-effective entity extraction and tailored interview question synthesis. |
| **Prompt Engineering** | Few-shot Schema Enforcement | Strict JSON-only prompt design using regex cleanup and schema validators to prevent markdown fences from breaking downstream logic. |

---

## 🧠 3. Machine Learning & Semantic Embeddings (NLP)

| Technology | Version / Model | Role in Pipeline |
| :--- | :---: | :--- |
| **Sentence-Transformers** | `3.0.0+` | Hugging Face framework used to compute dense vector semantic embeddings for entire resume and JD texts. |
| **Embedding Model** | `all-MiniLM-L6-v2` | Lightweight (80MB), fast, 384-dimensional sentence embedding model mapping texts into dense vector space. |
| **Scikit-Learn** | `1.4.0+` | Computes pairwise cosine similarity between resume and job description vectors to measure holistic contextual alignment. |
| **PyTorch (torch)** | `2.2.0+` | Deep learning runtime executing tensor operations for the SentenceTransformer embedding model on CPU or CUDA. |

---

## 📄 4. Document Ingestion & Text Extraction

| Library | Version | Format Handled | Description |
| :--- | :---: | :---: | :--- |
| **pdfplumber** | `0.11.0+` | `.pdf` | High-precision PDF parser extracting text page-by-page while preserving layout and whitespace integrity. |
| **python-docx** | `1.1.0+` | `.docx` | Microsoft Word document reader converting structured paragraphs and tables into unified raw text strings. |
| **Python Standard Codecs** | Standard Library | `.txt` | Plain-text decoder with multi-encoding fallback (`utf-8`, `utf-16`, `latin-1`, `cp1252`). |

---

## 🗄️ 5. Persistence & Database Layer

| Component | Technology | Description |
| :--- | :---: | :--- |
| **Database Engine** | **SQLite 3** | Zero-configuration, serverless, self-contained relational database embedded directly in Python. |
| **Database File** | `candidates.db` | Stores candidate metadata, individual scoring breakdowns, JSON skill gap lists, interview assessment scores, and timestamps. |
| **Schema Management** | Automatic (`database.py`) | Auto-initializes schema on startup with support for pre-seeding realistic benchmark candidate pipelines. |

---

## 🧪 6. Testing, Quality Assurance & Security

| Tool / Practice | Purpose |
| :--- | :--- |
| **unittest** | Standard Python unit testing framework verifying skill normalization, set overlap math, experience ratios, and document parsers. |
| **Streamlit Secrets** (`.streamlit/secrets.toml`) | Secure, local credential isolation for private Groq API keys. |
| **Git Ignore Rules** (`.gitignore`) | Strict exclusion rules preventing credentials, virtual environments (`.venv`), and compiled caches from reaching public repositories. |

---

## 📦 7. Summary Dependency Manifest (`requirements.txt`)

```ini
# Core Application Framework
streamlit>=1.35.0
plotly>=5.20.0
pandas>=2.2.0

# Document Parsing
pdfplumber>=0.11.0
python-docx>=1.1.0

# AI & LLM Inference
groq>=0.9.0

# Machine Learning & NLP (Semantic Similarity)
sentence-transformers>=3.0.0
scikit-learn>=1.4.0
torch>=2.2.0

# Utilities & Environment
python-dotenv>=1.0.0
pydantic>=2.0.0
```
