"""
AI-Powered Resume vs. Job Description Matcher & Interview Coach.

A modern, interactive Streamlit web application that delivers real-time
candidate screening, multi-factor match scoring, visual skill gap analytics,
and AI-generated mock interview questions.
"""

import streamlit as st
import plotly.graph_objects as go

from parser import extract_text
from extractor import extract_resume_data, extract_jd_data, get_groq_api_key
from scorer import calculate_match_score
from interview import generate_mock_questions

# ---------- PAGE CONFIGURATION ----------
st.set_page_config(
    page_title="HALO Resume Analyzer | AI Candidate Screening",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- CUSTOM CSS STYLING ----------
st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .stApp { background-color: #f4f6fa; }

    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e5e7eb;
    }
    section[data-testid="stSidebar"] .block-container { padding-top: 1.5rem; }

    .nav-label {
        color: #9ca3af;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 1.2px;
        margin: 1.2rem 0 0.6rem 0;
    }
    .nav-item {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 9px 10px;
        border-radius: 8px;
        font-size: 0.92rem;
        font-weight: 600;
        color: #374151;
        margin-bottom: 2px;
    }
    .nav-item.active {
        background: #ecfeff;
        color: #0e7490;
    }
    .dot { font-size: 0.7rem; }
    .dot.active { color: #06b6d4; }
    .dot.inactive { color: #d1d5db; }

    .status-box {
        border: 1px solid #e5e7eb;
        border-radius: 10px;
        padding: 12px 14px;
        margin-top: 1.5rem;
        font-size: 0.82rem;
        background: #f9fafb;
    }
    .status-title {
        font-weight: 700;
        color: #374151;
        font-size: 0.75rem;
        letter-spacing: 1px;
        margin-bottom: 8px;
    }
    .status-row { display: flex; justify-content: space-between; color: #6b7280; margin-bottom: 4px; }
    .status-val { font-weight: 700; }

    .eyebrow {
        color: #0891b2;
        font-weight: 700;
        font-size: 0.78rem;
        letter-spacing: 1.8px;
        text-transform: uppercase;
        margin-bottom: 6px;
    }
    .main-title {
        font-size: 2.3rem;
        font-weight: 800;
        color: #111827;
        margin-bottom: 6px;
        line-height: 1.2;
    }
    .subtitle {
        color: #6b7280;
        font-size: 1rem;
        margin-bottom: 1.8rem;
    }

    .kpi-card {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 1.1rem 1.2rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    }
    .kpi-label {
        color: #9ca3af;
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.8px;
        text-transform: uppercase;
        margin-bottom: 8px;
    }
    .kpi-value { font-size: 2rem; font-weight: 800; line-height: 1; margin-bottom: 6px; }
    .kpi-sub { font-size: 0.78rem; font-weight: 700; }

    .section-heading {
        font-size: 1.15rem;
        font-weight: 800;
        color: #111827;
        margin: 2rem 0 1rem 0;
    }

    .chart-card {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 1.1rem 1.2rem 0.4rem 1.2rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    }
    .chart-title {
        font-weight: 700;
        color: #111827;
        font-size: 0.92rem;
        margin-bottom: 0.6rem;
    }

    .badge {
        display: inline-block; padding: 5px 13px; border-radius: 999px;
        font-size: 0.82rem; font-weight: 600; margin: 3px 5px 3px 0;
    }
    .badge-matched { background: #dcfce7; color: #15803d; border: 1px solid #86efac; }
    .badge-missing-required { background: #fee2e2; color: #b91c1c; border: 1px solid #fca5a5; }
    .badge-missing-preferred { background: #fef9c3; color: #a16207; border: 1px solid #fde047; }

    .exp-card {
        background: #ffffff; border-left: 4px solid #0891b2; border-radius: 8px;
        padding: 1rem 1.2rem; margin-bottom: 0.8rem; border-top: 1px solid #e5e7eb;
        border-right: 1px solid #e5e7eb; border-bottom: 1px solid #e5e7eb;
    }
    .exp-title { font-weight: 700; color: #111827; font-size: 1rem; }
    .exp-meta { color: #6b7280; font-size: 0.85rem; margin-bottom: 0.4rem; }

    .question-card {
        background: #ffffff; border: 1px solid #e5e7eb; border-radius: 12px;
        padding: 1.2rem 1.4rem; margin-bottom: 1rem; box-shadow: 0 1px 2px rgba(0,0,0,0.04);
    }
    .q-type {
        display: inline-block; font-size: 0.7rem; font-weight: 700; text-transform: uppercase;
        letter-spacing: 0.5px; padding: 3px 10px; border-radius: 999px; margin-bottom: 0.5rem;
    }
    .q-type-technical { background: #e0e7ff; color: #4338ca; }
    .q-type-behavioral { background: #fce7f3; color: #be185d; }
    .q-type-role-fit { background: #dcfce7; color: #15803d; }
    .q-type-error { background: #fee2e2; color: #b91c1c; }
    .q-text { font-size: 1rem; font-weight: 600; color: #111827; margin-bottom: 0.3rem; }
    .q-tests { color: #6b7280; font-size: 0.85rem; font-style: italic; }

    .stButton>button {
        background: linear-gradient(90deg, #0891b2, #6366f1);
        color: white; font-weight: 700; border: none; border-radius: 10px;
        padding: 0.65rem 2.2rem; font-size: 1rem;
    }
    .stButton>button:hover { color: white; opacity: 0.92; }

    div[data-testid="stMetricValue"] { color: #111827; }
</style>
""",
    unsafe_allow_html=True,
)

# ---------- SIDEBAR NAVIGATION & STATUS ----------
with st.sidebar:
    st.markdown("### 🧭 HALO Resume Analyzer")
    st.caption("AI-powered candidate screening & evaluation")
    st.markdown('<div class="nav-label">PLATFORM NAVIGATION</div>', unsafe_allow_html=True)
    st.markdown('<div class="nav-item active"><span class="dot active">●</span> Candidate Matcher</div>', unsafe_allow_html=True)
    st.markdown('<div class="nav-item"><span class="dot inactive">○</span> Skill Gap Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="nav-item"><span class="dot inactive">○</span> Mock Interview Coach</div>', unsafe_allow_html=True)

    has_api_key = bool(get_groq_api_key())
    status_color = "#16a34a" if has_api_key else "#dc2626"
    status_text = "Online" if has_api_key else "Missing Key"

    st.markdown(
        f"""
    <div class="status-box">
        <div class="status-title">SYSTEM STATUS</div>
        <div class="status-row"><span>AI Engine</span><span class="status-val" style="color:#0891b2;">Groq Cloud</span></div>
        <div class="status-row"><span>LLM Model</span><span class="status-val">gpt-oss-120b</span></div>
        <div class="status-row"><span>Embedding</span><span class="status-val">all-MiniLM-L6-v2</span></div>
        <div class="status-row"><span>Status</span><span class="status-val" style="color:{status_color};">{status_text}</span></div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    if not has_api_key:
        st.warning("⚠️ Groq API key is not detected. Please add it to `.streamlit/secrets.toml`.")

# ---------- MAIN HEADER ----------
st.markdown('<div class="eyebrow">RECRUITER & CANDIDATE COMMAND CENTER</div>', unsafe_allow_html=True)
st.markdown('<div class="main-title">Resume vs. Job Description Analyzer</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Real-time match scoring, granular skill gap breakdown, and AI-generated interview questions.</div>',
    unsafe_allow_html=True,
)

# ---------- UPLOAD SECTION ----------
col1, col2 = st.columns(2)
with col1:
    st.markdown("**📎 Upload Candidate Resume**")
    resume_file = st.file_uploader(
        "Upload Resume",
        type=["pdf", "docx", "txt"],
        label_visibility="collapsed",
        key="resume_uploader",
    )
    if resume_file:
        st.caption(f"Loaded: `{resume_file.name}` ({resume_file.size / 1024:.1f} KB)")

with col2:
    st.markdown("**💼 Job Description**")
    jd_file = st.file_uploader(
        "Upload Job Description",
        type=["pdf", "docx", "txt"],
        label_visibility="collapsed",
        key="jd_uploader",
    )
    jd_text_input = st.text_area(
        "Paste Job Description text here if not uploading a file:",
        height=100,
        placeholder="Paste JD requirements, responsibilities, and qualifications here...",
    )

st.write("")
analyze_clicked = st.button("✨ Analyze Match & Generate Questions", type="primary")

# ---------- PROCESSING LOGIC ----------
if analyze_clicked:
    if not resume_file:
        st.error("❌ Please upload a candidate resume to proceed.")
        st.stop()
    if not jd_file and not jd_text_input.strip():
        st.error("❌ Please upload a job description file or paste the job description text.")
        st.stop()
    if not get_groq_api_key():
        st.error("❌ Groq API key is missing. Please set `GROQ_API_KEY` in `.streamlit/secrets.toml` or environment variables.")
        st.stop()

    with st.spinner("📄 Step 1/4: Extracting text from documents..."):
        try:
            resume_text = extract_text(resume_file)
            jd_text = extract_text(jd_file) if jd_file else jd_text_input.strip()
        except Exception as e:
            st.error(f"Text extraction failed: {e}")
            st.stop()

    with st.spinner("🧠 Step 2/4: Parsing structured entities with Groq AI..."):
        try:
            resume_data = extract_resume_data(resume_text)
            jd_data = extract_jd_data(jd_text)
        except Exception as e:
            st.error(f"Information extraction failed: {e}")
            st.stop()

    with st.spinner("📊 Step 3/4: Calculating weighted multi-factor match score..."):
        try:
            result = calculate_match_score(resume_data, jd_data, resume_text, jd_text)
        except Exception as e:
            st.error(f"Scoring calculation failed: {e}")
            st.stop()

    with st.spinner("🗣️ Step 4/4: Generating tailored mock interview questions..."):
        try:
            questions = generate_mock_questions(
                resume_data, jd_data, result["skill_gap"]["missing_required"]
            )
        except Exception as e:
            questions = [{"question": f"Question generation error: {e}", "type": "error", "tests": ""}]

    # Cache state
    st.session_state["resume_data"] = resume_data
    st.session_state["jd_data"] = jd_data
    st.session_state["result"] = result
    st.session_state["questions"] = questions

# ---------- SCREENING RESULTS DISPLAY ----------
if "result" in st.session_state:
    result = st.session_state["result"]
    resume_data = st.session_state["resume_data"]
    jd_data = st.session_state["jd_data"]
    questions = st.session_state["questions"]

    gap = result["skill_gap"]
    b = result["breakdown"]
    score = float(result["final_score"])

    score_color = "#16a34a" if score >= 70 else ("#ca8a04" if score >= 45 else "#dc2626")
    total_gaps = len(gap["missing_required"]) + len(gap["missing_preferred"])

    st.markdown('<div class="section-heading">Screening Overview & Key Metrics</div>', unsafe_allow_html=True)

    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        st.markdown(
            f'<div class="kpi-card"><div class="kpi-label">Overall Match</div>'
            f'<div class="kpi-value" style="color:{score_color}">{score:.0f}%</div>'
            f'<div class="kpi-sub" style="color:{score_color}">Weighted Score</div></div>',
            unsafe_allow_html=True,
        )
    with k2:
        st.markdown(
            f'<div class="kpi-card"><div class="kpi-label">Skill Match</div>'
            f'<div class="kpi-value" style="color:#4338ca">{b["skill_match"]:.0f}%</div>'
            f'<div class="kpi-sub" style="color:#4338ca">Required Skills</div></div>',
            unsafe_allow_html=True,
        )
    with k3:
        st.markdown(
            f'<div class="kpi-card"><div class="kpi-label">Experience</div>'
            f'<div class="kpi-value" style="color:#0891b2">{b["experience_match"]:.0f}%</div>'
            f'<div class="kpi-sub" style="color:#0891b2">Years Alignment</div></div>',
            unsafe_allow_html=True,
        )
    with k4:
        st.markdown(
            f'<div class="kpi-card"><div class="kpi-label">Education</div>'
            f'<div class="kpi-value" style="color:#16a34a">{b["education_match"]:.0f}%</div>'
            f'<div class="kpi-sub" style="color:#16a34a">Degree Requirement</div></div>',
            unsafe_allow_html=True,
        )
    with k5:
        st.markdown(
            f'<div class="kpi-card"><div class="kpi-label">Skill Gaps</div>'
            f'<div class="kpi-value" style="color:#dc2626">{total_gaps}</div>'
            f'<div class="kpi-sub" style="color:#dc2626">Total Missing</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="section-heading">Visual Analytics & Distribution</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)

    plotly_layout = dict(
        height=260,
        margin=dict(l=10, r=10, t=10, b=10),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="Inter", color="#111827", size=12),
    )

    with c1:
        st.markdown('<div class="chart-card"><div class="chart-title">Weighted Score Breakdown</div>', unsafe_allow_html=True)
        categories = ["Skills (50%)", "Experience (25%)", "Education (15%)", "Semantic (10%)"]
        values = [b["skill_match"], b["experience_match"], b["education_match"], b["semantic_similarity"]]
        fig = go.Figure(
            go.Bar(
                x=categories,
                y=values,
                marker_color=["#0891b2", "#6366f1", "#16a34a", "#ec4899"],
                text=[f"{v:.0f}%" for v in values],
                textposition="outside",
            )
        )
        fig.update_layout(
            **plotly_layout,
            yaxis=dict(range=[0, 115], gridcolor="#f1f5f9", tickfont=dict(color="#374151")),
            xaxis=dict(showgrid=False, tickfont=dict(color="#111827", size=11)),
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="chart-card"><div class="chart-title">Missing Skills Breakdown</div>', unsafe_allow_html=True)
        missing_all = gap["missing_required"] + gap["missing_preferred"]
        if missing_all:
            colors = ["#dc2626"] * len(gap["missing_required"]) + ["#ca8a04"] * len(gap["missing_preferred"])
            fig2 = go.Figure(
                go.Bar(
                    x=[1] * len(missing_all),
                    y=missing_all,
                    orientation="h",
                    marker_color=colors,
                )
            )
            fig2.update_layout(
                **plotly_layout,
                xaxis=dict(visible=False),
                yaxis=dict(gridcolor="#f1f5f9", tickfont=dict(color="#111827", size=12)),
            )
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.success("🎉 No missing skills detected! Candidate possesses all required and preferred skills.")
        st.markdown("</div>", unsafe_allow_html=True)

    with c3:
        st.markdown('<div class="chart-card"><div class="chart-title">Matched vs. Missing Skills Ratio</div>', unsafe_allow_html=True)
        fig3 = go.Figure(
            go.Pie(
                labels=["Matched", "Missing Required", "Missing Preferred"],
                values=[
                    len(gap["matched"]),
                    len(gap["missing_required"]),
                    len(gap["missing_preferred"]),
                ],
                marker_colors=["#16a34a", "#dc2626", "#ca8a04"],
                hole=0.55,
            )
        )
        fig3.update_layout(
            **plotly_layout,
            showlegend=True,
            legend=dict(orientation="h", y=-0.15, font=dict(size=10, color="#111827")),
        )
        fig3.update_traces(textfont=dict(color="white", size=12))
        st.plotly_chart(fig3, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ---------- TABBED DETAILS ----------
    tab1, tab2, tab3 = st.tabs(["🧠 Extracted Profile", "🎯 Skill Gap Deep Dive", "🗣️ Mock Interview Coach"])

    with tab1:
        st.markdown('<div class="section-heading" style="font-size:0.95rem;">🛠️ Extracted Candidate Skills</div>', unsafe_allow_html=True)
        skills = resume_data.get("skills", [])
        if skills:
            skills_html = "".join([f'<span class="badge badge-matched">{s}</span>' for s in skills])
            st.markdown(skills_html, unsafe_allow_html=True)
        else:
            st.info("No explicit skill list extracted.")

        st.markdown('<div class="section-heading" style="font-size:0.95rem;">🎓 Education History</div>', unsafe_allow_html=True)
        education_list = resume_data.get("education", [])
        if education_list:
            for edu in education_list:
                st.markdown(
                    f'<div class="exp-card"><div class="exp-title">{edu.get("degree", "Degree Not Specified")}</div>'
                    f'<div class="exp-meta">{edu.get("institution", "Institution")} · {edu.get("year", "Year N/A")}</div></div>',
                    unsafe_allow_html=True,
                )
        else:
            st.info("No formal education history detected.")

        st.markdown('<div class="section-heading" style="font-size:0.95rem;">💼 Work Experience</div>', unsafe_allow_html=True)
        experience_list = resume_data.get("experience", [])
        if experience_list:
            for exp in experience_list:
                st.markdown(
                    f'<div class="exp-card"><div class="exp-title">{exp.get("title", "Position")}</div>'
                    f'<div class="exp-meta">{exp.get("company", "Company")} · {exp.get("duration", "Duration N/A")}</div>'
                    f'<div style="color:#374151; font-size:0.9rem;">{exp.get("description", "")}</div></div>',
                    unsafe_allow_html=True,
                )
        else:
            st.info("No structured work experience detected.")

    with tab2:
        st.markdown('<div class="section-heading" style="font-size:0.95rem;">✅ Matched Skills</div>', unsafe_allow_html=True)
        if gap["matched"]:
            html_matched = "".join([f'<span class="badge badge-matched">{s}</span>' for s in gap["matched"]])
            st.markdown(html_matched, unsafe_allow_html=True)
        else:
            st.markdown("*None identified*", unsafe_allow_html=True)

        st.markdown('<div class="section-heading" style="font-size:0.95rem;">❌ Missing Required Skills</div>', unsafe_allow_html=True)
        if gap["missing_required"]:
            html_req = "".join([f'<span class="badge badge-missing-required">{s}</span>' for s in gap["missing_required"]])
            st.markdown(html_req, unsafe_allow_html=True)
        else:
            st.markdown("*None — excellent fit! All required skills matched.*", unsafe_allow_html=True)

        st.markdown('<div class="section-heading" style="font-size:0.95rem;">⚠️ Missing Preferred Skills</div>', unsafe_allow_html=True)
        if gap["missing_preferred"]:
            html_pref = "".join([f'<span class="badge badge-missing-preferred">{s}</span>' for s in gap["missing_preferred"]])
            st.markdown(html_pref, unsafe_allow_html=True)
        else:
            st.markdown("*None missing*", unsafe_allow_html=True)

    with tab3:
        st.markdown('<div class="section-heading" style="font-size:0.95rem;">🎯 Tailored AI Interview Questions</div>', unsafe_allow_html=True)
        for i, q in enumerate(questions, 1):
            raw_type = q.get("type", "technical").lower()
            qtype = raw_type.replace(" ", "-")
            if qtype not in ["technical", "behavioral", "role-fit", "error"]:
                qtype = "technical"

            st.markdown(
                f"""
            <div class="question-card">
                <span class="q-type q-type-{qtype}">{q.get('type', 'Technical')}</span>
                <div class="q-text">{i}. {q.get('question', '')}</div>
                <div class="q-tests"><strong>Evaluation Goal:</strong> {q.get('tests', 'Assess candidate competency')}</div>
            </div>
            """,
                unsafe_allow_html=True,
            )