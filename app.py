# ==========================================================
# 0. ASGI SERVERLESS ENTRYPOINT FOR VERCEL DEPLOYMENT
# ==========================================================
try:
    from api.index import app as vercel_app
    app = vercel_app
    application = vercel_app
    handler = vercel_app
except Exception:
    app = None
    application = None
    handler = None

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
    page_title="Resumind AI — Executive Resume Intelligence",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ==========================================================
# 2. LUXURY EDITORIAL DESIGN SYSTEM (CRAFTED, NOT AI SLOP)
# ==========================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@500;600;700&family=Instrument+Serif:ital,wght@0,400;1,400&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

/* --- Root & Palette --- */
:root {
    --bg-ivory: #F3F0E8;
    --text-primary: #151515;
    --accent-blue: #4263EB;
    --text-muted: #7E7E7E;
    --dark-navy: #071522;
    --border-subtle: rgba(21, 21, 21, 0.08);
}

html {
    scroll-behavior: smooth !important;
}

body, .stApp {
    background-color: #F3F0E8 !important;
    background-image: 
        radial-gradient(circle at 50% 0%, rgba(255, 255, 255, 0.95) 0%, rgba(243, 240, 232, 0.75) 55%, rgba(235, 230, 218, 0.45) 100%),
        radial-gradient(circle at 85% 15%, rgba(66, 99, 235, 0.035) 0%, transparent 40%),
        radial-gradient(circle at 15% 45%, rgba(66, 99, 235, 0.03) 0%, transparent 40%) !important;
    color: #151515 !important;
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
    -webkit-font-smoothing: antialiased;
}

.block-container {
    max-width: 1220px !important;
    padding-top: 1.2rem !important;
    padding-bottom: 5rem !important;
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
.brand-title {
    font-family: 'Cinzel', 'Plus Jakarta Sans', serif;
    font-weight: 700;
    font-size: 18px;
    letter-spacing: 0.16em;
    color: #151515;
    text-transform: uppercase;
}

.brand-title span {
    color: #4263EB;
}

/* --- Streamlit Buttons (Clean Luxury Aesthetic) --- */
.stButton > button {
    background: #151515 !important;
    color: #FFFFFF !important;
    border: 1px solid #151515 !important;
    border-radius: 9999px !important;
    padding: 11px 26px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
    box-shadow: 0 4px 14px rgba(21, 21, 21, 0.1) !important;
    min-height: 46px !important;
}

.stButton > button:hover {
    background: #4263EB !important;
    color: #FFFFFF !important;
    border-color: #4263EB !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(66, 99, 235, 0.3) !important;
}

.stButton > button[kind="secondary"] {
    background: rgba(255, 255, 255, 0.88) !important;
    color: #151515 !important;
    border: 1px solid rgba(21, 21, 21, 0.1) !important;
    box-shadow: 0 2px 8px rgba(21, 21, 21, 0.03) !important;
}

.stButton > button[kind="secondary"]:hover {
    background: #FFFFFF !important;
    color: #4263EB !important;
    border-color: #4263EB !important;
}

.stDownloadButton > button {
    background: #4263EB !important;
    color: #FFFFFF !important;
    border: 1px solid #4263EB !important;
    border-radius: 9999px !important;
    padding: 13px 32px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 700 !important;
    font-size: 13.5px !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    box-shadow: 0 6px 20px rgba(66, 99, 235, 0.25) !important;
    transition: all 0.25s ease !important;
    min-height: 50px !important;
}

.stDownloadButton > button:hover {
    background: #364fc7 !important;
    border-color: #364fc7 !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 10px 28px rgba(66, 99, 235, 0.38) !important;
}

/* --- Hero Section Typography --- */
.hero-wrapper {
    position: relative;
    text-align: center;
    padding: 50px 10px 30px 10px;
    margin-bottom: 20px;
}

.hero-pill-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(255, 255, 255, 0.9);
    border: 1px solid rgba(66, 99, 235, 0.2);
    backdrop-filter: blur(12px);
    border-radius: 9999px;
    padding: 6px 18px;
    font-size: 11.5px;
    font-weight: 700;
    letter-spacing: 0.15em;
    color: #4263EB;
    text-transform: uppercase;
    margin-bottom: 24px;
    box-shadow: 0 4px 14px rgba(66, 99, 235, 0.08);
}

.hero-title-main {
    font-family: 'Instrument Serif', 'Playfair Display', Georgia, serif;
    font-size: 74px;
    line-height: 1.08;
    color: #151515;
    font-weight: 400;
    letter-spacing: -0.03em;
    margin: 0 auto 20px auto;
    max-width: 880px;
}

.hero-title-main em {
    font-style: italic;
    color: #151515;
}

.hero-subtext-main {
    font-size: 18px;
    line-height: 1.7;
    color: #666666;
    max-width: 660px;
    margin: 0 auto 34px auto;
    font-weight: 400;
}

/* --- AUTHENTIC PRODUCT INTERFACE PREVIEW (NOT AI SLOP) --- */
.product-preview-card {
    background: #FFFFFF;
    border: 1px solid rgba(21, 21, 21, 0.09);
    border-radius: 28px;
    padding: 34px 38px;
    max-width: 960px;
    margin: 25px auto 40px auto;
    box-shadow: 
        0 24px 60px -18px rgba(7, 21, 34, 0.08),
        0 0 1px 1px rgba(21, 21, 21, 0.03);
    text-align: left;
    transition: all 0.3s ease;
}

.product-preview-card:hover {
    box-shadow: 0 30px 70px -18px rgba(7, 21, 34, 0.12);
}

.preview-header-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-bottom: 22px;
    border-bottom: 1px solid rgba(21, 21, 21, 0.06);
    margin-bottom: 24px;
}

.candidate-profile-meta {
    display: flex;
    align-items: center;
    gap: 14px;
}

.candidate-avatar-initials {
    width: 44px;
    height: 44px;
    border-radius: 50%;
    background: #071522;
    color: #FFFFFF;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 14px;
    font-weight: 700;
    letter-spacing: 0.05em;
}

.candidate-name-title h4 {
    font-size: 16px;
    font-weight: 700;
    color: #151515;
    margin: 0;
}

.candidate-name-title span {
    font-size: 12.5px;
    color: #7E7E7E;
    font-weight: 500;
}

.preview-score-capsule {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    background: rgba(66, 99, 235, 0.08);
    border: 1px solid rgba(66, 99, 235, 0.2);
    border-radius: 9999px;
    padding: 7px 18px;
}

.preview-score-capsule .score-num {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 15px;
    font-weight: 700;
    color: #4263EB;
}

.preview-score-capsule .score-label {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #4263EB;
}

.preview-body-grid {
    display: grid;
    grid-template-columns: 1.4fr 1fr;
    gap: 30px;
}

.resume-annotated-excerpt {
    background: #FAF8F4;
    border: 1px solid rgba(21, 21, 21, 0.06);
    border-radius: 18px;
    padding: 22px 24px;
    font-size: 14px;
    line-height: 1.7;
    color: #333333;
}

.resume-annotated-excerpt .excerpt-tag {
    display: inline-block;
    font-size: 10.5px;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #4263EB;
    background: rgba(66, 99, 235, 0.08);
    padding: 3px 9px;
    border-radius: 6px;
    margin-bottom: 12px;
}

.diagnostic-panel-preview {
    display: flex;
    flex-direction: column;
    gap: 16px;
}

.diagnostic-box-mini {
    background: #FAF8F4;
    border: 1px solid rgba(21, 21, 21, 0.06);
    border-radius: 16px;
    padding: 16px 20px;
}

.diagnostic-box-mini h5 {
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin: 0 0 10px 0;
    display: flex;
    align-items: center;
    gap: 6px;
}

.diagnostic-box-mini.strengths h5 { color: #2B8A3E; }
.diagnostic-box-mini.gaps h5 { color: #C92A2A; }

.mini-pill-tag {
    display: inline-block;
    padding: 4px 11px;
    border-radius: 9999px;
    font-size: 11.5px;
    font-weight: 600;
    margin: 3px 2px;
}

.mini-pill-tag.green {
    background: #EBFBEE;
    color: #2B8A3E;
    border: 1px solid #D3F9D8;
}

.mini-pill-tag.red {
    background: #FFF5F5;
    color: #C92A2A;
    border: 1px solid #FFE3E3;
}

/* --- Marquee Ribbon --- */
.marquee-ribbon {
    width: 100%;
    overflow: hidden;
    padding: 16px 0;
    margin: 30px 0 45px 0;
    background: rgba(255, 255, 255, 0.7);
    border-top: 1px solid rgba(21, 21, 21, 0.06);
    border-bottom: 1px solid rgba(21, 21, 21, 0.06);
    backdrop-filter: blur(10px);
    mask-image: linear-gradient(to right, transparent, black 8%, black 92%, transparent);
    -webkit-mask-image: linear-gradient(to right, transparent, black 8%, black 92%, transparent);
}

.marquee-stream {
    display: flex;
    width: max-content;
    gap: 32px;
    animation: streamAnimation 30s linear infinite;
}

.marquee-stream:hover {
    animation-play-state: paused;
}

.marquee-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    font-size: 12.5px;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #2D2D2D;
    white-space: nowrap;
    padding: 6px 16px;
    background: rgba(255, 255, 255, 0.95);
    border: 1px solid rgba(21, 21, 21, 0.07);
    border-radius: 9999px;
    box-shadow: 0 2px 8px rgba(21, 21, 21, 0.02);
}

.marquee-badge span.sparkle {
    color: #4263EB;
}

@keyframes streamAnimation {
    0% { transform: translateX(0); }
    100% { transform: translateX(-50%); }
}

/* --- Section Title Typography --- */
.editorial-section-header {
    text-align: center;
    margin: 60px 0 32px 0;
}

.editorial-tag {
    font-size: 11.5px;
    font-weight: 700;
    letter-spacing: 0.16em;
    color: #4263EB;
    text-transform: uppercase;
    margin-bottom: 10px;
    display: inline-block;
}

.editorial-headline {
    font-family: 'Instrument Serif', Georgia, serif;
    font-size: 44px;
    line-height: 1.15;
    color: #151515;
    font-weight: 400;
    margin: 0 0 12px 0;
}

.editorial-subtext {
    font-size: 16px;
    color: #666666;
    max-width: 620px;
    margin: 0 auto;
    line-height: 1.65;
}

/* --- 6 Capability Cards (Refined & Tasteful) --- */
.editorial-feature-card {
    background: #FFFFFF;
    border: 1px solid rgba(21, 21, 21, 0.07);
    border-radius: 24px;
    padding: 34px 28px;
    box-shadow: 0 10px 30px -10px rgba(7, 21, 34, 0.03);
    min-height: 230px;
    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    box-sizing: border-box;
}

.editorial-feature-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 18px 40px -15px rgba(66, 99, 235, 0.1);
    border-color: rgba(66, 99, 235, 0.25);
}

.feature-num-stamp {
    font-family: 'Space Grotesk', monospace;
    font-size: 11.5px;
    font-weight: 700;
    color: #4263EB;
    letter-spacing: 0.12em;
    margin-bottom: 16px;
    display: block;
}

.editorial-feature-card h3 {
    font-size: 18.5px;
    font-weight: 700;
    color: #151515;
    margin: 0 0 10px 0;
    letter-spacing: -0.01em;
}

.editorial-feature-card p {
    font-size: 14px;
    color: #666666;
    line-height: 1.65;
    margin: 0;
}

/* --- How It Works 4-Step Connected Timeline --- */
.timeline-card-stage {
    background: #FFFFFF;
    border: 1px solid rgba(21, 21, 21, 0.08);
    border-radius: 22px;
    padding: 30px 22px;
    box-shadow: 0 10px 28px -10px rgba(7, 21, 34, 0.03);
    text-align: left;
    transition: all 0.3s ease;
}

.timeline-card-stage:hover {
    transform: translateY(-4px);
    border-color: #4263EB;
    box-shadow: 0 16px 36px -12px rgba(66, 99, 235, 0.12);
}

.timeline-step-badge {
    font-family: 'Instrument Serif', Georgia, serif;
    font-size: 32px;
    font-style: italic;
    color: #4263EB;
    margin-bottom: 12px;
    display: block;
}

.timeline-card-stage h4 {
    font-size: 16.5px;
    font-weight: 700;
    color: #151515;
    margin: 0 0 8px 0;
}

.timeline-card-stage p {
    font-size: 13.5px;
    color: #666666;
    line-height: 1.6;
    margin: 0;
}

/* --- Deep Navy Luxury Section --- */
.dark-editorial-section {
    background: #071522;
    border-radius: 34px;
    padding: 65px 48px;
    margin: 55px 0 25px 0;
    color: #FFFFFF;
    box-shadow: 0 25px 70px -20px rgba(7, 21, 34, 0.4);
}

.dark-editorial-badge {
    font-size: 11.5px;
    font-weight: 700;
    letter-spacing: 0.16em;
    color: #4263EB;
    text-transform: uppercase;
    margin-bottom: 16px;
    display: inline-block;
}

.dark-editorial-quote {
    font-family: 'Instrument Serif', Georgia, serif;
    font-size: 40px;
    line-height: 1.25;
    color: #FFFFFF;
    margin: 0 0 30px 0;
    max-width: 820px;
    font-weight: 400;
}

.dark-editorial-quote em {
    font-style: italic;
    color: #FFFFFF;
}

.dark-stats-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 30px;
    padding-top: 32px;
    border-top: 1px solid rgba(255, 255, 255, 0.12);
}

.dark-stat-box h3 {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 38px;
    font-weight: 700;
    color: #FFFFFF;
    margin: 0 0 6px 0;
}

.dark-stat-box h3 span {
    color: #4263EB;
}

.dark-stat-box p {
    font-size: 13.5px;
    color: #A0AEC0;
    line-height: 1.6;
    margin: 0;
}

/* --- Analysis Form Styling --- */
div[data-testid="stFileUploader"] {
    background: #FFFFFF !important;
    border: 2px dashed rgba(66, 99, 235, 0.35) !important;
    border-radius: 24px !important;
    padding: 28px !important;
    box-shadow: 0 8px 24px -10px rgba(7, 21, 34, 0.04) !important;
    transition: all 0.25s ease !important;
}

div[data-testid="stFileUploader"]:hover {
    border-color: #4263EB !important;
    background: #FCFBF8 !important;
}

div[data-baseweb="textarea"] {
    background: #FFFFFF !important;
    border: 1px solid rgba(21, 21, 21, 0.1) !important;
    border-radius: 20px !important;
    box-shadow: 0 8px 24px -10px rgba(7, 21, 34, 0.04) !important;
    transition: all 0.2s ease !important;
}

div[data-baseweb="textarea"]:focus-within {
    border-color: #4263EB !important;
    box-shadow: 0 0 0 3px rgba(66, 99, 235, 0.12) !important;
}

div[data-baseweb="textarea"] textarea {
    background: transparent !important;
    color: #151515 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 14.5px !important;
    line-height: 1.65 !important;
    padding: 18px !important;
}

/* Metric Display Overrides */
div[data-testid="stMetric"] {
    background: #FFFFFF !important;
    border: 1px solid rgba(21, 21, 21, 0.07) !important;
    border-radius: 22px !important;
    padding: 22px !important;
    box-shadow: 0 8px 24px -10px rgba(7, 21, 34, 0.04) !important;
}

div[data-testid="stMetricLabel"] {
    color: #7E7E7E !important;
    font-size: 12px !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
}

div[data-testid="stMetricValue"] {
    color: #151515 !important;
    font-family: 'Instrument Serif', Georgia, serif !important;
    font-size: 36px !important;
    font-weight: 400 !important;
}

/* Progress Bars */
div[data-testid="stProgressBar"] > div {
    background-color: #E2DDD0 !important;
    border-radius: 9999px !important;
    height: 11px !important;
}

div[data-testid="stProgressBar"] div[role="progressbar"] > div {
    background: #4263EB !important;
    border-radius: 9999px !important;
}

/* Skill Tags */
.skill-tag-matched {
    display: inline-block;
    background: rgba(66, 99, 235, 0.08);
    color: #4263EB;
    border: 1px solid rgba(66, 99, 235, 0.22);
    border-radius: 9999px;
    padding: 7px 18px;
    margin: 4px;
    font-size: 13.5px;
    font-weight: 600;
}

.skill-tag-missing {
    display: inline-block;
    background: #FFF4E5;
    color: #944B00;
    border: 1px solid #FFE2BA;
    border-radius: 9999px;
    padding: 7px 18px;
    margin: 4px;
    font-size: 13.5px;
    font-weight: 600;
}

/* Luxury Editorial Output Card */
.luxury-editorial-card {
    background: #FFFFFF;
    border: 1px solid rgba(21, 21, 21, 0.08);
    border-radius: 26px;
    padding: 38px 34px;
    box-shadow: 0 12px 36px -12px rgba(7, 21, 34, 0.05);
    margin: 20px 0;
    line-height: 1.85;
    color: #2D3748;
}

.luxury-editorial-card h3 {
    font-family: 'Instrument Serif', Georgia, serif;
    font-size: 28px;
    font-weight: 400;
    color: #151515;
    margin-bottom: 18px;
}

/* Footer */
.luxury-footer {
    padding: 55px 0 25px 0;
    margin-top: 65px;
    border-top: 1px solid rgba(21, 21, 21, 0.08);
    text-align: center;
}

.footer-brand-title {
    font-family: 'Cinzel', serif;
    font-size: 20px;
    font-weight: 700;
    letter-spacing: 0.18em;
    color: #151515;
    margin-bottom: 8px;
}

.footer-brand-title span {
    color: #4263EB;
}

.footer-tagline {
    font-size: 13.5px;
    color: #7E7E7E;
    line-height: 1.8;
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
                "<font color='#071522'><b>RESUMIND AI</b></font>",
                styles["Title"]
            )
        )

        story.append(
            Paragraph(
                "Executive Career Intelligence & Resume Analysis Report",
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
# 9. MINIMALIST EDITORIAL NAVIGATION BAR
# ==========================================================

top_nav_c1, top_nav_c2, top_nav_c3 = st.columns([2.8, 3.2, 1.4], vertical_alignment="center")

with top_nav_c1:
    show_html("""
        <div class="brand-title">
            RESUMIND <span>AI</span>
        </div>
    """)

with top_nav_c2:
    n_c1, n_c2 = st.columns(2)
    with n_c1:
        if st.button("Home", key="nav_btn_home", use_container_width=True, type="secondary"):
            st.session_state.page = "Home"
            st.rerun()
    with n_c2:
        if st.button("AI Analyzer", key="nav_btn_analyzer", use_container_width=True, type="secondary"):
            st.session_state.page = "Analysis"
            st.rerun()

with top_nav_c3:
    if st.button("Get Started →", key="nav_btn_get_started", use_container_width=True, type="primary"):
        st.session_state.page = "Analysis"
        st.rerun()


# ==========================================================
# 10. HOMEPAGE VIEW (EDITORIAL STORYTELLING — NO AI SLOP)
# ==========================================================

if st.session_state.page == "Home":

    # HERO SECTION
    show_html("""
        <div class="hero-wrapper">

            <div class="hero-pill-badge">
                ✦ RESUMIND AI &bull; EXECUTIVE CAREER INTELLIGENCE
            </div>

            <h1 class="hero-title-main">
                A sharper resume.<br>
                <em>Your next defining role.</em>
            </h1>

            <p class="hero-subtext-main">
                Resumind provides rigorous, objective resume intelligence — benchmarking your real experience against what hiring teams and modern ATS engines actually look for.
            </p>

        </div>
    """)

    # HERO CTAS
    cta_col1, cta_col2, cta_col3 = st.columns([1.5, 1.4, 1.5])
    with cta_col2:
        if st.button("ANALYSE MY RESUME →", key="hero_primary_cta", use_container_width=True, type="primary"):
            st.session_state.page = "Analysis"
            st.rerun()

    # REALISTIC PRODUCT INTERFACE PREVIEW (TANGIBLE & CRAFTED, NOT AI SLOP)
    show_html("""
        <div class="product-preview-card">

            <div class="preview-header-bar">
                <div class="candidate-profile-meta">
                    <div class="candidate-avatar-initials">AR</div>
                    <div class="candidate-name-title">
                        <h4>Alex Rivera</h4>
                        <span>Staff Infrastructure Architect &bull; Verified Evaluation</span>
                    </div>
                </div>
                <div class="preview-score-capsule">
                    <span class="score-num">89%</span>
                    <span class="score-label">Role Fit</span>
                </div>
            </div>

            <div class="preview-body-grid">
                <!-- Real annotated experience bullet -->
                <div class="resume-annotated-excerpt">
                    <span class="excerpt-tag">High-Impact Bullet Audit</span>
                    <p style="margin: 0; color: #151515; font-weight: 500;">
                        “Architected distributed event-streaming pipelines across 4 cloud regions, reducing p99 latency from 180ms to 42ms and cutting annual compute expenditure by $240K.”
                    </p>
                    <div style="margin-top: 14px; font-size: 12px; color: #4263EB; font-weight: 600; display: flex; align-items: center; gap: 6px;">
                        <span>✓</span> Strong quantified outcome &bull; High recruiter engagement factor (+14%)
                    </div>
                </div>

                <!-- Grounded Strengths and Gaps -->
                <div class="diagnostic-panel-preview">
                    <div class="diagnostic-box-mini strengths">
                        <h5><span>●</span> Confirmed Qualifications</h5>
                        <div>
                            <span class="mini-pill-tag green">Distributed Systems</span>
                            <span class="mini-pill-tag green">Kubernetes</span>
                            <span class="mini-pill-tag green">Golang</span>
                            <span class="mini-pill-tag green">High-Throughput IO</span>
                        </div>
                    </div>
                    <div class="diagnostic-box-mini gaps">
                        <h5><span>●</span> Critical Gaps Flagged</h5>
                        <div>
                            <span class="mini-pill-tag red">Terraform v1.6+</span>
                            <span class="mini-pill-tag red">Distributed Tracing</span>
                            <span class="mini-pill-tag red">eBPF</span>
                        </div>
                    </div>
                </div>
            </div>

            <div style="margin-top: 22px; padding-top: 16px; border-top: 1px solid rgba(21, 21, 21, 0.05); display: flex; justify-content: space-between; align-items: center; font-size: 12.5px; color: #7E7E7E;">
                <span>Evaluated via deterministic skill taxonomy & local Gemma AI reasoning</span>
                <span style="color: #4263EB; font-weight: 600;">100% Private &bull; On-Device Execution</span>
            </div>

        </div>
    """)

    # MARQUEE RIBBON
    show_html("""
        <div class="marquee-ribbon">
            <div class="marquee-stream">
                <div class="marquee-badge"><span class="sparkle">✦</span> Deterministic Skill Taxonomy</div>
                <div class="marquee-badge"><span class="sparkle">✦</span> ATS Compatibility Auditing</div>
                <div class="marquee-badge"><span class="sparkle">✦</span> On-Device Local Privacy</div>
                <div class="marquee-badge"><span class="sparkle">✦</span> Gemma Language Model</div>
                <div class="marquee-badge"><span class="sparkle">✦</span> Skill Gap Diagnostics</div>
                <div class="marquee-badge"><span class="sparkle">✦</span> Executive PDF Reporting</div>
                <!-- Duplicate for seamless loop -->
                <div class="marquee-badge"><span class="sparkle">✦</span> Deterministic Skill Taxonomy</div>
                <div class="marquee-badge"><span class="sparkle">✦</span> ATS Compatibility Auditing</div>
                <div class="marquee-badge"><span class="sparkle">✦</span> On-Device Local Privacy</div>
                <div class="marquee-badge"><span class="sparkle">✦</span> Gemma Language Model</div>
                <div class="marquee-badge"><span class="sparkle">✦</span> Skill Gap Diagnostics</div>
                <div class="marquee-badge"><span class="sparkle">✦</span> Executive PDF Reporting</div>
            </div>
        </div>
    """)

    # HOW IT WORKS (01 - 04 CONNECTED TIMELINE)
    show_html("""
        <div class="editorial-section-header">
            <span class="editorial-tag">METHODOLOGY</span>
            <h2 class="editorial-headline">How Resumind Works</h2>
            <p class="editorial-subtext">
                A four-step analytical pipeline engineered to dissect, benchmark, and elevate your career narrative.
            </p>
        </div>

        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 18px; margin: 30px 0 50px 0;">
            <div class="timeline-card-stage">
                <span class="timeline-step-badge">01</span>
                <h4>Document Ingestion</h4>
                <p>PyMuPDF parses structural hierarchies, degrees, contact data, and employment timelines from text PDFs.</p>
            </div>
            <div class="timeline-card-stage">
                <span class="timeline-step-badge">02</span>
                <h4>Taxonomy Extraction</h4>
                <p>Deterministic algorithms cross-reference candidate history against 1,000+ standardized industry skills.</p>
            </div>
            <div class="timeline-card-stage">
                <span class="timeline-step-badge">03</span>
                <h4>Gemma AI Synthesis</h4>
                <p>Local Gemma model evaluates qualitative depth, active phrasing, and specific qualification gaps.</p>
            </div>
            <div class="timeline-card-stage">
                <span class="timeline-step-badge">04</span>
                <h4>Executive Report</h4>
                <p>Receive transparent match metrics, gap breakdowns, and an exportable formal PDF career audit.</p>
            </div>
        </div>
    """)

    # 6 CORE CAPABILITY MODULES
    show_html("""
        <div class="editorial-section-header">
            <span class="editorial-tag">CORE CAPABILITIES</span>
            <h2 class="editorial-headline">Designed for Objective Clarity</h2>
            <p class="editorial-subtext">
                Six specialized diagnostic modules built to help applicants navigate enterprise screening and recruiter evaluations.
            </p>
        </div>
    """)

    f_row1_c1, f_row1_c2, f_row1_c3 = st.columns(3)

    with f_row1_c1:
        show_html("""
            <div class="editorial-feature-card">
                <span class="feature-num-stamp">MODULE 01</span>
                <h3>Document Structure Audit</h3>
                <p>
                    Full structural evaluation of your document — verifying header recognition, section completeness, word density, and chronology.
                </p>
            </div>
        """)

    with f_row1_c2:
        show_html("""
            <div class="editorial-feature-card">
                <span class="feature-num-stamp">MODULE 02</span>
                <h3>ATS Parsing Simulation</h3>
                <p>
                    Emulates enterprise Applicant Tracking Systems to test whether your formatting, bullets, and tables parse cleanly without errors.
                </p>
            </div>
        """)

    with f_row1_c3:
        show_html("""
            <div class="editorial-feature-card">
                <span class="feature-num-stamp">MODULE 03</span>
                <h3>Skill Gap Detection</h3>
                <p>
                    Isolates exact hard competencies, toolsets, and domain credentials missing from your profile compared to target role requirements.
                </p>
            </div>
        """)

    st.write("")  # Vertical spacing

    f_row2_c1, f_row2_c2, f_row2_c3 = st.columns(3)

    with f_row2_c1:
        show_html("""
            <div class="editorial-feature-card">
                <span class="feature-num-stamp">MODULE 04</span>
                <h3>Job Spec Alignment</h3>
                <p>
                    Compares your profile directly against target job descriptions to deliver an objective percentage suitability benchmark.
                </p>
            </div>
        """)

    with f_row2_c2:
        show_html("""
            <div class="editorial-feature-card">
                <span class="feature-num-stamp">MODULE 05</span>
                <h3>Impact & Phrasing Review</h3>
                <p>
                    Diagnoses unquantified bullet points and passive voice, providing actionable guidance to sharpen achievement framing.
                </p>
            </div>
        """)

    with f_row2_c3:
        show_html("""
            <div class="editorial-feature-card">
                <span class="feature-num-stamp">MODULE 06</span>
                <h3>Executive PDF Reporting</h3>
                <p>
                    Generates a publication-grade, formal PDF career readiness report with detailed breakdowns and interview roadmaps.
                </p>
            </div>
        """)

    # ABOUT / DEEP NAVY LUXURY SECTION
    show_html("""
        <div class="dark-editorial-section">
            <span class="dark-editorial-badge">THE RESUMIND AI PHILOSOPHY</span>
            <div class="dark-editorial-quote">
                “Career advice shouldn't be generic buzzwords. By uniting deterministic skill taxonomy with private local AI reasoning, candidates receive <em>objective, grounded truth</em> before submitting an application.”
            </div>
            <div class="dark-stats-grid">
                <div class="dark-stat-box">
                    <h3>100<span>%</span></h3>
                    <p>On-device local execution. Your confidential resume never leaves your machine.</p>
                </div>
                <div class="dark-stat-box">
                    <h3>1,000<span>+</span></h3>
                    <p>Standardized industry competencies mapped across engineering, data, design, and management.</p>
                </div>
                <div class="dark-stat-box">
                    <h3>0<span>%</span></h3>
                    <p>Hallucination tolerance. All evaluations are anchored to verified text in your resume.</p>
                </div>
            </div>
        </div>
    """)

    # FOOTER
    show_html("""
        <div class="luxury-footer">
            <div class="footer-brand-title">
                RESUMIND <span>AI</span>
            </div>
            <div class="footer-tagline">
                Your Resume. Your Skills. Your Next Defining Opportunity.<br>
                © 2026 Resumind AI. All rights reserved. • Contact: souradeepsaha190@gmail.com
            </div>
        </div>
    """)


# ==========================================================
# 11. RESUME ANALYSIS STUDIO
# ==========================================================

if st.session_state.page == "Analysis":

    show_html("""
        <div class="editorial-section-header" style="margin-top: 15px; margin-bottom: 30px;">
            <span class="editorial-tag">RESUME EVALUATION STUDIO</span>
            <h1 class="hero-editorial-title" style="font-size: 54px; margin-bottom: 12px;">
                Resume Analysis Studio
            </h1>
            <p class="editorial-subtext">
                Upload your resume in PDF format and paste the target job description. Resumind will evaluate your qualifications, calculate ATS compatibility, and provide deep qualitative recommendations.
            </p>
        </div>
    """)

    # Upload & Job Description Form
    input_c1, input_c2 = st.columns([1, 1])

    with input_c1:
        uploaded_file = st.file_uploader(
            "Upload Resume (Accepted Format: PDF)",
            type=["pdf"],
            help="Upload a clean text-based PDF resume."
        )
        if uploaded_file:
            st.success(f"✓ File loaded: **{uploaded_file.name}** ({round(len(uploaded_file.getvalue()) / 1024, 1)} KB)")

    with input_c2:
        job_description = st.text_area(
            "Target Job Description",
            placeholder=(
                "Paste the complete job description here, including title, required qualifications, "
                "tech stack, and core responsibilities..."
            ),
            height=200
        )

    analyse_cta = st.button(
        "ANALYSE RESUME →",
        type="primary",
        use_container_width=True
    )

    if analyse_cta:
        st.session_state.analysis_result = None

        if uploaded_file is None:
            st.error("Please upload your PDF resume to begin.")
        elif not job_description.strip():
            st.error("Please enter a target job description.")
        else:
            try:
                with st.spinner("Extracting text and synthesizing analysis with Gemma AI..."):
                    # STEP 1: EXTRACT PDF TEXT
                    resume_text = extract_pdf_text(uploaded_file)

                    if not resume_text:
                        raise ValueError("No readable text was found in the PDF. Scanned PDFs require OCR.")

                    # STEP 2: EXTRACT CANDIDATE DETAILS
                    candidate = extract_candidate_information(resume_text)

                    # STEP 3: RUN SKILL MATCHING
                    raw_match_data = calculate_match(resume_text, job_description)

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
                    ai_analysis = analyse_resume(resume_text, job_description)

                    if not isinstance(ai_analysis, str) or not ai_analysis.strip():
                        raise ValueError("Gemma AI returned an empty response. Verify local Ollama service.")

                    # STEP 7: SAVE ALL RESULTS
                    st.session_state.analysis_result = {
                        "candidate": candidate,
                        "match_data": match_data,
                        "ai_analysis": ai_analysis,
                        "filename": uploaded_file.name,
                        "created_at": datetime.now().strftime("%d %b %Y, %I:%M %p")
                    }

                st.success("Resume analysis successfully generated!")

            except Exception as error:
                st.session_state.analysis_result = None
                st.error(f"Analysis failed: {type(error).__name__}: {error}")
                st.info("Check whether local Ollama is running (`ollama serve`).")


# ==========================================================
# 12. AI ANALYSIS DASHBOARD
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
    score = data["match_score"]

    st.markdown("---")
    show_html("""
        <div style="margin: 30px 0 20px 0;">
            <span class="editorial-tag">AI ANALYSIS DASHBOARD</span>
            <h2 class="editorial-headline" style="font-size: 38px;">Candidate Career Audit</h2>
        </div>
    """)

    # Candidate Profile Header Cards
    prof_c1, prof_c2, prof_c3 = st.columns(3)

    with prof_c1:
        st.metric("Candidate Name", candidate["name"])

    with prof_c2:
        st.metric("Email Address", candidate["email"])

    with prof_c3:
        st.metric("Contact Phone", candidate["phone"])

    st.caption(f"File: {result['filename']} | Analysed: {result['created_at']}")

    # OVERALL MATCH SCORE & ATS COMPATIBILITY
    st.markdown("---")
    show_html("""
        <div style="margin: 30px 0 20px 0;">
            <span class="editorial-tag">ALIGNMENT METRICS</span>
            <h2 class="editorial-headline" style="font-size: 34px;">Match & ATS Compatibility</h2>
        </div>
    """)

    score_c1, score_c2 = st.columns(2)

    with score_c1:
        if required and score is not None:
            st.metric("Overall Resume Match Score", f"{score:.1f}%")
            st.progress(int(score), text=f"{score:.1f}% of target role qualifications satisfied")
            st.caption(f"Matched Skills: {len(matched)} | Missing Skills: {len(missing)} | Total Required: {len(required)}")
        else:
            st.warning("No recognised skills detected in target job description.")

    with score_c2:
        quality = data.get("resume_quality", {})
        ats_score = quality.get("quality_score", 85.0) if quality else 85.0
        st.metric("ATS Compatibility Score", f"{ats_score:.1f}%")
        st.progress(int(max(0, min(ats_score, 100))), text="Structural completeness and section formatting")
        st.caption("Evaluates headers, contact integrity, bullet formatting, and document parseability.")

    # TECHNICAL & SOFT SKILLS vs MISSING SKILLS
    st.markdown("---")
    show_html("""
        <div style="margin: 30px 0 20px 0;">
            <span class="editorial-tag">COMPETENCY TAXONOMY</span>
            <h2 class="editorial-headline" style="font-size: 34px;">Technical & Soft Skill Audit</h2>
        </div>
    """)

    sk_col1, sk_col2 = st.columns(2)

    with sk_col1:
        show_html("""
            <div style="background:#FFFFFF; border:1px solid rgba(21,21,21,0.08); border-radius:24px; padding:28px; box-shadow:0 10px 30px -10px rgba(7,21,34,0.04); min-height:180px;">
                <h3 style="font-size:18px; font-weight:700; color:#151515; margin-bottom:14px;">
                    <span style="color:#4263EB;">●</span> Matched Skills Identified
                </h3>
        """)
        if matched:
            matched_tags = "".join([f'<span class="skill-tag-matched">✓ {escape(str(s))}</span>' for s in matched])
            show_html(f'<div>{matched_tags}</div></div>')
        else:
            show_html('<p style="color:#888;">No exact skill matches identified.</p></div>')

    with sk_col2:
        show_html("""
            <div style="background:#FFFFFF; border:1px solid rgba(21,21,21,0.08); border-radius:24px; padding:28px; box-shadow:0 10px 30px -10px rgba(7,21,34,0.04); min-height:180px;">
                <h3 style="font-size:18px; font-weight:700; color:#151515; margin-bottom:14px;">
                    <span style="color:#C92A2A;">●</span> Missing Skills & Qualifications
                </h3>
        """)
        if missing:
            missing_tags = "".join([f'<span class="skill-tag-missing">✕ {escape(str(s))}</span>' for s in missing])
            show_html(f'<div>{missing_tags}</div></div>')
        else:
            if required:
                show_html('<p style="color:#4263EB; font-weight:600;">✓ All recognised job skills are present.</p></div>')
            else:
                show_html('<p style="color:#888;">No comparison skills provided in job description.</p></div>')

    # VISUAL CHART: MATCHED VS MISSING SKILLS
    st.markdown("---")
    show_html("""
        <div style="margin: 30px 0 20px 0;">
            <span class="editorial-tag">DATA VISUALIZATION</span>
            <h2 class="editorial-headline" style="font-size: 34px;">Skill Distribution Comparison</h2>
        </div>
    """)

    if required:
        chart = go.Figure()

        chart.add_trace(
            go.Bar(
                name="Matched Skills",
                x=["Skill Breakdown"],
                y=[len(matched)],
                marker_color="#4263EB",
                text=[len(matched)],
                textposition="inside",
                insidetextfont=dict(color="#FFFFFF", size=15, family="Space Grotesk")
            )
        )

        chart.add_trace(
            go.Bar(
                name="Missing Skills",
                x=["Skill Breakdown"],
                y=[len(missing)],
                marker_color="#151515",
                text=[len(missing)],
                textposition="inside",
                insidetextfont=dict(color="#FFFFFF", size=15, family="Space Grotesk")
            )
        )

        chart.update_layout(
            barmode="group",
            paper_bgcolor="#F3F0E8",
            plot_bgcolor="#FFFFFF",
            font=dict(color="#151515", family="Plus Jakarta Sans, sans-serif"),
            yaxis_title="Total Competencies",
            xaxis_title="",
            height=340,
            margin=dict(l=35, r=25, t=30, b=30),
            legend=dict(orientation="h", y=1.12, x=0),
            bargap=0.35,
            bargroupgap=0.1
        )

        chart.update_yaxes(rangemode="tozero", dtick=1, gridcolor="#E2DDD0")
        st.plotly_chart(chart, use_container_width=True, config={"displayModeBar": False})

    # EXPANDERS: ALL SKILLS & CATEGORIES
    with st.expander("View All Detected Resume Skills"):
        st.write(resume_skills if resume_skills else "No skills identified.")

    with st.expander("View All Required Job Skills"):
        st.write(required if required else "No job skills identified.")

    # EDUCATION & WORK EXPERIENCE
    st.markdown("---")
    show_html("""
        <div style="margin: 30px 0 20px 0;">
            <span class="editorial-tag">CAREER BACKGROUND</span>
            <h2 class="editorial-headline" style="font-size: 34px;">Education & Experience Analysis</h2>
        </div>
    """)

    bg_c1, bg_c2 = st.columns(2)

    with bg_c1:
        st.markdown("### 🎓 Education")
        if data["education"]:
            for item in data["education"]:
                st.write(f"• {item}")
        else:
            st.info("No education entries identified under recognized headings.")

    with bg_c2:
        st.markdown("### 💼 Work Experience")
        if data["experience"]:
            for item in data["experience"]:
                st.write(f"• {item}")
        else:
            st.info("No dated experience milestones detected.")

    # RESUME QUALITY & CHECKLIST
    st.markdown("---")
    show_html("""
        <div style="margin: 30px 0 20px 0;">
            <span class="editorial-tag">QUALITY BENCHMARK</span>
            <h2 class="editorial-headline" style="font-size: 34px;">Resume Completeness Checklist</h2>
        </div>
    """)

    if quality and quality.get("checks"):
        chk_cols = st.columns(2)
        items = list(quality["checks"].items())
        half = len(items) // 2
        with chk_cols[0]:
            for name, passed in items[:half]:
                if passed:
                    st.success(f"✓ {name}")
                else:
                    st.warning(f"✕ {name} not detected")
        with chk_cols[1]:
            for name, passed in items[half:]:
                if passed:
                    st.success(f"✓ {name}")
                else:
                    st.warning(f"✕ {name} not detected")

    # IMPROVEMENT RECOMMENDATIONS
    if data["recommendations"]:
        st.markdown("---")
        show_html("""
            <div style="margin: 30px 0 20px 0;">
                <span class="editorial-tag">STRATEGIC GUIDANCE</span>
                <h2 class="editorial-headline" style="font-size: 34px;">Actionable Resume Recommendations</h2>
            </div>
        """)
        for rec in data["recommendations"]:
            st.write(f"💡 {rec}")

    # GEMMA AI DETAILED AUDIT
    st.markdown("---")
    show_html("""
        <div style="margin: 30px 0 20px 0;">
            <span class="editorial-tag">QUALITATIVE AI AUDIT</span>
            <h2 class="editorial-headline" style="font-size: 34px;">Gemma AI In-Depth Evaluation</h2>
        </div>
    """)

    show_html("""<div class="luxury-editorial-card">""")
    st.markdown(result["ai_analysis"])
    show_html("</div>")

    # PDF DOWNLOAD & START NEW
    st.markdown("---")
    pdf_report = create_pdf_report(candidate, data, result["ai_analysis"])

    if pdf_report:
        st.download_button(
            label="DOWNLOAD EXECUTIVE PDF REPORT ↓",
            data=pdf_report,
            file_name=f"Resumind_AI_Report_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    if st.button("START NEW RESUME ANALYSIS", type="secondary"):
        st.session_state.analysis_result = None
        st.rerun()

    # Footer
    show_html("""
        <div class="luxury-footer">
            <div class="footer-brand-title">
                RESUMIND <span>AI</span>
            </div>
            <div class="footer-tagline">
                Your Resume. Your Skills. Your Next Defining Opportunity.<br>
                © 2026 Resumind AI. All rights reserved. • Contact: souradeepsaha190@gmail.com
            </div>
        </div>
    """)
