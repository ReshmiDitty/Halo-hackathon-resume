"""
HALO Recruitment & Talent Intelligence Platform (v2.0).

AI-powered candidate screening, talent cohort analytics, skill gap distributions,
real-time multi-factor resume scoring, and mock interview assessment pipeline.
Light Theme Edition with Executive Visual Profiling.
"""

import json
from collections import Counter
import html
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import database as db
from extractor import extract_jd_data, extract_resume_data, get_groq_api_key, DEFAULT_MODEL
from interview import generate_mock_questions
from parser import extract_text
from scorer import calculate_match_score

# ---------- PAGE CONFIGURATION ----------
st.set_page_config(
    page_title="HALO – AI Recruitment & Screening Platform",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- GLOBAL LIGHT THEME STYLING ----------
st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
    
    html, body, [class*="css"], .stApp {
        font-family: 'Inter', sans-serif;
        background-color: #F8FAFC !important;
        color: #0F172A !important;
    }

    /* Top header bar adjustment */
    header[data-testid="stHeader"] {
        background-color: transparent !important;
    }

    /* Sidebar Light Styling */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E2E8F0 !important;
    }
    section[data-testid="stSidebar"] .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2rem;
    }

    /* Nav Header */
    .nav-header {
        color: #0284C7 !important;
        font-size: 0.78rem !important;
        font-weight: 800 !important;
        letter-spacing: 1.6px !important;
        text-transform: uppercase !important;
        margin: 1.4rem 0 0.8rem 0 !important;
    }

    /* Sidebar Navigation Radio Buttons */
    div[data-testid="stRadio"] div[role="radiogroup"] {
        gap: 6px !important;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] > label {
        background-color: #F8FAFC !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 8px !important;
        padding: 8px 12px !important;
        margin-bottom: 4px !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
        display: flex !important;
        align-items: center !important;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] > label:hover {
        background-color: #F0F9FF !important;
        border-color: #38BDF8 !important;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] > label:has(input:checked) {
        background-color: #E0F2FE !important;
        border-color: #0284C7 !important;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] label p,
    div[data-testid="stRadio"] div[role="radiogroup"] label span,
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label p,
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label span {
        color: #0F172A !important;
        font-weight: 700 !important;
        font-size: 0.92rem !important;
        opacity: 1 !important;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] > label:has(input:checked) p {
        color: #0369A1 !important;
        font-weight: 800 !important;
    }

    /* System Status Card in Sidebar */
    .status-card {
        background: #FFFFFF !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 10px;
        padding: 14px 16px;
        margin-top: 1.5rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    }
    .status-card-title {
        font-weight: 800 !important;
        color: #0F172A !important;
        font-size: 0.78rem !important;
        letter-spacing: 1.2px;
        text-transform: uppercase;
        margin-bottom: 10px;
    }
    .status-row {
        display: flex;
        justify-content: space-between;
        color: #334155 !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        margin-bottom: 6px;
    }
    .status-row span:first-child {
        color: #475569 !important;
        font-weight: 600 !important;
    }
    .status-val-local {
        color: #0284C7 !important;
        font-weight: 800 !important;
    }
    .status-val-online {
        color: #16A34A !important;
        font-weight: 800 !important;
    }

    /* Typography */
    .eyebrow {
        color: #0284C7;
        font-weight: 800;
        font-size: 0.8rem;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 8px;
    }
    .main-title {
        font-size: 2.3rem;
        font-weight: 800;
        color: #0F172A;
        margin-bottom: 6px;
        line-height: 1.2;
    }
    .subtitle {
        color: #64748B;
        font-size: 1rem;
        margin-bottom: 2rem;
    }

    /* Metric KPI Cards */
    .kpi-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 1.1rem 1.2rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    }
    .kpi-title {
        color: #64748B;
        font-size: 0.72rem;
        font-weight: 800;
        letter-spacing: 0.8px;
        text-transform: uppercase;
        margin-bottom: 8px;
    }
    .kpi-num {
        font-size: 2.1rem;
        font-weight: 800;
        line-height: 1;
        margin-bottom: 6px;
    }
    .kpi-footer {
        font-size: 0.78rem;
        font-weight: 700;
    }

    /* Section Headings */
    .section-title {
        font-size: 1.25rem;
        font-weight: 800;
        color: #0F172A;
        margin: 2rem 0 1.2rem 0;
    }

    /* Chart Containers */
    .chart-box {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 1rem 1rem 0.2rem 1rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    }
    .chart-title {
        font-size: 0.92rem;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 0.5rem;
    }

    /* Custom Badges */
    .badge {
        display: inline-block;
        padding: 5px 12px;
        border-radius: 999px;
        font-size: 0.8rem;
        font-weight: 700;
        margin: 3px 4px 3px 0;
    }
    .badge-matched {
        background: #DCFCE7;
        color: #15803D;
        border: 1px solid #86EFAC;
    }
    .badge-missing-req {
        background: #FEE2E2;
        color: #B91C1C;
        border: 1px solid #FCA5A5;
    }
    .badge-missing-pref {
        background: #FEF9C3;
        color: #A16207;
        border: 1px solid #FDE047;
    }

    /* Cards */
    .light-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 1.1rem 1.3rem;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    .light-card-title {
        font-weight: 700;
        color: #0F172A;
        font-size: 1.05rem;
    }
    .light-card-meta {
        color: #64748B;
        font-size: 0.88rem;
        margin-bottom: 0.4rem;
    }

    /* File Uploader Exhaustive Light Theme Styling */
    div[data-testid="stFileUploader"],
    div[data-testid="stFileUploader"] section,
    div[data-testid="stFileUploader"] > div,
    section[data-testid="stFileUploadDropzone"],
    section[data-testid="stFileUploaderDropzone"],
    div[data-testid="stFileUploadDropzone"],
    div[data-testid="stFileUploaderDropzone"],
    div[data-testid="stFileUploaderDropzone"] > div,
    .stFileUploaderDropzone {
        background-color: #FFFFFF !important;
        background: #FFFFFF !important;
        color: #0F172A !important;
        border: 1px dashed #CBD5E1 !important;
        border-radius: 10px !important;
    }
    
    /* Uploaded file preview bar */
    div[data-testid="stUploadedFile"],
    div[data-testid="stUploadedFile"] > div,
    div[data-testid="stUploadedFileData"],
    [data-testid="stUploadedFile"],
    [data-testid="stUploadedFile"] * {
        background-color: #FFFFFF !important;
        background: #FFFFFF !important;
        color: #0F172A !important;
        fill: #0F172A !important;
    }
    div[data-testid="stUploadedFile"] {
        border: 1px solid #CBD5E1 !important;
        border-radius: 8px !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
        padding: 6px 12px !important;
    }
    div[data-testid="stUploadedFile"] small {
        color: #64748B !important;
    }
    
    /* Browse files button inside uploader */
    div[data-testid="stFileUploader"] button {
        background: #F1F5F9 !important;
        color: #0F172A !important;
        border: 1px solid #CBD5E1 !important;
        font-weight: 700 !important;
        border-radius: 6px !important;
    }
    div[data-testid="stFileUploader"] button:hover {
        background: #E2E8F0 !important;
        color: #0284C7 !important;
    }

    /* Inputs and Textareas Light Styling */
    textarea[data-testid="stTextArea"],
    .stTextArea textarea,
    .stTextInput input,
    div[data-baseweb="textarea"],
    div[data-baseweb="textarea"] textarea,
    div[data-baseweb="input"],
    div[data-baseweb="input"] input {
        background-color: #FFFFFF !important;
        background: #FFFFFF !important;
        color: #0F172A !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 8px !important;
    }
    .stTextInput>div>div>input::placeholder, .stTextArea>div>div>textarea::placeholder {
        color: #94A3B8 !important;
    }
    .stSelectbox>div>div {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 8px !important;
    }

    /* Light Theme Data Table */
    .table-container {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        overflow-x: auto;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        margin: 1rem 0;
    }
    .custom-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.88rem;
        color: #0F172A;
    }
    .custom-table th {
        background-color: #F8FAFC;
        color: #475569;
        font-weight: 800;
        font-size: 0.75rem;
        letter-spacing: 0.8px;
        text-transform: uppercase;
        padding: 14px 16px;
        text-align: left;
        border-bottom: 1px solid #E2E8F0;
    }
    .custom-table td {
        padding: 14px 16px;
        border-bottom: 1px solid #F1F5F9;
        vertical-align: middle;
    }
    .custom-table tr:last-child td {
        border-bottom: none;
    }
    .custom-table tr:hover {
        background-color: #F8FAFC;
    }

    /* Table Status Pills */
    .table-pill-assessed {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: #DCFCE7;
        color: #15803D;
        font-weight: 700;
        font-size: 0.78rem;
        padding: 4px 10px;
        border-radius: 999px;
        border: 1px solid #86EFAC;
    }
    .table-pill-screened {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: #E0F2FE;
        color: #0369A1;
        font-weight: 700;
        font-size: 0.78rem;
        padding: 4px 10px;
        border-radius: 999px;
        border: 1px solid #BAE6FD;
    }
    
    /* Primary buttons */
    .stButton>button {
        background: linear-gradient(90deg, #0284C7, #4F46E5) !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.6rem 1.5rem !important;
        transition: all 0.2s ease-in-out;
    }
    .stButton>button:hover {
        opacity: 0.92;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(2, 132, 199, 0.25);
    }
</style>
""",
    unsafe_allow_html=True,
)

# Initialize database
db.init_db()


def render_light_table(headers, rows):
    """Render a clean, modern, light-themed HTML table."""
    th_html = "".join([f"<th>{html.escape(h)}</th>" for h in headers])
    tr_html = ""
    for row in rows:
        td_html = "".join([f"<td>{r}</td>" for r in row])
        tr_html += f"<tr>{td_html}</tr>"

    table_markup = f"""
    <div class="table-container">
        <table class="custom-table">
            <thead>
                <tr>{th_html}</tr>
            </thead>
            <tbody>
                {tr_html}
            </tbody>
        </table>
    </div>
    """
    st.markdown(table_markup, unsafe_allow_html=True)


# ---------- SIDEBAR NAVIGATION & ACTIONS ----------
with st.sidebar:
    if st.button("✨ Load Demo Candidate (John Doe)", use_container_width=True):
        st.session_state["demo_loaded"] = True
        st.success("Loaded John Doe demo profile!")

    st.markdown('<div class="nav-header">PLATFORM NAVIGATION</div>', unsafe_allow_html=True)
    
    page = st.radio(
        "Navigation",
        options=[
            "📊 Dashboard",
            "📄 Resume Analyzer",
            "🎯 Candidate Assessment",
            "👥 Recruiter Database",
            "⚖️ Reports & Comparison",
            "⚙️ Settings",
        ],
        label_visibility="collapsed",
    )

    # Fetch live candidate count for status
    candidates_list = db.get_all_candidates()
    candidate_count = len(candidates_list)
    has_api_key = bool(get_groq_api_key())

    ai_engine_text = "GROQ CLOUD" if has_api_key else "LOCAL FALLBACK"
    ai_engine_color = "#0284C7" if has_api_key else "#D97706"

    st.markdown(
        f"""
    <div class="status-card">
        <div class="status-card-title">SYSTEM STATUS</div>
        <div class="status-row"><span>AI Engine:</span><span class="status-val-local" style="color:{ai_engine_color};">{ai_engine_text}</span></div>
        <div class="status-row"><span>Database:</span><span class="status-val-online">SQLite Online</span></div>
        <div class="status-row"><span>Candidates:</span><span style="font-weight:800; color:#0F172A;">{candidate_count}</span></div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div style="color:#94A3B8; font-size:0.75rem; text-align:center; margin-top:2rem;">HALO Platform v2.0 • AI Recruitment</div>',
        unsafe_allow_html=True,
    )


# ==============================================================================
# PAGE 1: TALENT SCREENING & HIRING DASHBOARD
# ==============================================================================
if page == "📊 Dashboard":
    st.markdown('<div class="eyebrow">RECRUITER COMMAND CENTER</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-title">Talent Screening & Hiring Dashboard</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="subtitle">Real-time metrics, qualification benchmarks, skill gap distributions, and candidate evaluation pipeline.</div>',
        unsafe_allow_html=True,
    )

    all_cands = db.get_all_candidates()
    total_cands = len(all_cands)

    if total_cands > 0:
        avg_match = sum(c["match_score"] for c in all_cands) / total_cands
        assessed_cands = [c for c in all_cands if c["status"] == "Assessed" and c["assessment_score"] > 0]
        assessed_count = len(assessed_cands)
        assessment_rate = (assessed_count / total_cands) * 100.0 if total_cands > 0 else 0.0
        avg_assessment = sum(c["assessment_score"] for c in assessed_cands) / assessed_count if assessed_count > 0 else 0.0
        
        all_gaps = []
        for c in all_cands:
            all_gaps.extend(c["missing_skills"])
        total_gaps_flagged = len(all_gaps)
    else:
        avg_match = 0.0
        assessed_count = 0
        assessment_rate = 0.0
        avg_assessment = 0.0
        total_gaps_flagged = 0
        all_gaps = []

    # 5 KPI Metric Cards (Light Theme)
    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        st.markdown(
            f"""
        <div class="kpi-card">
            <div class="kpi-title">TOTAL CANDIDATES</div>
            <div class="kpi-num" style="color: #0284C7;">{total_cands}</div>
            <div class="kpi-footer" style="color: #0369A1;">Active Pipeline</div>
        </div>
        """,
            unsafe_allow_html=True,
        )
    with k2:
        st.markdown(
            f"""
        <div class="kpi-card">
            <div class="kpi-title">AVERAGE MATCH %</div>
            <div class="kpi-num" style="color: #16A34A;">{avg_match:.1f}%</div>
            <div class="kpi-footer" style="color: #64748B;">Resume Screening</div>
        </div>
        """,
            unsafe_allow_html=True,
        )
    with k3:
        st.markdown(
            f"""
        <div class="kpi-card">
            <div class="kpi-title">ASSESSMENT RATE</div>
            <div class="kpi-num" style="color: #7C3AED;">{assessment_rate:.0f}%</div>
            <div class="kpi-footer" style="color: #64748B;">{assessed_count}/{total_cands} Assessed</div>
        </div>
        """,
            unsafe_allow_html=True,
        )
    with k4:
        st.markdown(
            f"""
        <div class="kpi-card">
            <div class="kpi-title">AVG ASSESSMENT</div>
            <div class="kpi-num" style="color: #0D9488;">{avg_assessment:.1f}%</div>
            <div class="kpi-footer" style="color: #059669;">Interview Average</div>
        </div>
        """,
            unsafe_allow_html=True,
        )
    with k5:
        st.markdown(
            f"""
        <div class="kpi-card">
            <div class="kpi-title">SKILL GAPS FLAGGED</div>
            <div class="kpi-num" style="color: #DC2626;">{total_gaps_flagged}</div>
            <div class="kpi-footer" style="color: #C2410C;">Missing Skills</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    # Section Heading
    st.markdown('<div class="section-title">Cohort Analytics & Distribution Models</div>', unsafe_allow_html=True)

    # 3 Light Plotly Charts side by side
    ch1, ch2, ch3 = st.columns(3)

    light_layout = dict(
        height=280,
        margin=dict(l=10, r=10, t=20, b=20),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        font=dict(family="Inter", color="#475569", size=11),
    )

    # Chart 1: Candidate Match Score Distribution
    with ch1:
        st.markdown('<div class="chart-box"><div class="chart-title">Candidate Match Score Distribution</div>', unsafe_allow_html=True)
        scores = [c["match_score"] for c in all_cands]
        fig1 = go.Figure()
        fig1.add_trace(
            go.Histogram(
                x=scores,
                xbins=dict(start=0, end=100, size=5),
                marker=dict(color="#0284C7", line=dict(color="#0369A1", width=1)),
                opacity=0.9,
            )
        )
        fig1.update_layout(
            **light_layout,
            xaxis=dict(title="Match Score (%)", range=[0, 100], gridcolor="#F1F5F9", tickfont=dict(color="#475569")),
            yaxis=dict(title="Candidate Count", gridcolor="#F1F5F9", tickfont=dict(color="#475569")),
        )
        st.plotly_chart(fig1, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Chart 2: Most Frequent Skill Gaps
    with ch2:
        st.markdown('<div class="chart-box"><div class="chart-title">Most Frequent Skill Gaps</div>', unsafe_allow_html=True)
        gap_counts = Counter(all_gaps).most_common(5)
        if gap_counts:
            skills = [item[0] for item in reversed(gap_counts)]
            counts = [item[1] for item in reversed(gap_counts)]
            fig2 = go.Figure(
                go.Bar(
                    x=counts,
                    y=skills,
                    orientation="h",
                    marker=dict(color="#EF4444"),
                    text=counts,
                    textposition="inside",
                    textfont=dict(color="#FFFFFF", weight="bold"),
                )
            )
            fig2.update_layout(
                **light_layout,
                xaxis=dict(title="Candidates Missing Skill", gridcolor="#F1F5F9", tickfont=dict(color="#475569")),
                yaxis=dict(gridcolor="#F1F5F9", tickfont=dict(color="#0F172A")),
            )
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No skill gaps flagged in candidate pool.")
        st.markdown("</div>", unsafe_allow_html=True)

    # Chart 3: Resume Match vs. Assessment Score
    with ch3:
        st.markdown('<div class="chart-box"><div class="chart-title">Resume Match vs. Assessment Score</div>', unsafe_allow_html=True)
        screened = [c for c in all_cands if c["status"] == "Screened"]
        assessed = [c for c in all_cands if c["status"] == "Assessed"]

        fig3 = go.Figure()
        if screened:
            fig3.add_trace(
                go.Scatter(
                    x=[c["match_score"] for c in screened],
                    y=[c["assessment_score"] for c in screened],
                    mode="markers",
                    name="Screened",
                    marker=dict(size=9, color="#0284C7", symbol="circle"),
                )
            )
        if assessed:
            fig3.add_trace(
                go.Scatter(
                    x=[c["match_score"] for c in assessed],
                    y=[c["assessment_score"] for c in assessed],
                    mode="markers",
                    name="Assessed",
                    marker=dict(size=10, color="#16A34A", symbol="circle"),
                )
            )

        fig3.update_layout(
            **light_layout,
            xaxis=dict(title="Resume Match (%)", range=[0, 105], gridcolor="#F1F5F9", tickfont=dict(color="#475569")),
            yaxis=dict(title="Assessment Score (%)", range=[-5, 105], gridcolor="#F1F5F9", tickfont=dict(color="#475569")),
            legend=dict(orientation="v", x=0.75, y=0.95, font=dict(color="#0F172A", size=10)),
        )
        st.plotly_chart(fig3, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Candidate Pipeline Stream with Filter & Sorting Controls
    st.markdown('<div class="section-title">Candidate Pipeline Stream</div>', unsafe_allow_html=True)
    
    ctrl_col1, ctrl_col2 = st.columns([1, 1])
    with ctrl_col1:
        stream_filter = st.selectbox(
            "Filter by Candidate Status:",
            ["All Candidates", "Screened Only", "Assessed Only"],
            key="stream_status_filter",
        )
    with ctrl_col2:
        stream_sort = st.selectbox(
            "Sort Candidate Order:",
            [
                "Highest Match Score First (High → Low)",
                "Lowest Match Score First (Low → High)",
                "Highest Assessment Score (High → Low)",
                "Most Experience (Years)",
            ],
            key="stream_sort_order",
        )

    # Filter pipeline stream
    displayed_cands = list(all_cands)
    if stream_filter == "Screened Only":
        displayed_cands = [c for c in displayed_cands if c["status"] == "Screened"]
    elif stream_filter == "Assessed Only":
        displayed_cands = [c for c in displayed_cands if c["status"] == "Assessed"]

    # Sort pipeline stream
    if stream_sort == "Highest Match Score First (High → Low)":
        displayed_cands.sort(key=lambda c: c["match_score"], reverse=True)
    elif stream_sort == "Lowest Match Score First (Low → High)":
        displayed_cands.sort(key=lambda c: c["match_score"], reverse=False)
    elif stream_sort == "Highest Assessment Score (High → Low)":
        displayed_cands.sort(key=lambda c: c["assessment_score"], reverse=True)
    elif stream_sort == "Most Experience (Years)":
        displayed_cands.sort(key=lambda c: c["experience_years"], reverse=True)

    if displayed_cands:
        table_rows = []
        for c in displayed_cands:
            status_html = (
                '<span class="table-pill-assessed">● Assessed</span>'
                if c["status"] == "Assessed"
                else '<span class="table-pill-screened">● Screened</span>'
            )
            gaps_text = ", ".join(c["missing_skills"][:2]) + ("..." if len(c["missing_skills"]) > 2 else "")
            assess_text = f"<strong>{c['assessment_score']:.1f}%</strong>" if c["status"] == "Assessed" else "<span style='color:#94A3B8;'>Pending</span>"
            table_rows.append([
                f"<strong>{html.escape(c['name'])}</strong>",
                html.escape(c["role"]),
                f"<span style='color:#0284C7; font-weight:800; font-size:0.95rem;'>{c['match_score']:.1f}%</span>",
                f"{c['skill_match']:.0f}%",
                assess_text,
                html.escape(gaps_text) or "<span style='color:#16A34A; font-weight:600;'>None</span>",
                status_html,
            ])
        render_light_table(
            headers=["Candidate", "Target Role", "Match Score", "Skill Match", "Assessment", "Primary Skill Gaps", "Status"],
            rows=table_rows,
        )
    else:
        st.info(f"No candidates match the selected filter ('{stream_filter}').")


# ==============================================================================
# PAGE 2: RESUME ANALYZER
# ==============================================================================
elif page == "📄 Resume Analyzer":
    st.markdown('<div class="eyebrow">SCREENING & INTELLIGENCE</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-title">Resume vs. Job Description Analyzer</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="subtitle">Extract structured candidate entities, compute multi-factor match scores, and automatically add to your candidate pipeline.</div>',
        unsafe_allow_html=True,
    )

    # Demo pre-fill if button was clicked
    default_cand_name = "John Doe" if st.session_state.get("demo_loaded") else ""
    default_cand_role = "Senior Full Stack Engineer" if st.session_state.get("demo_loaded") else ""

    col_meta1, col_meta2 = st.columns(2)
    with col_meta1:
        candidate_name = st.text_input("Candidate Full Name", value=default_cand_name, placeholder="e.g. John Doe")
    with col_meta2:
        target_role = st.text_input("Target Job Title / Position", value=default_cand_role, placeholder="e.g. Senior Software Engineer")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**📎 Upload Candidate Resume**")
        resume_file = st.file_uploader(
            "Upload Resume (PDF, DOCX, TXT)",
            type=["pdf", "docx", "txt"],
            key="analyzer_resume_uploader",
        )

    with col2:
        st.markdown("**💼 Job Description**")
        jd_file = st.file_uploader(
            "Upload JD Document (PDF, DOCX, TXT)",
            type=["pdf", "docx", "txt"],
            key="analyzer_jd_uploader",
        )
        jd_text_input = st.text_area(
            "Or paste JD text directly:",
            height=100,
            placeholder="Paste required skills, experience level, and key responsibilities...",
        )

    st.write("")
    analyze_btn = st.button("✨ Run Deep Match Analysis", type="primary")

    if analyze_btn:
        if not resume_file and not st.session_state.get("demo_loaded"):
            st.error("Please upload a candidate resume.")
            st.stop()
        if not jd_file and not jd_text_input.strip() and not st.session_state.get("demo_loaded"):
            st.error("Please upload a job description file or paste the JD text.")
            st.stop()

        with st.spinner("Extracting document content and executing AI analysis..."):
            if st.session_state.get("demo_loaded") and not resume_file:
                demo = db.DEMO_CANDIDATES[0]
                resume_data = {
                    "skills": ["Python", "JavaScript", "React", "Node.js", "Docker", "AWS", "SQL", "Git", "REST APIs", "Agile/Scrum"],
                    "education": [{"degree": "Bachelor of Science in Computer Science", "institution": "State University", "year": "2020"}],
                    "experience": [
                        {"title": "Senior Software Engineer", "company": "Tech Innovations Inc.", "duration": "3.5 years", "description": "Architected high-throughput microservices using Python, FastAPI, and Docker. Led a team of 4 engineers."},
                        {"title": "Full Stack Developer", "company": "CloudScale Systems", "duration": "2.7 years", "description": "Developed React single-page applications and RESTful APIs with Node.js and PostgreSQL."}
                    ],
                    "total_years_experience": demo["experience_years"],
                }
                jd_data = {
                    "required_skills": ["Python", "React", "Node.js", "Docker", "Kubernetes", "AWS"],
                    "preferred_skills": ["GraphQL", "CI/CD"],
                    "required_experience_years": 5,
                    "education_requirement": "Bachelor of Science in Computer Science",
                    "key_responsibilities": ["Lead development", "Architect distributed systems"],
                }
                resume_text = "Experienced Full Stack Engineer with Python, React, Node.js, Docker, AWS, and database skills."
                jd_text = "Looking for a Senior Full Stack Engineer with Python, React, Docker, Kubernetes, AWS, GraphQL."
            else:
                resume_text = extract_text(resume_file)
                jd_text = extract_text(jd_file) if jd_file else jd_text_input.strip()
                resume_data = extract_resume_data(resume_text)
                jd_data = extract_jd_data(jd_text)

            result = calculate_match_score(resume_data, jd_data, resume_text, jd_text)
            
            # Auto-save to SQLite database
            c_name = candidate_name.strip() or "Candidate " + str(total_cands + 1)
            c_role = target_role.strip() or "Software Engineer"
            db.add_candidate(
                name=c_name,
                role=c_role,
                match_score=result["final_score"],
                skill_match=result["breakdown"]["skill_match"],
                experience_match=result["breakdown"]["experience_match"],
                education_match=result["breakdown"]["education_match"],
                semantic_similarity=result["breakdown"]["semantic_similarity"],
                missing_skills=result["skill_gap"]["missing_required"] + result["skill_gap"]["missing_preferred"],
                experience_years=resume_data.get("total_years_experience", 0.0),
                education=resume_data.get("education", [{}])[0].get("degree", ""),
            )

            st.session_state["last_analysis"] = {
                "name": c_name,
                "role": c_role,
                "resume_data": resume_data,
                "jd_data": jd_data,
                "result": result,
            }
            st.success(f"Analysis complete! Candidate '{c_name}' successfully added to Recruiter Database.")

    if "last_analysis" in st.session_state:
        analysis = st.session_state["last_analysis"]
        result = analysis["result"]
        b = result["breakdown"]
        gap = result["skill_gap"]
        final_score = result["final_score"]
        rdata = analysis["resume_data"]

        st.markdown('<div class="section-title">Match Analysis Results</div>', unsafe_allow_html=True)
        r1, r2, r3, r4 = st.columns(4)
        with r1:
            st.markdown(
                f"""
            <div class="kpi-card">
                <div class="kpi-title">OVERALL MATCH</div>
                <div class="kpi-num" style="color: #16A34A;">{final_score:.1f}%</div>
                <div class="kpi-footer" style="color: #64748B;">Weighted Rating</div>
            </div>
            """,
                unsafe_allow_html=True,
            )
        with r2:
            st.markdown(
                f"""
            <div class="kpi-card">
                <div class="kpi-title">SKILL MATCH (50%)</div>
                <div class="kpi-num" style="color: #0284C7;">{b['skill_match']:.0f}%</div>
                <div class="kpi-footer" style="color: #64748B;">Required Competencies</div>
            </div>
            """,
                unsafe_allow_html=True,
            )
        with r3:
            st.markdown(
                f"""
            <div class="kpi-card">
                <div class="kpi-title">EXPERIENCE (25%)</div>
                <div class="kpi-num" style="color: #7C3AED;">{b['experience_match']:.0f}%</div>
                <div class="kpi-footer" style="color: #64748B;">Tenure Match</div>
            </div>
            """,
                unsafe_allow_html=True,
            )
        with r4:
            st.markdown(
                f"""
            <div class="kpi-card">
                <div class="kpi-title">EDUCATION (15%)</div>
                <div class="kpi-num" style="color: #D97706;">{b['education_match']:.0f}%</div>
                <div class="kpi-footer" style="color: #64748B;">Degree Requirement</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        # Tabbed Breakdown
        tab1, tab2, tab3 = st.tabs(["🎯 Skill Gap Detail", "🧠 Extracted Candidate Profile", "📊 Comparison Radar"])
        
        with tab1:
            st.markdown("**Matched Skills:**")
            st.markdown("".join([f'<span class="badge badge-matched">{s}</span>' for s in gap["matched"]]) or "*None*", unsafe_allow_html=True)

            st.markdown("<br>**Missing Required Skills:**", unsafe_allow_html=True)
            st.markdown("".join([f'<span class="badge badge-missing-req">{s}</span>' for s in gap["missing_required"]]) or "*None (All Matched)*", unsafe_allow_html=True)

            st.markdown("<br>**Missing Preferred Skills:**", unsafe_allow_html=True)
            st.markdown("".join([f'<span class="badge badge-missing-pref">{s}</span>' for s in gap["missing_preferred"]]) or "*None*", unsafe_allow_html=True)

        # TAB 2: GORGEOUS, PROFESSIONAL CANDIDATE PROFILE (NO RAW CODE)
        with tab2:
            st.markdown(
                f"""
            <div style="display:flex; justify-content:space-between; align-items:center; background:#FFFFFF; border:1px solid #E2E8F0; border-radius:10px; padding:12px 18px; margin-bottom:1.2rem;">
                <div>
                    <span style="color:#64748B; font-size:0.8rem; font-weight:700; text-transform:uppercase; letter-spacing:0.8px;">Parsed Candidate</span>
                    <h3 style="margin:0; color:#0F172A; font-size:1.2rem; font-weight:800;">{html.escape(analysis['name'])}</h3>
                </div>
                <div style="text-align:right;">
                    <span style="color:#64748B; font-size:0.8rem; font-weight:700; text-transform:uppercase; letter-spacing:0.8px;">Total Experience</span>
                    <div style="font-size:1.2rem; font-weight:800; color:#0284C7;">{rdata.get('total_years_experience', 0)} Years</div>
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )

            # Skills Section
            st.markdown('<div style="font-weight:800; color:#0F172A; font-size:0.95rem; margin-bottom:6px;">🛠️ Identified Technical & Professional Skills</div>', unsafe_allow_html=True)
            skills_list = rdata.get("skills", [])
            if skills_list:
                skills_badges = "".join([f'<span class="badge badge-matched" style="background:#F0F9FF; color:#0369A1; border-color:#BAE6FD; font-size:0.85rem; padding:6px 14px;">{html.escape(s)}</span>' for s in skills_list])
                st.markdown(f'<div style="margin-bottom:1.5rem;">{skills_badges}</div>', unsafe_allow_html=True)
            else:
                st.info("No specific skills extracted.")

            # Education Section
            st.markdown('<div style="font-weight:800; color:#0F172A; font-size:0.95rem; margin-bottom:6px;">🎓 Education & Academic History</div>', unsafe_allow_html=True)
            edu_list = rdata.get("education", [])
            if edu_list:
                for edu in edu_list:
                    st.markdown(
                        f"""
                    <div class="light-card" style="border-left: 4px solid #0284C7; margin-bottom:0.7rem;">
                        <div style="font-weight:800; color:#0F172A; font-size:1rem;">{html.escape(edu.get('degree', 'Degree'))}</div>
                        <div style="color:#64748B; font-size:0.88rem; margin-top:2px;">🏛️ {html.escape(edu.get('institution', 'University'))} &nbsp;·&nbsp; 🗓️ {html.escape(str(edu.get('year', 'N/A')))}</div>
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )
            else:
                st.info("No formal education history detected.")

            # Experience Section
            st.markdown('<div style="font-weight:800; color:#0F172A; font-size:0.95rem; margin:1.2rem 0 6px 0;">💼 Professional Work Experience</div>', unsafe_allow_html=True)
            exp_list = rdata.get("experience", [])
            if exp_list:
                for exp in exp_list:
                    desc = html.escape(exp.get("description", ""))
                    st.markdown(
                        f"""
                    <div class="light-card" style="border-left: 4px solid #16A34A; margin-bottom:0.8rem;">
                        <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                            <div>
                                <div style="font-weight:800; color:#0F172A; font-size:1.02rem;">{html.escape(exp.get('title', 'Position'))}</div>
                                <div style="color:#0284C7; font-weight:700; font-size:0.9rem; margin-top:2px;">🏢 {html.escape(exp.get('company', 'Company'))}</div>
                            </div>
                            <span class="badge" style="background:#F1F5F9; color:#475569; border:1px solid #E2E8F0;">⏱️ {html.escape(str(exp.get('duration', 'N/A')))}</span>
                        </div>
                        <div style="color:#334155; font-size:0.88rem; margin-top:8px; line-height:1.5;">{desc}</div>
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )
            else:
                st.info("No detailed work history detected.")

            with st.expander("🔍 View Raw JSON Data (Developer Reference)"):
                st.json(rdata)

        with tab3:
            radar_fig = go.Figure()
            radar_fig.add_trace(
                go.Scatterpolar(
                    r=[b["skill_match"], b["experience_match"], b["education_match"], b["semantic_similarity"]],
                    theta=["Skills", "Experience", "Education", "Semantic"],
                    fill="toself",
                    fillcolor="rgba(2, 132, 199, 0.15)",
                    line=dict(color="#0284C7", width=2),
                    name=analysis["name"],
                )
            )
            radar_fig.update_layout(
                polar=dict(
                    bgcolor="#FFFFFF",
                    radialaxis=dict(visible=True, range=[0, 100], gridcolor="#F1F5F9", linecolor="#CBD5E1"),
                    angularaxis=dict(gridcolor="#F1F5F9", linecolor="#CBD5E1"),
                ),
                paper_bgcolor="#FFFFFF",
                font=dict(color="#0F172A"),
                margin=dict(l=20, r=20, t=20, b=20),
                height=300,
            )
            st.plotly_chart(radar_fig, use_container_width=True)


# ==============================================================================
# PAGE 3: CANDIDATE ASSESSMENT & MOCK INTERVIEW
# ==============================================================================
elif page == "🎯 Candidate Assessment":
    st.markdown('<div class="eyebrow">INTERVIEW INTELLIGENCE</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-title">Candidate Assessment & Interview Studio</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="subtitle">Generate tailored interview questions targeting candidate skill gaps, record interview evaluations, and update the hiring pipeline.</div>',
        unsafe_allow_html=True,
    )

    all_cands = db.get_all_candidates()
    if not all_cands:
        st.warning("No candidates found in database. Please add candidates via Resume Analyzer first.")
    else:
        candidate_names = [f"{c['id']} - {c['name']} ({c['role']})" for c in all_cands]
        selected_option = st.selectbox("Select Candidate to Evaluate", candidate_names)
        cand_id = int(selected_option.split(" - ")[0])
        cand = next(c for c in all_cands if c["id"] == cand_id)

        c1, c2 = st.columns([1, 1])
        with c1:
            st.markdown(
                f"""
            <div class="light-card">
                <div class="light-card-title">{html.escape(cand['name'])}</div>
                <div class="light-card-meta">{html.escape(cand['role'])} · Match Score: <strong style="color:#0284C7;">{cand['match_score']:.1f}%</strong></div>
                <div style="margin-top:8px;">
                    <strong>Identified Skill Gaps:</strong><br>
                    {' '.join([f'<span class=\"badge badge-missing-req\">{html.escape(s)}</span>' for s in cand['missing_skills']]) or '<span style=\"color:#16A34A;\">None</span>'}
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        with c2:
            st.markdown(
                f"""
            <div class="light-card">
                <div class="light-card-title">Assessment Status: <span style="color:{'#16A34A' if cand['status'] == 'Assessed' else '#0284C7'};">{cand['status']}</span></div>
                <div class="light-card-meta">Current Interview Score: <strong>{cand['assessment_score']:.1f}%</strong></div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        st.markdown('<div class="section-title">Targeted AI Interview Questions</div>', unsafe_allow_html=True)
        if st.button("⚡ Generate Tailored Questions for this Candidate"):
            with st.spinner("Generating targeted questions via AI..."):
                sample_resume = {"experience": [{"title": cand["role"], "company": "Previous Tech Co", "duration": f"{cand['experience_years']} years"}]}
                sample_jd = {"key_responsibilities": ["Develop scalable backend microservices", "Manage cloud deployments"]}
                questions = generate_mock_questions(sample_resume, sample_jd, cand["missing_skills"])
                st.session_state[f"questions_{cand_id}"] = questions

        questions = st.session_state.get(
            f"questions_{cand_id}",
            [
                {
                    "question": f"How have you worked around {cand['missing_skills'][0] if cand['missing_skills'] else 'new technologies'} in previous projects?",
                    "type": "technical",
                    "tests": "Adaptability and willingness to learn missing tools",
                },
                {
                    "question": "Describe a scenario where you resolved a critical production incident under tight deadlines.",
                    "type": "behavioral",
                    "tests": "Problem solving, composure, and communication",
                },
                {
                    "question": f"How does your past experience as {cand['role']} align with managing high-scale system reliability?",
                    "type": "role-fit",
                    "tests": "Domain familiarity and architecture understanding",
                },
            ],
        )

        for idx, q in enumerate(questions, 1):
            st.markdown(
                f"""
            <div class="light-card">
                <span class="badge badge-matched" style="background:#EEF2FF; color:#4F46E5; border-color:#C7D2FE;">{q.get('type', 'General').upper()}</span>
                <div style="font-weight:700; color:#0F172A; margin: 6px 0 4px 0;">{idx}. {html.escape(q.get('question'))}</div>
                <div style="color:#64748B; font-size:0.85rem; font-style:italic;">Evaluates: {html.escape(q.get('tests'))}</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        st.markdown('<div class="section-title">Submit Assessment Score</div>', unsafe_allow_html=True)
        new_score = st.slider("Interview Performance Score (%)", min_value=0.0, max_value=100.0, value=float(cand["assessment_score"]) or 75.0, step=1.0)
        
        if st.button("💾 Save Assessment to Pipeline"):
            db.update_candidate_assessment(cand_id, new_score, status="Assessed")
            st.success(f"Candidate assessment updated to {new_score:.1f}%!")
            st.rerun()


# ==============================================================================
# PAGE 4: RECRUITER DATABASE
# ==============================================================================
elif page == "👥 Recruiter Database":
    st.markdown('<div class="eyebrow">TALENT REPOSITORY</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-title">Recruiter Candidate Database</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="subtitle">Search, filter, inspect, and manage screened candidates stored in the local SQLite database.</div>',
        unsafe_allow_html=True,
    )

    all_cands = db.get_all_candidates()

    col1, col2 = st.columns([2, 1])
    with col1:
        search_query = st.text_input("🔍 Search candidates by name or role", "")
    with col2:
        status_filter = st.selectbox("Filter by Status", ["All", "Screened", "Assessed"])

    filtered_cands = all_cands
    if search_query:
        filtered_cands = [
            c for c in filtered_cands
            if search_query.lower() in c["name"].lower() or search_query.lower() in c["role"].lower()
        ]
    if status_filter != "All":
        filtered_cands = [c for c in filtered_cands if c["status"] == status_filter]

    st.markdown(f"**Showing {len(filtered_cands)} candidates**")

    if filtered_cands:
        table_rows = []
        for c in filtered_cands:
            status_html = (
                '<span class="table-pill-assessed">● Assessed</span>'
                if c["status"] == "Assessed"
                else '<span class="table-pill-screened">● Screened</span>'
            )
            gaps_text = ", ".join(c["missing_skills"]) or "None"
            assess_text = f"<strong>{c['assessment_score']:.1f}%</strong>" if c["status"] == "Assessed" else "<span style='color:#94A3B8;'>Pending</span>"
            table_rows.append([
                f"<span style='color:#64748B;'>#{c['id']}</span>",
                f"<strong>{html.escape(c['name'])}</strong>",
                html.escape(c["role"]),
                f"<span style='color:#0284C7; font-weight:700;'>{c['match_score']:.1f}%</span>",
                f"{c['skill_match']:.0f}%",
                f"{c['experience_years']} yrs",
                html.escape(c["education"]),
                html.escape(gaps_text),
                assess_text,
                status_html,
            ])

        render_light_table(
            headers=["ID", "Candidate", "Role", "Match Score", "Skill Match", "Experience", "Education", "Missing Skills", "Assessment", "Status"],
            rows=table_rows,
        )

        df_export = pd.DataFrame(
            [
                {
                    "ID": c["id"],
                    "Name": c["name"],
                    "Role": c["role"],
                    "Match Score": f"{c['match_score']:.1f}%",
                    "Skill Match": f"{c['skill_match']:.0f}%",
                    "Experience": f"{c['experience_years']} yrs",
                    "Education": c["education"],
                    "Missing Skills": ", ".join(c["missing_skills"]),
                    "Assessment": f"{c['assessment_score']:.1f}%" if c["status"] == "Assessed" else "Pending",
                    "Status": c["status"],
                }
                for c in filtered_cands
            ]
        )

        st.download_button(
            "📥 Export Candidate Pipeline as CSV",
            data=df_export.to_csv(index=False),
            file_name="recruiter_candidate_pipeline.csv",
            mime="text/csv",
        )


# ==============================================================================
# PAGE 5: REPORTS & COMPARISON
# ==============================================================================
elif page == "⚖️ Reports & Comparison":
    st.markdown('<div class="eyebrow">HEAD-TO-HEAD BENCHMARKING</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-title">Candidate Comparison & Benchmarks</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="subtitle">Compare candidate profiles, qualifications, match scores, and interview performance side by side.</div>',
        unsafe_allow_html=True,
    )

    all_cands = db.get_all_candidates()
    if len(all_cands) < 2:
        st.info("Please have at least 2 candidates in the database to run side-by-side comparisons.")
    else:
        cand_map = {f"{c['name']} ({c['role']})": c for c in all_cands}
        selected_cands = st.multiselect(
            "Select 2 to 4 candidates to compare",
            list(cand_map.keys()),
            default=list(cand_map.keys())[:2],
        )

        if len(selected_cands) >= 2:
            comp_data = [cand_map[name] for name in selected_cands]

            # Radar Chart Overlay
            radar = go.Figure()
            colors = ["#0284C7", "#16A34A", "#7C3AED", "#D97706"]
            for idx, c in enumerate(comp_data):
                radar.add_trace(
                    go.Scatterpolar(
                        r=[c["match_score"], c["skill_match"], c["experience_match"], c["education_match"], c["assessment_score"]],
                        theta=["Overall Match", "Skills", "Experience", "Education", "Assessment"],
                        fill="toself",
                        name=c["name"],
                        line=dict(color=colors[idx % len(colors)], width=2),
                    )
                )
            radar.update_layout(
                polar=dict(
                    bgcolor="#FFFFFF",
                    radialaxis=dict(visible=True, range=[0, 100], gridcolor="#F1F5F9"),
                    angularaxis=dict(gridcolor="#F1F5F9"),
                ),
                paper_bgcolor="#FFFFFF",
                font=dict(color="#0F172A"),
                margin=dict(l=20, r=20, t=20, b=20),
                height=350,
            )
            st.plotly_chart(radar, use_container_width=True)

            # Side by side columns
            cols = st.columns(len(comp_data))
            for i, c in enumerate(comp_data):
                with cols[i]:
                    st.markdown(
                        f"""
                    <div class="kpi-card" style="border-top: 4px solid {colors[i % len(colors)]};">
                        <div class="kpi-title">{html.escape(c['name'])}</div>
                        <div class="kpi-num" style="color:{colors[i % len(colors)]};">{c['match_score']:.1f}%</div>
                        <div class="kpi-footer" style="color:#64748B;">{html.escape(c['role'])}</div>
                        <hr style="border-color:#E2E8F0; margin: 12px 0;">
                        <div style="font-size:0.85rem; color:#334155;">
                            <div><strong>Skill Match:</strong> {c['skill_match']:.0f}%</div>
                            <div><strong>Experience:</strong> {c['experience_years']} years</div>
                            <div><strong>Assessment:</strong> {c['assessment_score']:.1f}%</div>
                            <div style="margin-top:6px;"><strong>Missing:</strong><br>{', '.join([html.escape(s) for s in c['missing_skills']]) or 'None'}</div>
                        </div>
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )


# ==============================================================================
# PAGE 6: SETTINGS
# ==============================================================================
elif page == "⚙️ Settings":
    st.markdown('<div class="eyebrow">CONFIGURATION & SYSTEM</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-title">Platform Settings & AI Configuration</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="subtitle">Manage API keys, select default Groq LLM inference models, customize scoring weight ratios, and manage database state.</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-title">Groq Cloud AI Configuration</div>', unsafe_allow_html=True)
    curr_key = get_groq_api_key() or ""
    masked_key = (curr_key[:6] + "..." + curr_key[-4:]) if len(curr_key) > 10 else "Not Configured"
    st.text_input("Active Groq API Key", value=masked_key, disabled=True)
    st.caption("To update your key, edit `.streamlit/secrets.toml` with `GROQ_API_KEY = 'your_key'`.")

    model_option = st.selectbox(
        "Groq LLM Inference Model",
        ["openai/gpt-oss-120b", "llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"],
        index=0,
    )

    st.markdown('<div class="section-title">Database Management</div>', unsafe_allow_html=True)
    if st.button("🔄 Reset Candidate Database to Default Demo Pipeline"):
        db.reset_database()
        st.success("Candidate database has been reset with 10 demo candidates matching the dashboard!")
        st.rerun()