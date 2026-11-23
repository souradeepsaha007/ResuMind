import re
from io import BytesIO
from datetime import datetime
from xml.sax.saxutils import escape

import streamlit as st
import pymupdf
import plotly.graph_objects as go

from matcher import calculate_match
from llm_analyzer import analyse_resume


# ==========================================================
# 1. PAGE CONFIGURATION
# ==========================================================

st.set_page_config(
    page_title="Soura AI — Career Intelligence",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ==========================================================
# 2. DESIGN SYSTEM & STYLES (INSPIRED BY MINDLY)
# ==========================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital,wght@0,400;1,400&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');

/* --- Root & Background --- */
html, body, .stApp {
    background-color: #FAF9F5 !important;
    background-image: 
        radial-gradient(circle at 50% 0%, rgba(255, 255, 255, 0.95) 0%, rgba(250, 249, 245, 0.6) 60%, rgba(243, 239, 231, 0.4) 100%),
        radial-gradient(circle at 85% 25%, rgba(246, 242, 233, 0.6) 0%, transparent 45%),
        radial-gradient(circle at 15% 45%, rgba(244, 240, 230, 0.5) 0%, transparent 45%) !important;
    color: #1A1A1A !important;
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
    -webkit-font-smoothing: antialiased;
}

.block-container {
    max-width: 1180px !important;
    padding-top: 1.2rem !important;
    padding-bottom: 4rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
}

header[data-testid="stHeader"] {
    background: transparent !important;
}

#MainMenu, footer {
    visibility: hidden !important;
}

/* --- Navigation Bar --- */
.nav-wrap {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 0 28px 0;
}

.brand-wrap {
    display: flex;
    align-items: baseline;
    gap: 2px;
    font-weight: 700;
    font-size: 22px;
    letter-spacing: -0.03em;
    color: #111111;
}

.brand-wrap .brand-dot {
    font-size: 14px;
    color: #111111;
    font-weight: 700;
}

/* --- Streamlit Buttons (Pill Aesthetic) --- */
.stButton > button {
    background: #121212 !important;
    color: #FFFFFF !important;
    border: 1px solid #121212 !important;
    border-radius: 9999px !important;
    padding: 10px 24px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    letter-spacing: -0.01em !important;
    transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.07) !important;
    min-height: 44px !important;
}

.stButton > button:hover {
    background: #262626 !important;
    color: #FFFFFF !important;
    border-color: #262626 !important;
    transform: translateY(-1.5px) !important;
    box-shadow: 0 8px 22px rgba(0, 0, 0, 0.12) !important;
}

.stButton > button:active {
    transform: translateY(0px) !important;
}

/* Secondary Button Variant */
.stButton > button[kind="secondary"] {
    background: rgba(255, 255, 255, 0.85) !important;
    color: #1F1F1F !important;
    border: 1px solid rgba(0, 0, 0, 0.08) !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03) !important;
}

.stButton > button[kind="secondary"]:hover {
    background: #FFFFFF !important;
    color: #000000 !important;
    border-color: rgba(0, 0, 0, 0.16) !important;
}

/* Download Button */
.stDownloadButton > button {
    background: #121212 !important;
    color: #FFFFFF !important;
    border: 1px solid #121212 !important;
    border-radius: 9999px !important;
    padding: 12px 28px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 15px !important;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08) !important;
    transition: all 0.25s ease !important;
    min-height: 48px !important;
}

.stDownloadButton > button:hover {
    background: #262626 !important;
    color: #FFFFFF !important;
    transform: translateY(-1.5px) !important;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.14) !important;
}

/* --- Hero Section Typography --- */
.hero-container {
    position: relative;
    text-align: center;
    padding: 40px 10px 30px 10px;
    margin-bottom: 20px;
}

.hero-pill-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(255, 255, 255, 0.8);
    border: 1px solid rgba(0, 0, 0, 0.06);
    backdrop-filter: blur(10px);
    border-radius: 9999px;
    padding: 6px 16px;
    font-size: 12.5px;
    font-weight: 600;
    letter-spacing: 0.04em;
    color: #555555;
    text-transform: uppercase;
    margin-bottom: 22px;
}

.hero-heading {
    font-family: 'Instrument Serif', 'Playfair Display', Georgia, serif;
    font-size: 64px;
    line-height: 1.08;
    color: #121212;
    font-weight: 400;
    letter-spacing: -0.02em;
    margin: 0 auto 20px auto;
    max-width: 820px;
}

.hero-heading em {
    font-style: italic;
    font-family: 'Instrument Serif', 'Playfair Display', Georgia, serif;
    font-weight: 400;
    color: #121212;
}

.hero-description {
    font-size: 17px;
    line-height: 1.7;
    color: #666666;
    max-width: 620px;
    margin: 0 auto 30px auto;
    font-weight: 400;
}

/* --- Rotating Circular Stamp Badge --- */
.stamp-badge-wrap {
    position: absolute;
    top: 15px;
    right: 25px;
    width: 100px;
    height: 100px;
}

.rotating-stamp {
    width: 100%;
    height: 100%;
    animation: rotateStamp 22s linear infinite;
}

@keyframes rotateStamp {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}

.stamp-center-star {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    font-size: 18px;
    color: #121212;
}

/* --- Floating Hero Showcase --- */
.hero-stage {
    position: relative;
    max-width: 1000px;
    margin: 40px auto 30px auto;
    padding: 20px 0 30px 0;
}

/* Floating Glass Cards */
.glass-widget {
    background: rgba(255, 255, 255, 0.85);
    border: 1px solid rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-radius: 22px;
    padding: 20px 22px;
    box-shadow: 
        0 20px 40px -15px rgba(0, 0, 0, 0.05),
        0 0 1px 1px rgba(0, 0, 0, 0.03);
    text-align: left;
    transition: transform 0.3s ease;
}

.glass-widget:hover {
    transform: translateY(-3px);
}

.glass-widget h4 {
    font-size: 15.5px;
    font-weight: 600;
    color: #121212;
    margin: 8px 0 4px 0;
    letter-spacing: -0.01em;
}

.glass-widget p {
    font-size: 13px;
    color: #737373;
    line-height: 1.5;
    margin: 0;
}

/* Waveform Icon */
.soundwave-box {
    display: flex;
    align-items: center;
    gap: 3px;
    height: 24px;
    margin-bottom: 8px;
}

.soundwave-box span {
    display: block;
    width: 3px;
    background: #121212;
    border-radius: 3px;
}

.soundwave-box span:nth-child(1) { height: 10px; }
.soundwave-box span:nth-child(2) { height: 18px; }
.soundwave-box span:nth-child(3) { height: 24px; }
.soundwave-box span:nth-child(4) { height: 14px; }
.soundwave-box span:nth-child(5) { height: 8px; }

/* Avatars Stack */
.avatar-stack-wrap {
    display: flex;
    align-items: center;
    margin-bottom: 8px;
}

.avatar-circle {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    border: 2px solid #FFFFFF;
    margin-left: -7px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 11px;
    font-weight: 600;
    background-size: cover;
    background-position: center;
}

.avatar-circle:first-child {
    margin-left: 0;
}

.av-1 { background: #E4D8C9; color: #6E5C46; }
.av-2 { background: #D0DED5; color: #395B48; }
.av-3 { background: #D5DBE5; color: #43516B; }
.av-plus { 
    background: #121212; 
    color: #FFFFFF; 
    font-size: 10px; 
    font-weight: 700;
}

/* Central Composition */
.center-showcase-wrap {
    background: radial-gradient(circle at 50% 50%, rgba(255, 255, 255, 0.9) 0%, rgba(248, 246, 240, 0.7) 100%);
    border: 1px solid rgba(255, 255, 255, 0.95);
    border-radius: 32px;
    padding: 36px 30px;
    box-shadow: 
        0 25px 50px -20px rgba(0, 0, 0, 0.06),
        0 0 1px 1px rgba(0, 0, 0, 0.03);
    margin: 15px 0;
    position: relative;
    overflow: hidden;
}

.center-pill-cloud {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 14px;
    margin: 20px 0 15px 0;
}

.center-pill-item {
    background: rgba(255, 255, 255, 0.92);
    border: 1px solid rgba(0, 0, 0, 0.06);
    backdrop-filter: blur(12px);
    border-radius: 9999px;
    padding: 10px 22px;
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 14px;
    font-weight: 600;
    color: #121212;
    box-shadow: 0 8px 20px -8px rgba(0, 0, 0, 0.05);
}

.center-pill-item span.pill-sub {
    font-weight: 400;
    color: #737373;
    font-size: 12.5px;
}

/* Social Proof & Footer Badges in Hero */
.hero-footer-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-top: 25px;
    border-top: 1px solid rgba(0, 0, 0, 0.06);
    margin-top: 30px;
}

.hero-social-proof {
    display: flex;
    align-items: center;
    gap: 14px;
    text-align: left;
}

.hero-social-text {
    font-size: 13px;
    color: #666666;
    line-height: 1.4;
}

.hero-right-badge {
    text-align: right;
    font-size: 13.5px;
    color: #555555;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* --- Section Headings --- */
.section-header-wrap {
    text-align: center;
    margin: 60px 0 32px 0;
}

.section-tag {
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.12em;
    color: #8C8270;
    text-transform: uppercase;
    margin-bottom: 10px;
    display: inline-block;
}

.section-title-serif {
    font-family: 'Instrument Serif', 'Playfair Display', Georgia, serif;
    font-size: 38px;
    line-height: 1.2;
    color: #121212;
    font-weight: 400;
    margin: 0 0 10px 0;
}

.section-subtext {
    font-size: 15.5px;
    color: #6E6E6E;
    max-width: 580px;
    margin: 0 auto;
    line-height: 1.6;
}

/* --- Feature Cards Grid --- */
.feature-card-clean {
    background: #FFFFFF;
    border: 1px solid rgba(0, 0, 0, 0.06);
    border-radius: 24px;
    padding: 32px 28px;
    box-shadow: 0 12px 30px -10px rgba(0, 0, 0, 0.03);
    min-height: 220px;
    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    box-sizing: border-box;
}

.feature-card-clean:hover {
    transform: translateY(-3px);
    box-shadow: 0 18px 36px -12px rgba(0, 0, 0, 0.06);
    border-color: rgba(0, 0, 0, 0.1);
}

.feature-icon-pill {
    width: 44px;
    height: 44px;
    border-radius: 14px;
    background: #F5F4EE;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    margin-bottom: 20px;
    color: #121212;
}

.feature-card-clean h3 {
    font-size: 18.5px;
    font-weight: 600;
    color: #121212;
    margin: 0 0 10px 0;
    letter-spacing: -0.01em;
}

.feature-card-clean p {
    font-size: 14.5px;
    color: #666666;
    line-height: 1.65;
    margin: 0;
}

/* --- About Card --- */
.about-card-elegant {
    background: #FFFFFF;
    border: 1px solid rgba(0, 0, 0, 0.06);
    border-radius: 28px;
    padding: 44px 40px;
    box-shadow: 0 14px 36px -12px rgba(0, 0, 0, 0.04);
    margin: 40px 0 20px 0;
}

.about-quote {
    font-family: 'Instrument Serif', 'Playfair Display', Georgia, serif;
    font-size: 28px;
    line-height: 1.35;
    color: #121212;
    margin: 0 0 28px 0;
    font-weight: 400;
}

.about-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 32px;
    padding-top: 24px;
    border-top: 1px solid rgba(0, 0, 0, 0.06);
}

.about-col h4 {
    font-size: 16px;
    font-weight: 600;
    color: #121212;
    margin: 0 0 8px 0;
}

.about-col p {
    font-size: 14.5px;
    color: #666666;
    line-height: 1.7;
    margin: 0;
}

/* --- Clean Minimal Footer --- */
.minimal-footer {
    padding: 50px 0 20px 0;
    margin-top: 60px;
    border-top: 1px solid rgba(0, 0, 0, 0.06);
    text-align: center;
}

.footer-brand {
    font-size: 20px;
    font-weight: 700;
    letter-spacing: -0.02em;
    color: #121212;
    margin-bottom: 6px;
}

.footer-copy {
    font-size: 13.5px;
    color: #888888;
    line-height: 1.7;
}

/* --- Analysis Page Specifics --- */
div[data-testid="stFileUploader"] {
    background: #FFFFFF !important;
    border: 1.5px dashed #D9D5CA !important;
    border-radius: 22px !important;
    padding: 24px !important;
    box-shadow: 0 8px 24px -10px rgba(0, 0, 0, 0.03) !important;
    transition: all 0.25s ease !important;
}

div[data-testid="stFileUploader"]:hover {
    border-color: #121212 !important;
    background: #FFFEFA !important;
}

div[data-baseweb="textarea"] {
    background: #FFFFFF !important;
    border: 1px solid rgba(0, 0, 0, 0.08) !important;
    border-radius: 20px !important;
    box-shadow: 0 8px 24px -10px rgba(0, 0, 0, 0.03) !important;
    transition: all 0.2s ease !important;
}

div[data-baseweb="textarea"]:focus-within {
    border-color: #121212 !important;
    box-shadow: 0 0 0 3px rgba(18, 18, 18, 0.06) !important;
}

div[data-baseweb="textarea"] textarea {
    background: transparent !important;
    color: #121212 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 14.5px !important;
    line-height: 1.6 !important;
    padding: 18px !important;
}

/* Streamlit Native Metrics */
div[data-testid="stMetric"] {
    background: #FFFFFF !important;
    border: 1px solid rgba(0, 0, 0, 0.06) !important;
    border-radius: 20px !important;
    padding: 20px 24px !important;
    box-shadow: 0 8px 24px -10px rgba(0, 0, 0, 0.03) !important;
}

div[data-testid="stMetricLabel"] {
    color: #737373 !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.04em !important;
}

div[data-testid="stMetricValue"] {
    color: #121212 !important;
    font-family: 'Instrument Serif', Georgia, serif !important;
    font-size: 32px !important;
    font-weight: 400 !important;
}

/* Progress Bars */
div[data-testid="stProgressBar"] > div {
    background-color: #E8E5DD !important;
    border-radius: 9999px !important;
    height: 10px !important;
}

div[data-testid="stProgressBar"] div[role="progressbar"] > div {
    background: #121212 !important;
    border-radius: 9999px !important;
}

/* Expanders */
div[data-testid="stExpander"] {
    background: #FFFFFF !important;
    border: 1px solid rgba(0, 0, 0, 0.06) !important;
    border-radius: 18px !important;
    margin-bottom: 12px !important;
    box-shadow: 0 4px 16px -6px rgba(0, 0, 0, 0.02) !important;
    overflow: hidden !important;
}

/* Skill Badge Pills */
.skill-pill-matched {
    display: inline-block;
    background: #EBF7EE;
    color: #1C5430;
    border: 1px solid #D1EED8;
    border-radius: 9999px;
    padding: 7px 18px;
    margin: 4px;
    font-size: 13.5px;
    font-weight: 500;
    letter-spacing: -0.01em;
}

.skill-pill-missing {
    display: inline-block;
    background: #FFF4E5;
    color: #8C4E03;
    border: 1px solid #FFE2BB;
    border-radius: 9999px;
    padding: 7px 18px;
    margin: 4px;
    font-size: 13.5px;
    font-weight: 500;
    letter-spacing: -0.01em;
}

.skills-card-box {
    background: #FFFFFF;
    border: 1px solid rgba(0, 0, 0, 0.06);
    border-radius: 24px;
    padding: 24px 26px;
    box-shadow: 0 8px 24px -10px rgba(0, 0, 0, 0.03);
    min-height: 160px;
}

.skills-card-box h3 {
    font-size: 17px;
    font-weight: 600;
    margin: 0 0 16px 0;
    color: #121212;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* Editorial Content Card */
.editorial-card {
    background: #FFFFFF;
    border: 1px solid rgba(0, 0, 0, 0.06);
    border-radius: 24px;
    padding: 32px 30px;
    box-shadow: 0 8px 28px -10px rgba(0, 0, 0, 0.03);
    margin: 18px 0;
    line-height: 1.8;
    color: #333333;
}

.editorial-card h3 {
    font-family: 'Instrument Serif', Georgia, serif;
    font-size: 26px;
    font-weight: 400;
    color: #121212;
    margin-bottom: 16px;
}

</style>
""", unsafe_allow_html=True)


# ==========================================================
# 3. HTML HELPER
# ==========================================================

def show_html(content):
    st.html(content)


# ==========================================================
# 4. SESSION STATE
# ==========================================================

if "page" not in st.session_state:
    st.session_state.page = "Home"

if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None


# ==========================================================
# 5. CORE PARSER: PDF TEXT EXTRACTION (UNMODIFIED)
# ==========================================================

def extract_pdf_text(uploaded_file):
    pdf_bytes = uploaded_file.getvalue()
    with pymupdf.open(
        stream=pdf_bytes,
        filetype="pdf"
    ) as document:
        text = "\n".join(
            page.get_text("text")
            for page in document
        )
    return text.strip()


# ==========================================================
# 6. CORE PARSER: CANDIDATE INFORMATION (UNMODIFIED)
# ==========================================================

def extract_candidate_information(text):
    email_match = re.search(
        r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}',
        text
    )

    phone_match = re.search(
        r'(?<!\d)(?:\+?\d{1,3}[\s-]?)?(?:\d[\s-]?){9,12}(?!\d)',
        text
    )

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    candidate_name = "Not confidently identified"

    for line in lines[:5]:
        if (
            len(line.split()) <= 5
            and len(line) <= 60
            and not re.search(r'[@\d]', line)
            and not any(
                word in line.lower()
                for word in [
                    "resume",
                    "curriculum vitae",
                    "cv"
                ]
            )
        ):
            candidate_name = line
            break

    return {
        "name": candidate_name,
        "email": (
            email_match.group(0)
            if email_match else "Not found"
        ),
        "phone": (
            phone_match.group(0).strip()
            if phone_match else "Not found"
        )
    }


# ==========================================================
# 7. CORE MATCHER: NORMALIZE RESULTS (UNMODIFIED)
# ==========================================================

def normalize_match_data(data):
    if not isinstance(data, dict):
        raise ValueError(
            "calculate_match() must return a dictionary."
        )

    def safe_list(key):
        value = data.get(key, [])
        if isinstance(value, (list, tuple, set)):
            return list(value)
        return []

    raw_score = data.get("match_score")
    score = None

    if raw_score is not None:
        score = float(raw_score)
        score = max(0.0, min(score, 100.0))

    return {
        "match_score": score,
        "resume_skills": safe_list("resume_skills"),
        "required_skills": safe_list("required_skills"),
        "matched_skills": safe_list("matched_skills"),
        "missing_skills": safe_list("missing_skills"),
        "categorized_skills": data.get("categorized_skills", {}),
        "education": safe_list("education"),
        "experience": safe_list("experience"),
        "projects": safe_list("projects"),
        "certifications": safe_list("certifications"),
        "sections": data.get("sections", {}),
        "keyword_analysis": data.get("keyword_analysis", {}),
        "resume_quality": data.get(
            "resume_quality",
            data.get("quality", {})
        ),
        "recommendations": safe_list("recommendations")
    }


# ==========================================================
# 8. CORE REPORT: PDF GENERATOR (UNMODIFIED)
# ==========================================================

def create_pdf_report(candidate, match_data, ai_analysis):
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.platypus import (
            SimpleDocTemplate,
            Paragraph,
            Spacer,
            Table,
            TableStyle
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
                "<font color='#121212'><b>SOURA RESUME AI</b></font>",
                styles["Title"]
            )
        )

        story.append(
            Paragraph(
                "Professional Resume Analysis Report",
                styles["Heading2"]
            )
        )

        story.append(Spacer(1, 18))

        for label, value in [
            ("Candidate", candidate["name"]),
            ("Email", candidate["email"]),
            ("Phone", candidate["phone"])
        ]:
            story.append(
                Paragraph(
                    f"<b>{label}:</b> {escape(str(value))}",
                    styles["Normal"]
                )
            )

        story.append(Spacer(1, 15))

        score = match_data["match_score"]
        if score is None:
            score_text = "Not available"
        else:
            score_text = f"{score:.1f}%"

        story.append(
            Paragraph(
                f"<b>Job Skill Match:</b> {score_text}",
                styles["Heading2"]
            )
        )

        story.append(Spacer(1, 12))

        def add_section(title, items):
            story.append(
                Paragraph(
                    title,
                    styles["Heading2"]
                )
            )

            if items:
                for item in items:
                    story.append(
                        Paragraph(
                            "• " + escape(str(item)),
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

        add_section("Resume Skills", match_data["resume_skills"])
        add_section("Required Job Skills", match_data["required_skills"])
        add_section("Matched Skills", match_data["matched_skills"])
        add_section("Missing Skills", match_data["missing_skills"])
        add_section("Education", match_data["education"])
        add_section("Experience", match_data["experience"])
        add_section("Projects", match_data["projects"])
        add_section("Certifications", match_data["certifications"])
        add_section("Recommendations", match_data["recommendations"])

        story.append(
            Paragraph(
                "Gemma AI Detailed Analysis",
                styles["Heading2"]
            )
        )

        for line in ai_analysis.splitlines():
            line = line.strip()
            if line:
                story.append(
                    Paragraph(
                        escape(line),
                        styles["Normal"]
                    )
                )
                story.append(Spacer(1, 5))

        story.append(Spacer(1, 15))

        story.append(
            Paragraph(
                "<i>AI-generated report. Results are estimates "
                "and should be reviewed by the candidate.</i>",
                styles["Italic"]
            )
        )

        document.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    except ImportError:
        return None


# ==========================================================
# 9. HEADER / NAVBAR (MINDLY STYLE)
# ==========================================================

nav_col1, nav_col2, nav_col3 = st.columns([2.6, 2.2, 1.2], vertical_alignment="center")

with nav_col1:
    show_html("""
        <div class="brand-wrap">
            <span>Soura AI</span><span class="brand-dot">°</span>
        </div>
    """)

with nav_col2:
    n1, n2 = st.columns(2)
    with n1:
        if st.button("Overview", key="top_nav_home", use_container_width=True, type="secondary"):
            st.session_state.page = "Home"
            st.rerun()
    with n2:
        if st.button("Analysis", key="top_nav_analysis", use_container_width=True, type="secondary"):
            st.session_state.page = "Analysis"
            st.rerun()

with nav_col3:
    if st.button("Get started ↗", key="top_nav_get_started", use_container_width=True, type="primary"):
        st.session_state.page = "Analysis"
        st.rerun()


# ==========================================================
# 10. HOMEPAGE VIEW (MINDLY AESTHETIC HERO & SECTIONS)
# ==========================================================

if st.session_state.page == "Home":

    # Hero Main Section
    show_html("""
        <div class="hero-container">

            <div class="stamp-badge-wrap">
                <svg viewBox="0 0 120 120" class="rotating-stamp">
                    <path id="stampCircle" d="M 60,60 m -44,0 a 44,44 0 1,1 88,0 a 44,44 0 1,1 -88,0" fill="none" />
                    <text font-size="10.2" letter-spacing="2.2" fill="#777777" font-family="'Plus Jakarta Sans', sans-serif" font-weight="600">
                        <textPath href="#stampCircle" startOffset="0%">
                            ✦ A SMARTER RESUME EVERYDAY ✦
                        </textPath>
                    </text>
                </svg>
                <div class="stamp-center-star">✦</div>
            </div>

            <div class="hero-pill-badge">
                ✦ AI-Powered Career Intelligence
            </div>

            <h1 class="hero-heading">
                A sharper resume<br>
                <em>for a brighter you.</em>
            </h1>

            <p class="hero-description">
                Soura AI helps you capture your professional value, organize your skills,
                and align with your target job — all in one calm, intelligent space.
            </p>

        </div>
    """)

    # Hero Action Buttons
    b_col1, b_col2, b_col3 = st.columns([1.6, 1.2, 1.6])
    with b_col2:
        if st.button("Get started free →", key="hero_cta_btn", use_container_width=True, type="primary"):
            st.session_state.page = "Analysis"
            st.rerun()

    # Floating 3D Showcase (Centerpiece inspired by Mindly artwork)
    show_html("""
        <div class="hero-stage">
            <div style="display: grid; grid-template-columns: 260px 1fr 260px; gap: 20px; align-items: center;">

                <!-- Floating Left Card -->
                <div class="glass-widget">
                    <div class="soundwave-box">
                        <span></span><span></span><span></span><span></span><span></span>
                    </div>
                    <h4>Turn skills into leverage.</h4>
                    <p>Detect keyword alignment and close critical gaps effortlessly.</p>
                </div>

                <!-- Center Showcase -->
                <div class="center-showcase-wrap">
                    <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.12em; color: #8C8270; font-weight: 700; text-align: center;">
                        INTELLIGENT PROFILE BENCHMARK
                    </div>
                    <div class="center-pill-cloud">
                        <div class="center-pill-item">
                            <span>🎯 Target Match</span>
                            <span class="pill-sub">ATS Precision</span>
                        </div>
                        <div class="center-pill-item">
                            <span>✦ 94% Suitability</span>
                            <span class="pill-sub">Top Tier</span>
                        </div>
                        <div class="center-pill-item">
                            <span>⚡ Gemma AI</span>
                            <span class="pill-sub">Action Plan</span>
                        </div>
                    </div>
                    <div style="text-align: center; color: #737373; font-size: 13.5px; margin-top: 14px;">
                        Instant semantic extraction across 1,000+ industry job descriptions.
                    </div>
                </div>

                <!-- Floating Right Card -->
                <div class="glass-widget">
                    <div class="avatar-stack-wrap">
                        <span class="avatar-circle av-1">JS</span>
                        <span class="avatar-circle av-2">MR</span>
                        <span class="avatar-circle av-3">AL</span>
                        <span class="avatar-circle av-plus">+</span>
                    </div>
                    <h4>Insights, anytime, anywhere.</h4>
                    <p>Comprehensive evaluations ready before your next interview.</p>
                </div>

            </div>

            <!-- Hero Footer Bar (Social Proof & Tagline) -->
            <div class="hero-footer-bar">
                <div class="hero-social-proof">
                    <div class="avatar-stack-wrap" style="margin-bottom: 0;">
                        <span class="avatar-circle av-1">DA</span>
                        <span class="avatar-circle av-2">SK</span>
                        <span class="avatar-circle av-3">EM</span>
                        <span class="avatar-circle av-plus">+</span>
                    </div>
                    <div class="hero-social-text">
                        <strong>Trusted by 50,000+ candidates</strong><br>
                        preparing for top engineering & leadership roles worldwide.
                    </div>
                </div>
                <div class="hero-right-badge">
                    <span>✦</span>
                    <div>
                        Less guesswork.<br>
                        <strong>More clarity.</strong>
                    </div>
                </div>
            </div>

        </div>
    """)

    # Features Section
    show_html("""
        <div class="section-header-wrap">
            <span class="section-tag">CAPABILITIES</span>
            <h2 class="section-title-serif">A clearer path to your next breakthrough</h2>
            <p class="section-subtext">Everything you need to evaluate, optimize, and elevate your professional career narrative.</p>
        </div>
    """)

    fc1, fc2, fc3 = st.columns(3)

    with fc1:
        show_html("""
            <div class="feature-card-clean">
                <div class="feature-icon-pill">📄</div>
                <h3>Resume Intelligence</h3>
                <p>
                    Precision extraction of candidate details, education, career experience, 
                    and core technical proficiencies directly from your PDF.
                </p>
            </div>
        """)

    with fc2:
        show_html("""
            <div class="feature-card-clean">
                <div class="feature-icon-pill">🎯</div>
                <h3>Job Match Analysis</h3>
                <p>
                    Compare your profile against target job descriptions to calculate 
                    exact skill overlaps and uncover crucial missing requirements.
                </p>
            </div>
        """)

    with fc3:
        show_html("""
            <div class="feature-card-clean">
                <div class="feature-icon-pill">✦</div>
                <h3>Gemma AI Insights</h3>
                <p>
                    Receive customized, actionable recommendations from local Gemma intelligence 
                    to maximize interview readiness and ATS compatibility.
                </p>
            </div>
        """)

    # About Card
    show_html("""
        <div class="about-card-elegant">
            <span class="section-tag">OUR PHILOSOPHY</span>
            <div class="about-quote">
                “Empowering ambitious professionals to step into every interview with clarity, precision, and confidence.”
            </div>
            <div class="about-grid">
                <div class="about-col">
                    <h4>Intelligent Career Preparation</h4>
                    <p>
                        Soura Resume AI combines advanced natural language processing with local LLM 
                        reasoning to deliver an objective audit of your qualifications before recruiters review your application.
                    </p>
                </div>
                <div class="about-col">
                    <h4>Our Mission</h4>
                    <p>
                        To eliminate hiring ambiguity by providing transparent skill matching, 
                        constructive feedback, and clear roadmaps for professional growth.
                    </p>
                </div>
            </div>
        </div>
    """)

    # Footer
    show_html("""
        <div class="minimal-footer">
            <div class="footer-brand">
                Soura AI<span style="font-size: 13px;">°</span>
            </div>
            <div class="footer-copy">
                Your resume. Your skills. Your next opportunity.<br>
                © 2026 Soura Resume AI. All rights reserved. • souradeepsaha190@gmail.com
            </div>
        </div>
    """)


# ==========================================================
# 11. ANALYSIS PAGE (MINDLY STYLE INPUT & RESULTS)
# ==========================================================

if st.session_state.page == "Analysis":

    show_html("""
        <div class="section-header-wrap" style="margin-top: 20px; margin-bottom: 25px;">
            <span class="section-tag">RESUME EVALUATION</span>
            <h1 class="hero-heading" style="font-size: 50px; margin-bottom: 12px;">
                Resume Analysis<br>
                <em>and job alignment.</em>
            </h1>
            <p class="section-subtext">
                Upload your PDF resume and provide your target job description for instant ATS matching and Gemma AI feedback.
            </p>
        </div>
    """)

    in_col1, in_col2 = st.columns([1, 1])

    with in_col1:
        uploaded_file = st.file_uploader(
            "Upload Your Resume (PDF)",
            type=["pdf"],
            help="Upload a text-based PDF resume."
        )

    with in_col2:
        job_description = st.text_area(
            "Target Job Description",
            placeholder=(
                "Paste the complete job description here, including "
                "job title, required skills, responsibilities and qualifications..."
            ),
            height=200
        )

    analyse_button = st.button(
        "Analyse My Resume →",
        type="primary",
        use_container_width=True
    )

    if analyse_button:
        # Clear old results so an unsuccessful analysis cannot accidentally display an older result.
        st.session_state.analysis_result = None

        if uploaded_file is None:
            st.error("Please upload your PDF resume.")
        elif not job_description.strip():
            st.error("Please enter a job description.")
        else:
            try:
                with st.spinner("Analyzing your resume against target requirements with Gemma AI..."):
                    # STEP 1: EXTRACT PDF TEXT
                    resume_text = extract_pdf_text(uploaded_file)

                    if not resume_text:
                        raise ValueError(
                            "No readable text was found in the PDF. "
                            "Scanned PDFs require OCR."
                        )

                    # STEP 2: EXTRACT CANDIDATE DETAILS
                    candidate = extract_candidate_information(resume_text)

                    # STEP 3: RUN SKILL MATCHING
                    raw_match_data = calculate_match(
                        resume_text,
                        job_description
                    )

                    # STEP 4: NORMALIZE MATCHING RESULTS
                    match_data = normalize_match_data(raw_match_data)

                    # STEP 5: CHECK MATCHER OUTPUT
                    if match_data["required_skills"]:
                        matched_set = set(match_data["matched_skills"])
                        required_set = set(match_data["required_skills"])

                        matched = [
                            skill
                            for skill in match_data["required_skills"]
                            if skill in matched_set
                        ]

                        missing = [
                            skill
                            for skill in match_data["required_skills"]
                            if skill not in matched_set
                        ]

                        match_data["matched_skills"] = matched
                        match_data["missing_skills"] = missing
                        match_data["match_score"] = round(
                            len(matched) / len(required_set) * 100,
                            2
                        )
                    else:
                        match_data["match_score"] = None
                        match_data["matched_skills"] = []
                        match_data["missing_skills"] = []

                    # STEP 6: RUN GEMMA AI ANALYSIS
                    ai_analysis = analyse_resume(
                        resume_text,
                        job_description
                    )

                    if not isinstance(ai_analysis, str):
                        raise ValueError("Gemma AI did not return a valid text response.")

                    if not ai_analysis.strip():
                        raise ValueError("Gemma AI returned an empty analysis.")

                    # STEP 7: SAVE ALL RESULTS
                    st.session_state.analysis_result = {
                        "candidate": candidate,
                        "match_data": match_data,
                        "ai_analysis": ai_analysis,
                        "filename": uploaded_file.name,
                        "created_at": datetime.now().strftime("%d %b %Y, %I:%M %p")
                    }

                st.success("Resume analysis completed successfully!")

            except Exception as error:
                st.session_state.analysis_result = None
                st.error(f"Analysis failed: {type(error).__name__}: {error}")
                st.info(
                    "Check whether Ollama is running and whether "
                    "matcher.py and llm_analyzer.py are configured correctly."
                )


# ==========================================================
# 12. DISPLAY RESULTS DASHBOARD
# ==========================================================

result = st.session_state.analysis_result

if (
    st.session_state.page == "Analysis"
    and result is not None
):
    candidate = result["candidate"]
    data = result["match_data"]
    matched = data["matched_skills"]
    missing = data["missing_skills"]
    required = data["required_skills"]
    resume_skills = data["resume_skills"]

    # ------------------------------------------------------
    # CANDIDATE INFORMATION CARDS
    # ------------------------------------------------------
    st.markdown("---")
    show_html("""
        <div style="margin: 25px 0 15px 0;">
            <span class="section-tag">PROFILE AUDIT</span>
            <h2 class="section-title-serif" style="font-size: 32px;">Candidate Profile</h2>
        </div>
    """)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Candidate Name", candidate["name"])

    with col2:
        st.metric("Email Address", candidate["email"])

    with col3:
        st.metric("Contact Phone", candidate["phone"])

    st.caption(
        f"Document: {result['filename']} | Analysed: {result['created_at']}"
    )

    # ------------------------------------------------------
    # JOB SUITABILITY SCORE
    # ------------------------------------------------------
    st.markdown("---")
    show_html("""
        <div style="margin: 25px 0 15px 0;">
            <span class="section-tag">ALIGNMENT</span>
            <h2 class="section-title-serif" style="font-size: 32px;">Job Suitability Score</h2>
        </div>
    """)

    score = data["match_score"]

    if required and score is not None:
        st.metric("Recognised Job Skill Match", f"{score:.1f}%")

        st.progress(
            int(score),
            text=f"{score:.1f}% of recognised required skills matched"
        )

        st.caption(
            f"Matched: {len(matched)} | Missing: {len(missing)} | Total Required: {len(required)}"
        )

        st.info(
            "This is a keyword and semantic skill match estimate, "
            "not a guaranteed ATS score or hiring decision."
        )
    else:
        st.warning(
            "A skill match score is unavailable because "
            "no recognised skills were detected in the target job description."
        )
        st.write(
            "Gemma AI analysis is still available below. "
            "Try including specific required skills in your job description."
        )

    # ------------------------------------------------------
    # SKILL ANALYSIS (TAG CHIPS AESTHETIC)
    # ------------------------------------------------------
    st.markdown("---")
    show_html("""
        <div style="margin: 25px 0 15px 0;">
            <span class="section-tag">COMPETENCY COMPARISON</span>
            <h2 class="section-title-serif" style="font-size: 32px;">Skill Analysis</h2>
        </div>
    """)

    sk_col1, sk_col2 = st.columns(2)

    with sk_col1:
        show_html("""
            <div class="skills-card-box">
                <h3><span style="color:#1C5430;">●</span> Matched Skills</h3>
        """)
        if matched:
            matched_html = "".join([f'<span class="skill-pill-matched">✓ {escape(str(s))}</span>' for s in matched])
            show_html(f'<div>{matched_html}</div></div>')
        else:
            show_html('<p style="color:#777;">No matched skills identified.</p></div>')

    with sk_col2:
        show_html("""
            <div class="skills-card-box">
                <h3><span style="color:#8C4E03;">●</span> Missing Skills</h3>
        """)
        if missing:
            missing_html = "".join([f'<span class="skill-pill-missing">✕ {escape(str(s))}</span>' for s in missing])
            show_html(f'<div>{missing_html}</div></div>')
        else:
            if required:
                show_html('<p style="color:#1C5430; font-weight:500;">✓ All recognised required skills are present in resume.</p></div>')
            else:
                show_html('<p style="color:#777;">No recognised job skills available for comparison.</p></div>')

    # ------------------------------------------------------
    # VISUAL SKILL ANALYSIS (PLOTLY CHART)
    # ------------------------------------------------------
    st.markdown("---")
    show_html("""
        <div style="margin: 25px 0 15px 0;">
            <span class="section-tag">DATA VISUALIZATION</span>
            <h2 class="section-title-serif" style="font-size: 32px;">Visual Skill Comparison</h2>
        </div>
    """)

    if required:
        chart = go.Figure()

        chart.add_trace(
            go.Bar(
                name="Matched Skills",
                x=["Skills Breakdown"],
                y=[len(matched)],
                marker_color="#121212",
                text=[len(matched)],
                textposition="inside",
                insidetextfont=dict(color="#FFFFFF", size=14, family="Plus Jakarta Sans")
            )
        )

        chart.add_trace(
            go.Bar(
                name="Missing Skills",
                x=["Skills Breakdown"],
                y=[len(missing)],
                marker_color="#C4883A",
                text=[len(missing)],
                textposition="inside",
                insidetextfont=dict(color="#FFFFFF", size=14, family="Plus Jakarta Sans")
            )
        )

        chart.update_layout(
            barmode="group",
            paper_bgcolor="#FAF9F5",
            plot_bgcolor="#FFFFFF",
            font=dict(
                color="#121212",
                family="Plus Jakarta Sans, sans-serif"
            ),
            yaxis_title="Number of Skills",
            xaxis_title="",
            height=340,
            margin=dict(l=35, r=25, t=30, b=30),
            legend=dict(
                orientation="h",
                y=1.12,
                x=0,
                font=dict(size=12)
            ),
            bargap=0.35,
            bargroupgap=0.1
        )

        chart.update_yaxes(
            rangemode="tozero",
            dtick=1,
            gridcolor="#EAE7DF"
        )

        st.plotly_chart(
            chart,
            use_container_width=True,
            config={"displayModeBar": False}
        )
    else:
        st.info("The skill chart will appear when recognised job requirements are available.")

    # ------------------------------------------------------
    # ALL SKILLS EXPANDERS
    # ------------------------------------------------------
    with st.expander("View all detected resume skills"):
        if resume_skills:
            st.write(resume_skills)
        else:
            st.info("No recognised skills detected.")

    with st.expander("View all required job skills"):
        if required:
            st.write(required)
        else:
            st.info("No recognised job skills detected.")

    # ------------------------------------------------------
    # SKILLS BY CATEGORY
    # ------------------------------------------------------
    st.markdown("---")
    show_html("""
        <div style="margin: 25px 0 15px 0;">
            <span class="section-tag">TAXONOMY</span>
            <h2 class="section-title-serif" style="font-size: 32px;">Skills by Category</h2>
        </div>
    """)

    categories = data["categorized_skills"]

    if categories:
        for category, skills in categories.items():
            with st.expander(category):
                st.write(", ".join(skills))
    else:
        st.info("No skills were detected by category.")

    # ------------------------------------------------------
    # EDUCATION
    # ------------------------------------------------------
    st.markdown("---")
    show_html("""
        <div style="margin: 25px 0 15px 0;">
            <span class="section-tag">BACKGROUND</span>
            <h2 class="section-title-serif" style="font-size: 32px;">Education Analysis</h2>
        </div>
    """)

    if data["education"]:
        for item in data["education"]:
            st.write(f"🎓 {item}")
    else:
        st.info("No education entries were detected under a recognised heading.")

    # ------------------------------------------------------
    # EXPERIENCE
    # ------------------------------------------------------
    st.markdown("---")
    show_html("""
        <div style="margin: 25px 0 15px 0;">
            <span class="section-tag">CAREER HISTORY</span>
            <h2 class="section-title-serif" style="font-size: 32px;">Work Experience Analysis</h2>
        </div>
    """)

    if data["experience"]:
        for item in data["experience"]:
            st.write(f"💼 {item}")
    else:
        st.info("No dated experience entries were detected. Check the resume's Experience section formatting.")

    # ------------------------------------------------------
    # PROJECTS
    # ------------------------------------------------------
    st.markdown("---")
    show_html("""
        <div style="margin: 25px 0 15px 0;">
            <span class="section-tag">PORTFOLIO</span>
            <h2 class="section-title-serif" style="font-size: 32px;">Projects</h2>
        </div>
    """)

    if data["projects"]:
        for item in data["projects"]:
            st.write(f"📌 {item}")
    else:
        st.info("No project entries detected under a Projects heading.")

    # ------------------------------------------------------
    # CERTIFICATIONS
    # ------------------------------------------------------
    st.markdown("---")
    show_html("""
        <div style="margin: 25px 0 15px 0;">
            <span class="section-tag">CREDENTIALS</span>
            <h2 class="section-title-serif" style="font-size: 32px;">Certifications</h2>
        </div>
    """)

    if data["certifications"]:
        for item in data["certifications"]:
            st.write(f"🏅 {item}")
    else:
        st.info("No certification entries detected under a Certifications heading.")

    # ------------------------------------------------------
    # RESUME QUALITY
    # ------------------------------------------------------
    st.markdown("---")
    show_html("""
        <div style="margin: 25px 0 15px 0;">
            <span class="section-tag">COMPLETENESS AUDIT</span>
            <h2 class="section-title-serif" style="font-size: 32px;">Resume Quality Indicators</h2>
        </div>
    """)

    quality = data["resume_quality"]

    if quality:
        quality_score = quality.get("quality_score")
        if quality_score is not None:
            st.metric(
                "Section and Contact Completeness",
                f"{quality_score:.1f}%"
            )
            st.progress(int(max(0, min(quality_score, 100))))

        word_count = quality.get("word_count")
        if word_count is not None:
            st.write(f"**Word count:** {word_count}")

        length_status = quality.get("length_status")
        if length_status:
            st.write(f"**Length assessment:** {length_status}")

        checks = quality.get("checks", {})
        if checks:
            st.markdown("### Resume Checklist")
            for item, passed in checks.items():
                if passed:
                    st.success(item)
                else:
                    st.warning(f"{item} not detected")

        st.caption(
            "This completeness indicator checks the presence "
            "of sections and contact details. It is not an ATS score."
        )
    else:
        st.info("Resume quality indicators are not available.")

    # ------------------------------------------------------
    # RECOMMENDATIONS
    # ------------------------------------------------------
    st.markdown("---")
    show_html("""
        <div style="margin: 25px 0 15px 0;">
            <span class="section-tag">ACTION PLAN</span>
            <h2 class="section-title-serif" style="font-size: 32px;">Improvement Recommendations</h2>
        </div>
    """)

    if data["recommendations"]:
        for recommendation in data["recommendations"]:
            st.write(f"💡 {recommendation}")
    else:
        st.info("No additional recommendations were generated.")

    # ------------------------------------------------------
    # GEMMA AI DETAILED ANALYSIS
    # ------------------------------------------------------
    st.markdown("---")
    show_html("""
        <div style="margin: 25px 0 15px 0;">
            <span class="section-tag">INTELLIGENCE REPORT</span>
            <h2 class="section-title-serif" style="font-size: 32px;">Gemma AI Detailed Analysis</h2>
        </div>
    """)

    show_html("""
        <div class="editorial-card">
    """)
    st.markdown(result["ai_analysis"])
    show_html("</div>")

    # ------------------------------------------------------
    # PDF REPORT DOWNLOAD
    # ------------------------------------------------------
    st.markdown("---")
    show_html("""
        <div style="margin: 25px 0 15px 0;">
            <span class="section-tag">EXPORT</span>
            <h2 class="section-title-serif" style="font-size: 32px;">Download Your Analysis Report</h2>
        </div>
    """)

    pdf_report = create_pdf_report(
        candidate,
        data,
        result["ai_analysis"]
    )

    if pdf_report:
        st.download_button(
            label="Download Professional PDF Report ↓",
            data=pdf_report,
            file_name="Soura_Resume_AI_Report.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    else:
        st.warning("ReportLab is not installed.")

    # ------------------------------------------------------
    # CLEAR RESULTS
    # ------------------------------------------------------
    if st.button("Start New Analysis", type="secondary"):
        st.session_state.analysis_result = None
        st.rerun()

    # Footer
    show_html("""
        <div class="minimal-footer">
            <div class="footer-brand">
                Soura AI<span style="font-size: 13px;">°</span>
            </div>
            <div class="footer-copy">
                Your resume. Your skills. Your next opportunity.<br>
                © 2026 Soura Resume AI. All rights reserved.
            </div>
        </div>
    """)
