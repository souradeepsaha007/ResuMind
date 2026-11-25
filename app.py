from llm_analyzer import analyze_resume
import json
import re
import tempfile
from pathlib import Path
from datetime import datetime
from io import BytesIO
from xml.sax.saxutils import escape

import streamlit as st
import pymupdf
import plotly.graph_objects as go

from llm_analyzer import analyze_resume
from ai_engine.resume_observer import SKILL_DATABASE


# ==========================================================
# 1. PAGE CONFIGURATION
# ==========================================================

st.set_page_config(
    page_title="Resumind AI — Resume Intelligence",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ==========================================================
# 2. DESIGN SYSTEM
# ==========================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@500;600;700&family=Instrument+Serif:ital,wght@0,400;1,400&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

:root {
    --bg: #F3F0E8;
    --ink: #151515;
    --blue: #4263EB;
    --muted: #777777;
    --navy: #071522;
}

html, body, .stApp {
    background-color: var(--bg) !important;
    color: var(--ink) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

.block-container {
    max-width: 1220px;
    padding-top: 1.5rem;
    padding-bottom: 4rem;
}

header[data-testid="stHeader"] {
    background: transparent;
}

#MainMenu, footer {
    visibility: hidden;
}

.brand {
    font-family: 'Cinzel', serif;
    font-size: 21px;
    font-weight: 700;
    letter-spacing: .15em;
}

.brand span {
    color: var(--blue);
}

.hero {
    text-align: center;
    padding: 55px 10px 30px;
}

.hero-tag {
    display: inline-block;
    background: white;
    border: 1px solid #dce2fa;
    border-radius: 30px;
    padding: 8px 18px;
    color: var(--blue);
    font-size: 11px;
    font-weight: 700;
    letter-spacing: .12em;
}

.hero h1 {
    font-family: 'Instrument Serif', Georgia, serif;
    font-size: clamp(42px, 7vw, 72px);
    line-height: 1.1;
    font-weight: 400;
    margin: 25px 0 15px;
}

.hero h1 em {
    color: var(--blue);
}

.hero p {
    max-width: 690px;
    margin: auto;
    color: #666;
    font-size: 16px;
    line-height: 1.8;
}

.section-heading {
    font-family: 'Instrument Serif', Georgia, serif;
    font-size: 37px;
    margin: 30px 0 12px;
}

.section-tag {
    color: var(--blue);
    font-size: 11px;
    font-weight: 700;
    letter-spacing: .15em;
}

.feature-card {
    background: white;
    border: 1px solid rgba(21,21,21,.08);
    border-radius: 22px;
    padding: 25px;
    min-height: 180px;
    margin-bottom: 15px;
}

.feature-card h3 {
    font-size: 17px;
    margin-bottom: 10px;
}

.feature-card p {
    font-size: 13px;
    color: #777;
    line-height: 1.7;
}

.stButton > button {
    background: #151515 !important;
    color: white !important;
    border: 1px solid #151515 !important;
    border-radius: 999px !important;
    min-height: 46px;
    font-weight: 600;
    letter-spacing: .04em;
}

.stButton > button:hover {
    background: var(--blue) !important;
    border-color: var(--blue) !important;
}

.stDownloadButton > button {
    background: var(--blue) !important;
    color: white !important;
    border-radius: 999px !important;
    border: none !important;
}

div[data-testid="stFileUploader"] {
    background: white;
    border: 2px dashed #c8d1f5;
    border-radius: 20px;
    padding: 20px;
}

div[data-testid="stMetric"] {
    background: white;
    border: 1px solid rgba(21,21,21,.08);
    border-radius: 18px;
    padding: 20px;
}

div[data-testid="stMetricValue"] {
    font-family: 'Instrument Serif', Georgia, serif;
}

div[data-baseweb="textarea"] {
    background: white;
    border-radius: 16px;
}

.result-card {
    background: white;
    border: 1px solid rgba(21,21,21,.08);
    border-radius: 22px;
    padding: 25px;
    margin: 15px 0;
}

.skill-tag {
    display: inline-block;
    background: #edf0ff;
    color: #344fc5;
    border: 1px solid #d9e0ff;
    border-radius: 30px;
    padding: 6px 13px;
    margin: 4px;
    font-size: 12px;
    font-weight: 600;
}

.missing-tag {
    display: inline-block;
    background: #fff1e5;
    color: #995000;
    border: 1px solid #ffe0bd;
    border-radius: 30px;
    padding: 6px 13px;
    margin: 4px;
    font-size: 12px;
    font-weight: 600;
}

.footer {
    border-top: 1px solid rgba(21,21,21,.1);
    text-align: center;
    padding: 35px 0 10px;
    margin-top: 60px;
    color: #777;
    font-size: 12px;
}
</style>
""", unsafe_allow_html=True)


# ==========================================================
# 3. SESSION STATE
# ==========================================================

if "page" not in st.session_state:
    st.session_state.page = "Home"

if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None


# ==========================================================
# 4. PDF TEXT EXTRACTION
# ==========================================================

def extract_pdf_text(uploaded_file):

    pdf_bytes = uploaded_file.getvalue()
    text_parts = []

    with pymupdf.open(
        stream=pdf_bytes,
        filetype="pdf"
    ) as document:

        for page in document:
            # Sort text in logical reading order
            page_text = page.get_text("text", sort=True)
            if not page_text or len(page_text.strip()) < 15:
                blocks = page.get_text("blocks")
                page_text = "\n".join(b[4] for b in blocks if len(b) > 4 and str(b[4]).strip())
            if page_text.strip():
                text_parts.append(page_text)

    raw_text = "\n".join(text_parts)
    raw_text = raw_text.replace("\xa0", " ").replace("\x00", " ")
    return raw_text.strip()


# ==========================================================
# 5. CANDIDATE INFORMATION
# ==========================================================

def extract_candidate_information(text):

    email_match = re.search(
        r'\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b',
        text
    )

    phone_match = re.search(
        r'(?:\+?\d{1,3}[\s.-]?)?(?:\(?\d{2,5}\)?[\s.-]?)?\d{3,5}[\s.-]?\d{4,5}',
        text
    )

    linkedin_match = re.search(
        r'(?:https?://)?(?:www\.)?linkedin\.com/(?:in|pub)/[a-zA-Z0-9_\-]+',
        text,
        re.IGNORECASE
    )

    github_match = re.search(
        r'(?:https?://)?(?:www\.)?github\.com/[a-zA-Z0-9_\-]+',
        text,
        re.IGNORECASE
    )

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    candidate_name = "Candidate"

    excluded_words = [
        "resume", "curriculum vitae", "cv", "email",
        "phone", "mobile", "linkedin", "github",
        "portfolio", "address", "profile", "summary",
        "objective", "education", "experience", "skills",
        "developer", "engineer"
    ]

    for line in lines[:10]:
        clean_line = re.sub(r'^[•*|✦\s\d\.-]+', '', line).strip()
        words = clean_line.split()
        if (
            1 <= len(words) <= 4
            and len(clean_line) <= 45
            and not re.search(r'[@\d:/\\{}<>]', clean_line)
            and not any(word in clean_line.lower() for word in excluded_words)
            and any(c.isalpha() for c in clean_line)
        ):
            candidate_name = clean_line
            break

    phone_str = "Not found"
    if phone_match:
        digits = re.sub(r'\D', '', phone_match.group(0))
        if 10 <= len(digits) <= 13:
            phone_str = phone_match.group(0).strip()

    return {
        "name": candidate_name,
        "email": (
            email_match.group(0)
            if email_match else "Not found"
        ),
        "phone": phone_str,
        "linkedin": linkedin_match.group(0) if linkedin_match else "",
        "github": github_match.group(0) if github_match else ""
    }


# ==========================================================
# 6. JOB DESCRIPTION SKILL EXTRACTION
# ==========================================================

def extract_job_skills(job_description):

    found = []

    for category, skills in SKILL_DATABASE.items():

        for skill in skills:

            pattern = (
                r"(?<![a-zA-Z0-9])"
                + re.escape(skill)
                + r"(?![a-zA-Z0-9])"
            )

            if re.search(
                pattern,
                job_description,
                re.IGNORECASE
            ):
                found.append(skill)

    return list(dict.fromkeys(found))


# ==========================================================
# 7. JOB MATCHING
# ==========================================================

def calculate_job_match(resume_result, job_description):

    resume_skills = []
    for category_skills in resume_result.get("skills", {}).values():
        for skill in category_skills:
            if skill not in resume_skills:
                resume_skills.append(skill)

    # Merge verified skills from trained PyTorch SkillNet
    for pred in resume_result.get("trained_skill_predictions", []):
        if pred.get("predicted_present") and pred.get("skill") not in resume_skills:
            resume_skills.append(pred["skill"])

    required_skills = extract_job_skills(job_description)

    resume_set = {
        skill.lower() for skill in resume_skills
    }

    matched = [
        skill for skill in required_skills
        if skill.lower() in resume_set
    ]

    missing = [
        skill for skill in required_skills
        if skill.lower() not in resume_set
    ]

    if required_skills:

        score = round(
            len(matched) / len(required_skills) * 100,
            2
        )

    else:
        score = None

    return {
        "resume_skills": resume_skills,
        "required_skills": required_skills,
        "matched_skills": matched,
        "missing_skills": missing,
        "match_score": score
    }


# ==========================================================
# 8. PDF REPORT GENERATOR
# ==========================================================

def create_pdf_report(result):

    try:

        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import (
            SimpleDocTemplate,
            Paragraph,
            Spacer
        )
        from reportlab.lib.styles import getSampleStyleSheet

        buffer = BytesIO()

        document = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40
        )

        styles = getSampleStyleSheet()

        story = []

        story.append(
            Paragraph(
                "<b>RESUMIND AI</b>",
                styles["Title"]
            )
        )

        story.append(
            Paragraph(
                "Resumind AI - Executive Career & Skills Analysis Report",
                styles["Heading2"]
            )
        )

        story.append(Spacer(1, 18))

        candidate = result["candidate"]
        analysis = result["soura_result"]
        matching = result["match_data"]

        for label, value in [
            ("Candidate", candidate["name"]),
            ("Email", candidate["email"]),
            ("Phone", candidate["phone"]),
            ("Career category", analysis["resume_category"])
        ]:

            story.append(
                Paragraph(
                    f"<b>{label}:</b> {escape(str(value))}",
                    styles["Normal"]
                )
            )

        story.append(Spacer(1, 15))

        if matching["match_score"] is not None:

            story.append(
                Paragraph(
                    f"<b>Job skill overlap:</b> "
                    f"{matching['match_score']:.1f}%",
                    styles["Heading2"]
                )
            )

        def add_section(title, content):

            story.append(
                Paragraph(title, styles["Heading2"])
            )

            if isinstance(content, dict):

                for category, values in content.items():

                    story.append(
                        Paragraph(
                            f"<b>{escape(str(category))}:</b> "
                            f"{escape(', '.join(map(str, values)))}",
                            styles["Normal"]
                        )
                    )

            elif isinstance(content, list):

                for item in content:

                    story.append(
                        Paragraph(
                            escape(str(item)),
                            styles["Normal"]
                        )
                    )

            elif content:

                for line in str(content).splitlines():

                    if line.strip():

                        story.append(
                            Paragraph(
                                escape(line),
                                styles["Normal"]
                            )
                        )

            else:

                story.append(
                    Paragraph(
                        "No information detected.",
                        styles["Normal"]
                    )
                )

            story.append(Spacer(1, 10))

        add_section(
            "Professional Summary",
            analysis["professional_summary"]
        )

        add_section(
            "Education",
            analysis["education"]["section_text"]
        )

        add_section(
            "Work Experience",
            analysis["experience"]["section_text"]
        )

        add_section(
            "Detected Skills",
            analysis["skills"]
        )

        add_section(
            "Projects",
            analysis["projects"]
        )

        add_section(
            "Certifications",
            analysis["certifications"]
        )

        add_section(
            "Achievements",
            analysis["achievements"]
        )

        add_section(
            "Matched Skills",
            matching["matched_skills"]
        )

        add_section(
            "Missing Skills",
            matching["missing_skills"]
        )

        story.append(
            Paragraph(
                "<i>This report contains automated resume observations. "
                "Please verify extracted information.</i>",
                styles["Italic"]
            )
        )

        document.build(story)

        buffer.seek(0)

        return buffer.getvalue()

    except ImportError:
        return None


# ==========================================================
# 9. NAVIGATION
# ==========================================================

nav1, nav2, nav3 = st.columns([2.5, 1, 1])

with nav1:

    st.markdown(
        '<div class="brand">RESUMIND <span>AI</span></div>',
        unsafe_allow_html=True
    )

with nav2:

    if st.button("HOME", use_container_width=True):

        st.session_state.page = "Home"
        st.rerun()

with nav3:

    if st.button("ANALYSER", use_container_width=True):

        st.session_state.page = "Analysis"
        st.rerun()


# ==========================================================
# 10. HOMEPAGE
# ==========================================================

if st.session_state.page == "Home":

    st.markdown(
        '<div class="hero">'
        '<span class="hero-tag">✦ RESUMIND AI ENGINE</span>'
        '<h1>A sharper resume.<br><em>Your next defining role.</em></h1>'
        '<p>Analyse your professional experience, discover your strengths and understand how your qualifications align with your next career opportunity. Supporting IT and non-IT resume analysis.</p>'
        '</div>',
        unsafe_allow_html=True
    )

    center1, center2, center3 = st.columns([1, 1.5, 1])

    with center2:

        if st.button(
            "ANALYSE MY RESUME →",
            use_container_width=True
        ):

            st.session_state.page = "Analysis"
            st.rerun()

    st.markdown(
        '<div class="section-heading">Core Capabilities</div>',
        unsafe_allow_html=True
    )

    c1, c2, c3 = st.columns(3)

    cards = [
        (
            "01",
            "Resume Observation",
            "Extract contact information, education, employment, skills and other resume sections."
        ),
        (
            "02",
            "Industry Recognition",
            "Identify common IT, non-IT and hybrid professional skill categories."
        ),
        (
            "03",
            "Job Compatibility",
            "Compare detected resume skills against an optional job description."
        ),
        (
            "04",
            "Neural SkillNet",
            "Use your custom PyTorch neural model trained on your RTX 2050 GPU."
        ),
        (
            "05",
            "Resume Diagnostics",
            "Review missing sections, qualifications and actionable suggestions."
        ),
        (
            "06",
            "Executive Reporting",
            "Export a professional structured PDF career analysis report."
        )
    ]

    for index, (number, title, description) in enumerate(cards):

        with [c1, c2, c3][index % 3]:

            st.markdown(
                f'<div class="feature-card">'
                f'<span class="section-tag">MODULE {number}</span>'
                f'<h3>{title}</h3>'
                f'<p>{description}</p>'
                f'</div>',
                unsafe_allow_html=True
            )

    st.markdown(
        '<div class="footer">'
        '<div class="brand">RESUMIND <span>AI</span></div>'
        'Your Resume. Your Skills. Your Next Opportunity.<br>'
        '&copy; 2026 Resumind AI'
        '</div>',
        unsafe_allow_html=True
    )


# ==========================================================
# 11. ANALYSIS PAGE
# ==========================================================

if st.session_state.page == "Analysis":

    st.markdown(
        '<div class="hero">'
        '<span class="hero-tag">RESUME EVALUATION STUDIO</span>'
        '<h1>Resume Analysis<br><em>Studio</em></h1>'
        '<p>Upload your PDF resume. Resumind AI will inspect your professional background, identify skills and organise your career information.</p>'
        '</div>',
        unsafe_allow_html=True
    )

    input1, input2 = st.columns([1, 1])

    with input1:

        uploaded_file = st.file_uploader(
            "Upload Resume PDF",
            type=["pdf"],
            help="Upload a text-based PDF resume."
        )

        if uploaded_file:

            st.success(
                f"Resume loaded: {uploaded_file.name}"
            )

    with input2:

        job_description = st.text_area(
            "Target Job Description (Optional)",
            placeholder=(
                "Paste the job description here if you "
                "want a resume-to-job comparison..."
            ),
            height=180
        )

    analyse_button = st.button(
        "ANALYSE RESUME →",
        type="primary",
        use_container_width=True
    )

    if analyse_button:

        st.session_state.analysis_result = None

        if uploaded_file is None:

            st.error("Please upload a resume PDF.")

        else:

            try:

                with st.spinner(
                    "Resumind AI is analysing your resume..."
                ):

                    # Extract text for candidate information
                    resume_text = extract_pdf_text(uploaded_file)

                    if not resume_text:

                        raise ValueError(
                            "No readable text found in this PDF. "
                            "Scanned PDFs require OCR."
                        )

                    candidate = extract_candidate_information(
                        resume_text
                    )

                    # Save uploaded file temporarily
                    with tempfile.NamedTemporaryFile(
                        suffix=".pdf",
                        delete=False
                    ) as temp_file:

                        temp_file.write(
                            uploaded_file.getvalue()
                        )

                        temp_pdf_path = Path(temp_file.name)

                    try:

                        # Run Resumind AI Engine
                        soura_result = analyze_resume(
                            temp_pdf_path,
                            job_description
                        )

                    finally:

                        temp_pdf_path.unlink(
                            missing_ok=True
                        )

                    # Sync candidate details into personal_information
                    if candidate and isinstance(candidate, dict):
                        if not soura_result.get("personal_information"):
                            soura_result["personal_information"] = candidate
                        else:
                            for k, v in candidate.items():
                                curr_v = soura_result["personal_information"].get(k)
                                if v and (not curr_v or curr_v in ("Candidate", "Not found", [])):
                                    soura_result["personal_information"][k] = v

                    # Optional job matching
                    if job_description.strip():

                        match_data = calculate_job_match(
                            soura_result,
                            job_description
                        )

                    else:

                        all_skills = [
                            skill
                            for values in soura_result.get("skills", {}).values()
                            for skill in values
                        ]
                        for pred in soura_result.get("trained_skill_predictions", []):
                            if pred.get("predicted_present") and pred.get("skill") not in all_skills:
                                all_skills.append(pred["skill"])

                        match_data = {
                            "resume_skills": all_skills,
                            "required_skills": [],
                            "matched_skills": [],
                            "missing_skills": [],
                            "match_score": None
                        }

                    # Save result
                    st.session_state.analysis_result = {
                        "candidate": candidate,
                        "soura_result": soura_result,
                        "match_data": match_data,
                        "filename": uploaded_file.name,
                        "created_at": datetime.now().strftime(
                            "%d %b %Y, %I:%M %p"
                        )
                    }

                st.success(
                    "Resumind AI analysis completed!"
                )

            except Exception as error:

                st.error(
                    f"Analysis failed: {type(error).__name__}: {error}"
                )

                st.exception(error)


# ==========================================================
# 12. ANALYSIS DASHBOARD
# ==========================================================

result = st.session_state.analysis_result

if (
    st.session_state.page == "Analysis"
    and result is not None
):

    candidate = result["candidate"]
    data = result["soura_result"]
    match = result["match_data"]

    st.divider()

    st.markdown(
        '<span class="section-tag">CAREER AUDIT</span>'
        '<div class="section-heading">Candidate Profile</div>',
        unsafe_allow_html=True
    )

    p1, p2, p3 = st.columns(3)

    with p1:
        st.metric("Candidate", candidate["name"])

    with p2:
        st.metric("Email", candidate["email"])

    with p3:
        st.metric("Phone", candidate["phone"])

    st.caption(
        f"File: {result['filename']} | "
        f"Analysed: {result['created_at']}"
    )

    st.markdown(
        f"**Career category:** {data['resume_category']}"
    )

    st.caption(
        f"Analysis engine: {data['engine']} | "
        f"Model status: {data.get('trained_model_status', 'Not available')}"
    )

    # ------------------------------------------------------
    # JOB MATCHING
    # ------------------------------------------------------

    st.divider()

    st.markdown(
        '<span class="section-tag">JOB COMPATIBILITY</span>'
        '<div class="section-heading">Skills Match Analysis</div>',
        unsafe_allow_html=True
    )

    if match["match_score"] is not None:

        score1, score2, score3 = st.columns(3)

        with score1:

            st.metric(
                "Skill Overlap",
                f"{match['match_score']:.1f}%"
            )

        with score2:

            st.metric(
                "Matched Skills",
                len(match["matched_skills"])
            )

        with score3:

            st.metric(
                "Missing Skills",
                len(match["missing_skills"])
            )

        st.progress(
            min(100, max(0, int(round(float(match["match_score"]))))),
            text="Percentage of recognised job skills found in the resume"
        )

        st.caption(
            "This is a keyword-based skill overlap measure, "
            "not a validated hiring probability or ATS score."
        )

    else:

        info_c1, info_c2 = st.columns([2.5, 1])
        with info_c1:
            st.info(
                "💡 **No Target Job Description Provided** — General resume analysis and neural skill predictions are displayed below. "
                "Paste a job description in the analysis studio to calculate real-time match percentage, keyword gaps, and ATS alignment."
            )
        with info_c2:
            st.metric("Target Job Status", "Awaiting Job Desc")

    # ------------------------------------------------------
    # MATCHED AND MISSING SKILLS
    # ------------------------------------------------------

    if match["required_skills"]:

        s1, s2 = st.columns(2)

        with s1:

            st.markdown("### Matched Skills")

            if match["matched_skills"]:

                tags = "".join(
                    f'<span class="skill-tag">✓ {escape(str(skill))}</span>'
                    for skill in match["matched_skills"]
                )

                st.markdown(tags, unsafe_allow_html=True)

            else:

                st.info("No matching skills identified.")

        with s2:

            st.markdown("### Missing Skills")

            if match["missing_skills"]:

                tags = "".join(
                    f'<span class="missing-tag">✕ {escape(str(skill))}</span>'
                    for skill in match["missing_skills"]
                )

                st.markdown(tags, unsafe_allow_html=True)

            else:

                st.success("All recognised job skills were found.")

        # Skill chart
        chart = go.Figure()

        chart.add_trace(
            go.Bar(
                name="Matched",
                x=["Job Skills"],
                y=[len(match["matched_skills"])],
                marker_color="#4263EB"
            )
        )

        chart.add_trace(
            go.Bar(
                name="Missing",
                x=["Job Skills"],
                y=[len(match["missing_skills"])],
                marker_color="#151515"
            )
        )

        chart.update_layout(
            barmode="group",
            paper_bgcolor="#F3F0E8",
            plot_bgcolor="#FFFFFF",
            font=dict(color="#151515"),
            height=330,
            yaxis_title="Number of skills",
            margin=dict(l=25, r=25, t=30, b=30)
        )

        st.plotly_chart(
            chart,
            use_container_width=True
        )

    else:

        cat_counts = {
            cat: len(s_list)
            for cat, s_list in data.get("skills", {}).items()
            if s_list
        }

        if cat_counts:

            st.markdown("### Profile Skill Domain Breakdown")

            chart = go.Figure()

            chart.add_trace(
                go.Bar(
                    x=list(cat_counts.keys()),
                    y=list(cat_counts.values()),
                    marker_color="#4263EB"
                )
            )

            chart.update_layout(
                paper_bgcolor="#F3F0E8",
                plot_bgcolor="#FFFFFF",
                font=dict(color="#151515"),
                height=300,
                yaxis_title="Skills Count",
                margin=dict(l=25, r=25, t=30, b=30)
            )

            st.plotly_chart(
                chart,
                use_container_width=True
            )

        if match.get("resume_skills"):

            st.markdown("### Profile Verified Skills")

            tags = "".join(
                f'<span class="skill-tag">✓ {escape(str(skill))}</span>'
                for skill in match["resume_skills"]
            )

            st.markdown(tags, unsafe_allow_html=True)

    # ------------------------------------------------------
    # SKILLS BY CATEGORY
    # ------------------------------------------------------

    st.divider()

    st.markdown(
        '<span class="section-tag">COMPETENCY TAXONOMY</span>'
        '<div class="section-heading">Detected Skills</div>',
        unsafe_allow_html=True
    )

    if data["skills"]:

        for category, skills in data["skills"].items():

            with st.expander(
                f"{category} — {len(skills)} skills",
                expanded=True
            ):

                tags = "".join(
                    f'<span class="skill-tag">{escape(str(skill))}</span>'
                    for skill in skills
                )

                st.markdown(
                    tags,
                    unsafe_allow_html=True
                )

    else:

        st.warning(
            "No recognised skills found. "
            "The resume may use skills outside the current dictionary."
        )

    # ------------------------------------------------------
    # COMPLETE RESUMIND AI ANALYSIS REPORT
    # ------------------------------------------------------

    ai_report = data.get("ai_analysis")
    if ai_report:

        st.divider()

        st.markdown(
            '<span class="section-tag">EXECUTIVE INTELLIGENCE</span>'
            '<div class="section-heading">Complete Resumind AI Analysis</div>',
            unsafe_allow_html=True
        )

        st.markdown(ai_report)

    # ------------------------------------------------------
    # PROFESSIONAL SUMMARY & OBJECTIVE
    # ------------------------------------------------------

    summary_text = (data.get("professional_summary") or "").strip()
    objective_text = (data.get("career_objective") or "").strip()

    if summary_text or objective_text:

        st.divider()

        if summary_text:
            st.markdown("### Professional Summary")
            st.write(summary_text)

        if objective_text and objective_text != summary_text:
            st.markdown("### Career Objective")
            st.write(objective_text)

    # ------------------------------------------------------
    # EDUCATION
    # ------------------------------------------------------

    st.divider()

    st.markdown("### Education")

    education = data.get("education") or {}
    sec_text = education.get("section_text", "") if isinstance(education, dict) else str(education)
    quals = education.get("possible_qualifications", []) if isinstance(education, dict) else []

    st.write(
        sec_text or "No education section detected."
    )

    if quals:

        st.markdown("**Possible qualifications detected:**")

        for qualification in quals:
            st.write(f"• {qualification}")

    # ------------------------------------------------------
    # EXPERIENCE
    # ------------------------------------------------------

    st.divider()

    st.markdown("### Work Experience")

    experience = data.get("experience") or {}
    exp_text = experience.get("section_text", "") if isinstance(experience, dict) else str(experience)
    exp_years = experience.get("years_of_experience_mentioned") if isinstance(experience, dict) else None

    st.write(
        exp_text or "No experience section detected."
    )

    if exp_years is not None:

        st.metric(
            "Experience mentioned",
            f"{exp_years} years"
        )

    # ------------------------------------------------------
    # PROJECTS AND CERTIFICATIONS
    # ------------------------------------------------------

    st.divider()

    pc1, pc2 = st.columns(2)

    with pc1:

        st.markdown("### Projects")

        st.write(
            data["projects"]
            or "No projects detected."
        )

    with pc2:

        st.markdown("### Certifications")

        st.write(
            data["certifications"]
            or "No certifications detected."
        )

    # ------------------------------------------------------
    # ACHIEVEMENTS AND LANGUAGES
    # ------------------------------------------------------

    ac1, ac2 = st.columns(2)

    with ac1:

        st.markdown("### Achievements")

        st.write(
            data["achievements"]
            or "No achievements detected."
        )

    with ac2:

        st.markdown("### Languages")

        st.write(
            data["languages"]
            or "No language section detected."
        )

    # ------------------------------------------------------
    # TRAINED MODEL PREDICTIONS
    # ------------------------------------------------------

    if data.get("trained_skill_predictions"):

        st.divider()

        st.markdown("### ✦ Resumind Neural Network Predictions")

        st.caption(
            "Predictions from your custom PyTorch SkillNet trained on your RTX 2050 GPU."
        )

        st.dataframe(
            data["trained_skill_predictions"],
            width="stretch",
            hide_index=True
        )

    elif data.get("trained_model_warning"):

        st.warning(
            "The trained model could not run: "
            + data["trained_model_warning"]
        )

    else:

        st.info(
            "Custom PyTorch SkillNet model is not trained yet. "
            "Run 'python build_model.py' to train it."
        )

    # ------------------------------------------------------
    # FULL JSON ANALYSIS
    # ------------------------------------------------------

    st.divider()

    with st.expander("View Complete Resumind AI Analysis"):

        st.json(data, expanded=True)

    # ------------------------------------------------------
    # DOWNLOAD REPORTS
    # ------------------------------------------------------

    st.divider()

    st.markdown("### Export Your Report")

    pdf_bytes = create_pdf_report(result)

    if pdf_bytes:

        st.download_button(
            "DOWNLOAD PDF REPORT",
            data=pdf_bytes,
            file_name="Resumind_AI_Report.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    else:

        st.warning(
            "Install reportlab to enable PDF reports."
        )

    # ------------------------------------------------------
    # NEW ANALYSIS
    # ------------------------------------------------------

    st.divider()

    if st.button(
        "START NEW RESUME ANALYSIS",
        use_container_width=True
    ):

        st.session_state.analysis_result = None
        st.rerun()

    st.markdown("""
    <div class="footer">
        <div class="brand">RESUMIND <span>AI</span></div>
        Powered by Resumind AI<br>
        &copy; 2026 Resumind AI
    </div>
    """, unsafe_allow_html=True)