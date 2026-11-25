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
from interview_engine import generate_interview_test, evaluate_test, generate_interview_pdf_report


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
    --bg: #F8FAFC;
    --ink: #0F172A;
    --blue: #4263EB;
    --blue-dark: #364FC7;
    --muted: #64748B;
    --card: #FFFFFF;
    --border: #E2E8F0;
}

html, body, .stApp {
    background-color: var(--bg) !important;
    color: var(--ink) !important;
    font-family: 'Plus Jakarta Sans', -apple-system, sans-serif !important;
}

.block-container {
    max-width: 1220px;
    padding-top: 1.5rem;
    padding-bottom: 4rem;
}

header[data-testid="stHeader"] {
    background: transparent !important;
}

#MainMenu, footer {
    visibility: hidden;
}

.brand {
    font-family: 'Cinzel', serif;
    font-size: 21px;
    font-weight: 700;
    letter-spacing: .15em;
    color: var(--ink) !important;
}

.brand span {
    color: var(--blue) !important;
}

.hero {
    text-align: center;
    padding: 40px 10px 25px;
}

.hero-tag {
    display: inline-block;
    background: #EEF2FF;
    border: 1px solid #C7D2FE;
    border-radius: 30px;
    padding: 6px 16px;
    color: var(--blue);
    font-size: 11px;
    font-weight: 700;
    letter-spacing: .12em;
}

.hero h1 {
    font-family: 'Instrument Serif', Georgia, serif;
    font-size: clamp(38px, 6vw, 64px);
    line-height: 1.15;
    font-weight: 400;
    color: var(--ink) !important;
    margin: 20px 0 12px;
}

.hero h1 em {
    color: var(--blue) !important;
    font-style: italic;
}

.hero p {
    max-width: 680px;
    margin: auto;
    color: #475569 !important;
    font-size: 15px;
    line-height: 1.7;
}

.section-heading {
    font-family: 'Instrument Serif', Georgia, serif;
    font-size: 34px;
    color: var(--ink) !important;
    margin: 28px 0 10px;
}

.section-tag {
    color: var(--blue);
    font-size: 11px;
    font-weight: 700;
    letter-spacing: .15em;
}

/* Upload Panel Header Styles */
.upload-panel-header {
    margin-bottom: 12px;
}

.panel-badge {
    display: inline-block;
    background: #EEF2FF;
    color: var(--blue);
    border: 1px solid #C7D2FE;
    border-radius: 20px;
    padding: 3px 10px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: .08em;
    margin-bottom: 6px;
}

.upload-panel-header h4 {
    margin: 4px 0 2px 0;
    font-size: 17px;
    font-weight: 600;
    color: #0F172A !important;
}

.panel-desc {
    font-size: 13px;
    color: #64748B !important;
    margin: 0 0 8px 0;
    line-height: 1.5;
}

/* File Uploader - Pure Crisp Light Mode */
div[data-testid="stFileUploader"] {
    background: #FFFFFF !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 16px !important;
    padding: 18px !important;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.02) !important;
}

div[data-testid="stFileUploader"] label[data-testid="stWidgetLabel"] {
    color: #0F172A !important;
    font-weight: 600 !important;
}

div[data-testid="stFileUploader"] section[data-testid="stFileUploaderDropzone"] {
    background: #F8FAFC !important;
    border: 2px dashed #93C5FD !important;
    border-radius: 12px !important;
    padding: 24px 14px !important;
    text-align: center !important;
}

div[data-testid="stFileUploader"] section[data-testid="stFileUploaderDropzone"]:hover {
    background: #EFF6FF !important;
    border-color: #3B82F6 !important;
}

div[data-testid="stFileUploader"] section[data-testid="stFileUploaderDropzone"] svg {
    fill: #4263EB !important;
    stroke: #4263EB !important;
    color: #4263EB !important;
}

div[data-testid="stFileUploader"] section[data-testid="stFileUploaderDropzone"] span,
div[data-testid="stFileUploader"] section[data-testid="stFileUploaderDropzone"] small,
div[data-testid="stFileUploader"] section[data-testid="stFileUploaderDropzone"] div,
div[data-testid="stFileUploaderDropzoneInstructions"] * {
    color: #334155 !important;
    font-weight: 500 !important;
}

div[data-testid="stFileUploader"] button,
div[data-testid="stFileUploaderDropzone"] button,
section[data-testid="stFileUploaderDropzone"] button {
    background: #FFFFFF !important;
    color: #2563EB !important;
    -webkit-text-fill-color: #2563EB !important;
    border: 1px solid #BFDBFE !important;
    border-radius: 8px !important;
    padding: 6px 16px !important;
    font-weight: 600 !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05) !important;
}

div[data-testid="stFileUploader"] button:hover,
div[data-testid="stFileUploaderDropzone"] button:hover,
section[data-testid="stFileUploaderDropzone"] button:hover {
    background: #EFF6FF !important;
    color: #1D4ED8 !important;
    -webkit-text-fill-color: #1D4ED8 !important;
    border-color: #60A5FA !important;
}

div[data-testid="stFileUploaderFileData"] {
    background: #F1F5F9 !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 10px !important;
    padding: 10px 14px !important;
    margin-top: 10px !important;
}

div[data-testid="stFileUploaderFileData"] * {
    color: #0F172A !important;
}

div[data-testid="stFileUploaderFileData"] button {
    background: transparent !important;
    border: none !important;
    color: #64748B !important;
    box-shadow: none !important;
}

div[data-testid="stFileUploaderFileData"] button:hover {
    background: #FEE2E2 !important;
    color: #DC2626 !important;
}

/* Textarea - Crisp White Background, High Contrast Text */
div[data-testid="stTextArea"] {
    background: transparent !important;
}

div[data-testid="stTextArea"] label[data-testid="stWidgetLabel"] {
    color: #0F172A !important;
    font-weight: 600 !important;
}

div[data-baseweb="textarea"],
div[data-baseweb="base-input"] {
    background-color: #FFFFFF !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 14px !important;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.02) !important;
}

div[data-baseweb="textarea"]:focus-within,
div[data-baseweb="base-input"]:focus-within {
    border-color: #3B82F6 !important;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15) !important;
}

div[data-baseweb="textarea"] textarea,
div[data-baseweb="base-input"] textarea {
    background-color: #FFFFFF !important;
    color: #0F172A !important;
    -webkit-text-fill-color: #0F172A !important;
    font-size: 14px !important;
    line-height: 1.6 !important;
    padding: 14px !important;
}

div[data-baseweb="textarea"] textarea::placeholder,
div[data-baseweb="base-input"] textarea::placeholder {
    color: #94A3B8 !important;
    -webkit-text-fill-color: #94A3B8 !important;
}

/* Primary and Secondary Buttons */
button[kind="primary"],
.stButton > button[kind="primary"],
button[data-testid="stBaseButton-primary"],
.stButton > button[data-testid="stBaseButton-primary"] {
    background: linear-gradient(135deg, #4263EB 0%, #364FC7 100%) !important;
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    border: none !important;
    border-radius: 999px !important;
    min-height: 48px !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    letter-spacing: .05em !important;
    box-shadow: 0 4px 14px rgba(66, 99, 235, 0.25) !important;
    transition: all 0.2s ease !important;
}

button[kind="primary"]:hover,
.stButton > button[kind="primary"]:hover,
button[data-testid="stBaseButton-primary"]:hover,
.stButton > button[data-testid="stBaseButton-primary"]:hover {
    background: linear-gradient(135deg, #364FC7 0%, #2B3FA0 100%) !important;
    box-shadow: 0 6px 20px rgba(66, 99, 235, 0.35) !important;
    transform: translateY(-1px) !important;
}

button[kind="secondary"],
.stButton > button,
button[data-testid="stBaseButton-secondary"],
.stButton > button[data-testid="stBaseButton-secondary"] {
    background: #FFFFFF !important;
    color: #1E293B !important;
    -webkit-text-fill-color: #1E293B !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 999px !important;
    min-height: 44px !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    letter-spacing: .03em !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04) !important;
    transition: all 0.2s ease !important;
}

button[kind="secondary"]:hover,
.stButton > button:hover,
button[data-testid="stBaseButton-secondary"]:hover,
.stButton > button[data-testid="stBaseButton-secondary"]:hover {
    background: #F8FAFC !important;
    color: #0F172A !important;
    -webkit-text-fill-color: #0F172A !important;
    border-color: #94A3B8 !important;
}

.stDownloadButton > button,
.stDownloadButton > button[data-testid="stBaseButton-primary"],
.stDownloadButton > button[data-testid="stBaseButton-secondary"] {
    background: linear-gradient(135deg, #4263EB 0%, #364FC7 100%) !important;
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    border-radius: 999px !important;
    border: none !important;
    min-height: 48px !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    letter-spacing: .05em !important;
    box-shadow: 0 4px 14px rgba(66, 99, 235, 0.25) !important;
}

.stDownloadButton > button:hover {
    background: linear-gradient(135deg, #364FC7 0%, #2B3FA0 100%) !important;
    box-shadow: 0 6px 20px rgba(66, 99, 235, 0.35) !important;
}

/* Code and Pre blocks */
code, pre {
    background: #F1F5F9 !important;
    color: #0F172A !important;
    -webkit-text-fill-color: #0F172A !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 8px !important;
}

/* Feature and Result Cards */
.feature-card {
    background: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 20px !important;
    padding: 24px !important;
    min-height: 180px;
    margin-bottom: 15px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.02) !important;
}

.feature-card h3 {
    font-size: 17px;
    color: #0F172A !important;
    margin-bottom: 10px;
}

.feature-card p {
    font-size: 13px;
    color: #64748B !important;
    line-height: 1.7;
}

/* Metrics Cards */
div[data-testid="stMetric"] {
    background: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 18px !important;
    padding: 20px !important;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.02) !important;
}

div[data-testid="stMetricLabel"] {
    color: #64748B !important;
    font-size: 12px !important;
    font-weight: 700 !important;
    letter-spacing: .08em !important;
    text-transform: uppercase !important;
}

div[data-testid="stMetricValue"] {
    color: #0F172A !important;
    font-family: 'Instrument Serif', Georgia, serif !important;
    font-size: 32px !important;
}

/* Alerts - Pure Light Mode, Zero Dark Spots */
div[data-testid="stAlert"] {
    border-radius: 14px !important;
    padding: 14px 18px !important;
    font-size: 14px !important;
    line-height: 1.6 !important;
}

div[data-testid="stAlert"] * {
    color: inherit !important;
}

div[data-testid="stAlert"]:has([data-testid="stNotificationContentInfo"]) {
    background: #EFF6FF !important;
    color: #1E40AF !important;
    border: 1px solid #BFDBFE !important;
}

div[data-testid="stAlert"]:has([data-testid="stNotificationContentSuccess"]) {
    background: #F0FDF4 !important;
    color: #166534 !important;
    border: 1px solid #BBF7D0 !important;
}

div[data-testid="stAlert"]:has([data-testid="stNotificationContentWarning"]) {
    background: #FFFBEB !important;
    color: #92400E !important;
    border: 1px solid #FDE68A !important;
}

div[data-testid="stAlert"]:has([data-testid="stNotificationContentError"]) {
    background: #FEF2F2 !important;
    color: #991B1B !important;
    border: 1px solid #FECACA !important;
}

/* Expanders */
div[data-testid="stExpander"] {
    background: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 14px !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.02) !important;
}

div[data-testid="stExpander"] details {
    background: #FFFFFF !important;
    border-radius: 14px !important;
}

div[data-testid="stExpander"] summary {
    color: #0F172A !important;
    font-weight: 600 !important;
}

/* Skill Tags */
.skill-tag {
    display: inline-block;
    background: #EEF2FF;
    color: #3730A3;
    border: 1px solid #C7D2FE;
    border-radius: 30px;
    padding: 6px 14px;
    margin: 4px;
    font-size: 12px;
    font-weight: 600;
}

.missing-tag {
    display: inline-block;
    background: #FFF7ED;
    color: #9A3412;
    border: 1px solid #FED7AA;
    border-radius: 30px;
    padding: 6px 14px;
    margin: 4px;
    font-size: 12px;
    font-weight: 600;
}

.footer {
    border-top: 1px solid #E2E8F0;
    text-align: center;
    padding: 35px 0 10px;
    margin-top: 60px;
    color: #64748B;
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

if "interview_test" not in st.session_state:
    st.session_state.interview_test = None

if "interview_answers" not in st.session_state:
    st.session_state.interview_answers = {}

if "interview_eval" not in st.session_state:
    st.session_state.interview_eval = None


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

nav1, nav2, nav3, nav4 = st.columns([2.2, 1, 1, 1.3])

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

with nav4:

    if st.button("MOCK INTERVIEW 🎯", use_container_width=True):

        st.session_state.page = "Interview"
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

    input1, input2 = st.columns([1, 1], gap="medium")

    with input1:

        st.markdown(
            '<div class="upload-panel-header">'
            '<span class="panel-badge">STEP 1</span>'
            '<h4>Upload PDF Resume</h4>'
            '<p class="panel-desc">Select or drop your text-based PDF resume (supports IT & non-IT).</p>'
            '</div>',
            unsafe_allow_html=True
        )

        uploaded_file = st.file_uploader(
            "Upload Resume PDF",
            type=["pdf"],
            help="Upload a text-based PDF resume.",
            label_visibility="collapsed"
        )

        if uploaded_file:

            st.success(
                f"✓ Resume loaded: {uploaded_file.name} ({len(uploaded_file.getvalue()) / 1024:.1f} KB)"
            )

    with input2:

        st.markdown(
            '<div class="upload-panel-header">'
            '<span class="panel-badge">STEP 2</span>'
            '<h4>Target Job Description <span style="font-weight:400; color:#64748B; font-size:12px;">(Optional)</span></h4>'
            '<p class="panel-desc">Paste job requirements to run ATS skill matching and gap analysis.</p>'
            '</div>',
            unsafe_allow_html=True
        )

        job_description = st.text_area(
            "Target Job Description (Optional)",
            placeholder=(
                "Paste the job description here if you "
                "want a resume-to-job comparison, ATS score & keyword match..."
            ),
            height=180,
            label_visibility="collapsed"
        )

    st.markdown('<div style="height: 10px;"></div>', unsafe_allow_html=True)

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
                marker_color="#F43F5E"
            )
        )

        chart.update_layout(
            barmode="group",
            paper_bgcolor="#FFFFFF",
            plot_bgcolor="#F8FAFC",
            font=dict(color="#0F172A", family="Plus Jakarta Sans"),
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
                paper_bgcolor="#FFFFFF",
                plot_bgcolor="#F8FAFC",
                font=dict(color="#0F172A", family="Plus Jakarta Sans"),
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
    # MOCK INTERVIEW CALLOUT
    # ------------------------------------------------------

    st.divider()

    st.markdown(
        '<div style="background: linear-gradient(135deg, #EEF2FF 0%, #E0E7FF 100%); '
        'border: 1px solid #C7D2FE; border-radius: 20px; padding: 24px 28px; margin: 15px 0;">'
        '<span style="display:inline-block; background:#4263EB; color:#FFFFFF; '
        'border-radius:20px; padding:4px 12px; font-size:11px; font-weight:700; '
        'letter-spacing:.08em; margin-bottom:10px;">✦ NEXT STEP: INTERVIEW PREPARATION</span>'
        '<h3 style="margin:4px 0 8px 0; color:#1E1B4B; font-size:20px; font-weight:700;">'
        'Test Your Knowledge with an AI Mock Interview</h3>'
        '<p style="margin:0 0 16px 0; color:#3730A3; font-size:14px; line-height:1.6;">'
        'Take an interactive test calibrated directly to your resume\'s detected skills '
        'and career category. Practice technical questions, review scenario challenges, '
        'and get instant readiness feedback with interviewer insights.</p>'
        '</div>',
        unsafe_allow_html=True
    )

    if st.button("START MOCK INTERVIEW TEST BASED ON THIS RESUME →", type="primary", key="btn_start_interview_from_resume", use_container_width=True):
        candidate_skills = list(match.get("resume_skills") or [])
        if not candidate_skills and data.get("skills"):
            for s_list in data["skills"].values():
                candidate_skills.extend(s_list)
        st.session_state.interview_test = generate_interview_test(
            candidate_skills=candidate_skills,
            resume_category=data.get("resume_category"),
            num_questions=5,
            focus_mode="Balanced Mock Interview"
        )
        st.session_state.interview_answers = {}
        st.session_state.interview_eval = None
        st.session_state.page = "Interview"
        st.rerun()

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
        type="secondary",
        use_container_width=True
    ):

        st.session_state.analysis_result = None
        st.rerun()

    st.markdown(
        '<div class="footer">'
        '<div class="brand">RESUMIND <span>AI</span></div>'
        'Powered by Resumind AI<br>'
        '&copy; 2026 Resumind AI'
        '</div>',
        unsafe_allow_html=True
    )


# ==========================================================
# 12. INTERVIEW PREP & SKILL TEST STUDIO
# ==========================================================

if st.session_state.page == "Interview":

    st.markdown(
        '<div class="hero">'
        '<span class="hero-tag">✦ AI INTERVIEW PREPARATION STUDIO</span>'
        '<h1>Interactive Mock Interview<br><em>& Skill Test</em></h1>'
        '<p>Test your competencies with questions tailored directly to your skills and domain. Get immediate evaluation, interview readiness grades, and detailed interviewer insights.</p>'
        '</div>',
        unsafe_allow_html=True
    )

    # STATE 1: CONFIGURATION (No active test yet)
    if st.session_state.interview_test is None:
        has_resume = (st.session_state.analysis_result is not None)
        active_skills = []
        active_name = "Candidate"
        active_cat = "IT & SOFTWARE"

        if has_resume:
            res = st.session_state.analysis_result
            active_name = res["candidate"]["name"]
            active_cat = res["soura_result"]["resume_category"]
            active_skills = list(res["match_data"].get("resume_skills") or [])
            if not active_skills and res["soura_result"].get("skills"):
                for slist in res["soura_result"]["skills"].values():
                    active_skills.extend(slist)

        # Config Panel
        with st.container(border=True):
            st.markdown(
                '<div class="upload-panel-header">'
                '<span class="panel-badge">TEST CONFIGURATION</span>'
                '<h4>Configure Your Mock Interview</h4>'
                '<p class="panel-desc">Customize your assessment focus, domain alignment, and question volume.</p>'
                '</div>',
                unsafe_allow_html=True
            )

            if has_resume and active_skills:
                st.info(
                    f"🎯 **Resume Synchronized:** Testing skills detected in **{active_name}'s** resume ({active_cat}): "
                    f"*{', '.join(active_skills[:12])}*"
                )
            else:
                st.info(
                    "💡 **No Resume Uploaded Yet:** You can choose your skills manually below, or upload a resume in the **ANALYSER** tab for auto-calibration."
                )

            c1, c2 = st.columns(2, gap="medium")
            with c1:
                focus_mode = st.selectbox(
                    "Interview Focus Area",
                    options=["Balanced Mock Interview", "Technical Only", "Behavioral & Leadership"],
                    index=0,
                    help="Balanced includes both technical knowledge and behavioral scenario questions."
                )

            with c2:
                num_q = st.select_slider(
                    "Number of Questions",
                    options=[3, 5, 8, 10, 15],
                    value=5
                )

            # Manual skill override / addition if desired
            all_known_skills = []
            for slist in SKILL_DATABASE.values():
                all_known_skills.extend(slist)
            all_known_skills = sorted(list(set(all_known_skills)))

            default_skills = [s for s in active_skills if s in all_known_skills] or ["Python", "SQL", "Git", "Problem Solving"]
            selected_skills = st.multiselect(
                "Target Skills to Test",
                options=all_known_skills,
                default=default_skills[:8],
                help="Add or remove skills to tailor the questions."
            )

            st.markdown('<div style="height: 10px;"></div>', unsafe_allow_html=True)

            if st.button("GENERATE & START TEST →", type="primary", use_container_width=True):
                test_questions = generate_interview_test(
                    candidate_skills=selected_skills,
                    resume_category=active_cat,
                    num_questions=num_q,
                    focus_mode=focus_mode
                )
                st.session_state.interview_test = test_questions
                st.session_state.interview_answers = {}
                st.session_state.interview_eval = None
                st.rerun()

    # STATE 2: ACTIVE TEST IN PROGRESS
    elif st.session_state.interview_eval is None:
        questions = st.session_state.interview_test
        total_q = len(questions)

        top_col1, top_col2 = st.columns([3, 1])
        with top_col1:
            st.markdown(
                f'<span class="section-tag">ASSESSMENT IN PROGRESS</span>'
                f'<div class="section-heading" style="font-size:26px; margin:10px 0;">'
                f'Answer the following {total_q} questions</div>',
                unsafe_allow_html=True
            )
        with top_col2:
            if st.button("RESET TEST ✕", type="secondary", use_container_width=True):
                st.session_state.interview_test = None
                st.session_state.interview_answers = {}
                st.session_state.interview_eval = None
                st.rerun()

        st.progress(
            len(st.session_state.interview_answers) / max(1, total_q),
            text=f"Completed {len(st.session_state.interview_answers)} of {total_q} questions"
        )

        for q in questions:
            q_id = q["test_id"]
            current_choice = st.session_state.interview_answers.get(q_id, None)

            with st.container(border=True):
                st.markdown(
                    f'<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">'
                    f'<div>'
                    f'<span class="panel-badge">QUESTION {q["question_number"]} OF {total_q}</span> '
                    f'<span class="skill-tag" style="margin:0 4px;">{escape(q["skill"])}</span>'
                    f'</div>'
                    f'<span style="font-size:11px; font-weight:600; color:#64748B; background:#F1F5F9; border-radius:20px; padding:3px 10px;">{escape(q["difficulty"])}</span>'
                    f'</div>'
                    f'<h4 style="margin:8px 0 14px 0; color:#0F172A; font-size:16px; font-weight:600; line-height:1.5;">'
                    f'{escape(q["question"])}</h4>',
                    unsafe_allow_html=True
                )

                selected_opt = st.radio(
                    label=f"q_label_{q_id}",
                    options=q["options"],
                    index=current_choice if current_choice is not None else None,
                    key=f"radio_{q_id}",
                    label_visibility="collapsed"
                )

                if selected_opt is not None:
                    st.session_state.interview_answers[q_id] = q["options"].index(selected_opt)

        st.markdown('<div style="height: 15px;"></div>', unsafe_allow_html=True)

        if st.button("SUBMIT TEST & VIEW EVALUATION →", type="primary", use_container_width=True):
            if len(st.session_state.interview_answers) < total_q:
                st.warning(f"Please answer all {total_q} questions before submitting (currently answered: {len(st.session_state.interview_answers)}).")
            else:
                eval_result = evaluate_test(st.session_state.interview_test, st.session_state.interview_answers)
                st.session_state.interview_eval = eval_result
                st.rerun()

    # STATE 3: TEST EVALUATION & DETAILED RESULTS
    else:
        eval_res = st.session_state.interview_eval
        score_pct = eval_res["score_pct"]
        correct_count = eval_res["correct_count"]
        total_q = eval_res["total"]
        tier = eval_res["tier"]

        candidate_name = "Candidate"
        if st.session_state.analysis_result:
            candidate_name = st.session_state.analysis_result["candidate"]["name"]

        # Results Hero Card
        st.markdown(
            f'<div style="background: #FFFFFF; border: 1px solid #CBD5E1; border-radius: 20px; padding: 28px; '
            f'box-shadow: 0 4px 16px rgba(0,0,0,0.03); text-align: center; margin-bottom: 25px;">'
            f'<span class="panel-badge">EVALUATION COMPLETE</span>'
            f'<h1 style="font-family:\'Instrument Serif\', serif; font-size: 56px; margin: 10px 0; color: #0F172A;">'
            f'{score_pct}%</h1>'
            f'<div style="font-size: 17px; font-weight: 700; color: {eval_res["readiness_color"]}; margin-bottom: 8px;">'
            f'{eval_res["readiness_badge"]}</div>'
            f'<p style="color: #64748B; font-size: 14px; margin: 0;">'
            f'Answered <b>{correct_count}</b> out of <b>{total_q}</b> questions correctly</p>'
            f'</div>',
            unsafe_allow_html=True
        )

        # Performance Metrics
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("Score", f"{score_pct}%")
        with m2:
            st.metric("Correct Answers", f"{correct_count} / {total_q}")
        with m3:
            st.metric("Readiness Tier", tier)

        # Per-Skill Mastery Breakdown
        if eval_res.get("skill_stats"):
            st.divider()
            st.markdown(
                '<span class="section-tag">COMPETENCY ACCURACY</span>'
                '<div class="section-heading">Skill-by-Skill Breakdown</div>',
                unsafe_allow_html=True
            )

            skill_cols = st.columns(min(4, max(1, len(eval_res["skill_stats"]))))
            for idx, (sname, sdata) in enumerate(eval_res["skill_stats"].items()):
                col = skill_cols[idx % len(skill_cols)]
                with col:
                    col_score = round((sdata["correct"] / sdata["total"]) * 100)
                    with st.container(border=True):
                        st.markdown(f"**{escape(sname)}**")
                        st.markdown(f"Accuracy: **{col_score}%** ({sdata['correct']}/{sdata['total']})")

        # Weak skills alert
        if eval_res.get("weak_skills"):
            st.warning(
                f"💡 **Recommended Revision:** Focus your final interview prep on: "
                f"**{', '.join(eval_res['weak_skills'])}**."
            )
        else:
            st.success("🎉 Outstanding! You answered every question correctly across all tested skill domains!")

        # Detailed Question Review
        st.divider()
        st.markdown(
            '<span class="section-tag">DETAILED REVIEW</span>'
            '<div class="section-heading">Question-by-Question Analysis & Interviewer Insights</div>',
            unsafe_allow_html=True
        )

        for item in eval_res["review"]:
            is_corr = item["is_correct"]
            bg_card = "#F0FDF4" if is_corr else "#FEF2F2"
            border_card = "#BBF7D0" if is_corr else "#FECACA"
            header_color = "#166534" if is_corr else "#991B1B"
            status_text = "✓ CORRECT" if is_corr else "✕ INCORRECT"

            st.markdown(
                f'<div style="background:{bg_card}; border:1px solid {border_card}; border-radius:16px; padding:20px; margin-bottom:18px;">'
                f'<div style="display:flex; justify-content:space-between; margin-bottom:8px;">'
                f'<span style="font-weight:700; color:{header_color}; font-size:12px; letter-spacing:.05em;">'
                f'{status_text} • QUESTION {item["question_number"]} ({escape(item["skill"])})</span>'
                f'</div>'
                f'<h4 style="margin:4px 0 12px 0; color:#0F172A; font-size:16px; line-height:1.5;">'
                f'{escape(item["question"])}</h4>'
                f'<p style="margin:4px 0; font-size:14px; color:#334155;"><b>Your Answer:</b> '
                f'<span style="color:{"#166534" if is_corr else "#DC2626"};">{escape(item["user_answer_text"])}</span></p>'
                f'{"<p style=\'margin:4px 0; font-size:14px; color:#166534;\'><b>Correct Answer:</b> " + escape(item["correct_answer_text"]) + "</p>" if not is_corr else ""}'
                f'<div style="margin-top:12px; padding-top:10px; border-top:1px dashed {border_card};">'
                f'<p style="margin:4px 0; font-size:13px; color:#475569; line-height:1.6;"><b>Explanation:</b> {escape(item["explanation"])}</p>'
                f'<p style="margin:6px 0 0 0; font-size:13px; color:#364FC7; line-height:1.6;"><b>💡 Interviewer Insight:</b> {escape(item["insight"])}</p>'
                f'</div>'
                f'</div>',
                unsafe_allow_html=True
            )

        # Download & Next Steps
        st.divider()
        st.markdown("### Export & Next Steps")

        pdf_bytes = generate_interview_pdf_report(candidate_name, eval_res)
        if pdf_bytes:
            st.download_button(
                "DOWNLOAD INTERVIEW READINESS REPORT (PDF)",
                data=pdf_bytes,
                file_name=f"Interview_Readiness_{candidate_name.replace(' ', '_')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )

        retake_c1, retake_c2 = st.columns(2)
        with retake_c1:
            if st.button("TAKE A NEW TEST ↻", type="secondary", use_container_width=True):
                st.session_state.interview_test = None
                st.session_state.interview_answers = {}
                st.session_state.interview_eval = None
                st.rerun()

        with retake_c2:
            if st.button("BACK TO RESUME AUDIT →", type="secondary", use_container_width=True):
                st.session_state.page = "Analysis"
                st.rerun()

    st.markdown(
        '<div class="footer">'
        '<div class="brand">RESUMIND <span>AI</span></div>'
        'AI Career Readiness & Interview Prep<br>'
        '&copy; 2026 Resumind AI'
        '</div>',
        unsafe_allow_html=True
    )