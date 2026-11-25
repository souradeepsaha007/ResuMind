"""
ResuMind AI - Intelligent Resume Verification & Gatekeeping Classifier
======================================================================
Guarantees that uploaded documents are authentic Candidate Resumes / CVs
before feeding them to PyTorch neural models, ATS scorers, or interview generators.

Detects and cleanly rejects non-resume documents such as:
- Invoices, receipts, and billing statements
- Academic research papers, theses, and journal preprints
- Legal contracts, NDAs, and terms of service
- Bank statements, financial reports, and tax filings
- Medical prescriptions, pathology, and clinical reports
- Generic prose, recipes, essays, and arbitrary text
"""

import re
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional

# Attempt to import full domain skill database
try:
    from ai_engine.resume_observer import SKILL_DATABASE
except Exception:
    SKILL_DATABASE = {}

# Fallback core skills if SKILL_DATABASE is unavailable
FALLBACK_SKILLS = {
    "python", "java", "c++", "c#", "javascript", "typescript", "html", "css",
    "react", "angular", "node.js", "django", "fastapi", "flask", "sql", "mysql",
    "postgresql", "mongodb", "aws", "azure", "docker", "kubernetes", "git",
    "linux", "machine learning", "deep learning", "data analysis", "excel",
    "accounting", "sales", "marketing", "management", "communication",
    "recruitment", "human resources", "project management", "autocad"
}

# =====================================================================
# NON-RESUME DISQUALIFIER TAXONOMIES
# =====================================================================

DISQUALIFIER_PATTERNS = {
    "Invoice / Billing Document": [
        r"\binvoice\b",
        r"\btax\s+invoice\b",
        r"\bbill\s+to\b",
        r"\bship\s+to\b",
        r"\bamount\s+due\b",
        r"\bsubtotal\b",
        r"\bdue\s+date\b",
        r"\bpayment\s+(?:terms|due|details|received)\b",
        r"\bremittance\b",
        r"\bunit\s+price\b",
        r"\bqty\b|\bquantity\b",
        r"\bgstin\b|\bvat\s+reg(?:istration)?\b",
        r"\btotal\s+(?:amount|payable|balance|price)\b",
        r"\bbalance\s+due\b",
        r"\breceipt\s+(?:#|no|number)\b",
        r"\binvoice\s+(?:#|no|number)\b",
    ],
    "Academic Research Paper / Thesis": [
        r"\babstract\b",
        r"\bkeywords\s*:",
        r"\bproceedings\s+of\b",
        r"\bieee\s+transactions\b",
        r"\barxiv\s*:\b",
        r"\bliterature\s+review\b",
        r"\bmethodology\b",
        r"\bexperimental\s+(?:setup|results|evaluation)\b",
        r"\bdoi\s*:\s*10\.\d+",
        r"\bconclusions?\s+(?:and\s+future\s+work)?\b",
        r"\breferences\s*\[1\]\b",
        r"\bet\s+al\.\b",
    ],
    "Legal Contract / Agreement": [
        r"\bthis\s+agreement\b",
        r"\bterms\s+and\s+conditions\b",
        r"\bgoverning\s+law\b",
        r"\bindemnif(?:y|ication)\b",
        r"\bconfidentiality\s+agreement\b",
        r"\bnon-disclosure\s+agreement\b",
        r"\bwitnesseth\b",
        r"\bseverability\b",
        r"\bin\s+witness\s+whereof\b",
        r"\bparties\s+hereto\b",
        r"\bhereinafter\b",
    ],
    "Financial Statement / Bank Statement": [
        r"\baccount\s+statement\b",
        r"\bbalance\s+brought\s+forward\b",
        r"\bcheque\s+no\b",
        r"\btransaction\s+description\b",
        r"\bclosing\s+balance\b",
        r"\bstatement\s+of\s+account\b",
        r"\bdebit\s+amount\b",
        r"\bcredit\s+amount\b",
    ],
    "Medical / Clinical Report": [
        r"\bpatient\s+name\b",
        r"\bprescribed\s+by\b",
        r"\bclinical\s+history\b",
        r"\bpathology\s+report\b",
        r"\bblood\s+examination\b",
        r"\blab\s+test\s+results\b",
        r"\brx\b|\bdosage\b",
    ],
}

# =====================================================================
# RESUME SECTION STRUCTURAL ANCHORS
# =====================================================================

RESUME_SECTION_PATTERNS = {
    "experience": [
        r"\b(?:work|professional|employment|career)\s+experience\b",
        r"\b(?:work|employment|career)\s+history\b",
        r"\bprofessional\s+background\b",
        r"\binternship(?:s|\s+experience)?\b",
        r"\brelevant\s+experience\b",
        r"^(?:experience|work\s+experience|employment)\s*[:\-]?$",
        r"^(?:experience|work\s+experience|employment)\b",
    ],
    "education": [
        r"\b(?:academic\s+background|educational\s+qualifications?|academic\s+details|academic\s+history)\b",
        r"\b(?:education\s*&?\s*credentials|education\s*&?\s*training)\b",
        r"\b(?:b\.?tech|m\.?tech|b\.e\.|b\.e\b|m\.e\.|m\.e\b|b\.?sc|m\.?sc|b\.?com|m\.?com|b\.a\.|b\.a\b|mba|bba|mca|bca|ph\.?d)\b",
        r"\b(?:bachelor|master|doctorate|diploma|matriculation|intermediate|secondary)\s+(?:of|in|education)?\b",
        r"\b(?:university|college|institute|cgpa|gpa|percentage)\b",
        r"^(?:education|academics?|qualifications?)\s*[:\-]?$",
        r"^(?:education|academics?|qualifications?)\b",
    ],
    "skills": [
        r"\b(?:technical|core|key|professional|programming)\s+skills\b",
        r"\bcore\s+competencies\b",
        r"\b(?:areas\s+of\s+expertise|technical\s+expertise|technologies|tech\s+stack)\b",
        r"\btools\s+(?:&|and)\s+technologies\b",
        r"\bproficiencies\b",
        r"^(?:skills|technical\s+skills|core\s+competencies)\s*[:\-]?$",
        r"^(?:skills|technical\s+skills|core\s+competencies|key\s+skills)\b",
    ],
    "projects": [
        r"\b(?:academic|personal|technical|key|capstone)\s+projects\b",
        r"\bproject\s+work\b",
        r"^(?:projects|key\s+projects)\s*[:\-]?$",
        r"^(?:projects|academic\s+projects|personal\s+projects)\b",
    ],
    "summary": [
        r"\b(?:professional|executive|career|background)\s+summary\b",
        r"\b(?:career|professional|job)\s+objective\b",
        r"\b(?:about\s+me|career\s+profile|personal\s+profile)\b",
        r"^(?:summary|profile|objective)\s*[:\-]?$",
        r"^(?:summary|profile|objective|career\s+objective)\b",
    ],
    "certifications": [
        r"\b(?:certifications?|licenses?|credentials|courses\s*&?\s*certifications?)\b",
        r"\b(?:awards?|honors?|achievements?|accomplishments?)\b",
        r"^(?:certifications?|achievements?|awards?)\s*[:\-]?$",
        r"^(?:certifications?|achievements?|awards?)\b",
    ],
}


def _extract_all_skills_flat() -> set:
    """Build a unified lowercase skill token set from domain database."""
    skill_set = set(FALLBACK_SKILLS)
    if SKILL_DATABASE:
        for cat_skills in SKILL_DATABASE.values():
            for sk in cat_skills:
                skill_set.add(sk.strip().lower())
    return skill_set


_UNIFIED_SKILL_SET = _extract_all_skills_flat()


def validate_resume_document(text: str) -> Dict[str, Any]:
    """
    Validates whether the provided plain text represents an authentic Candidate Resume / CV.

    Returns:
        dict: {
            "is_valid": bool,
            "confidence_score": float (0-100),
            "document_type": str,
            "detected_sections": List[str],
            "candidate_signals": Dict[str, Any],
            "detected_skills": List[str],
            "rejection_reason": Optional[str],
            "diagnostics": Dict[str, Any]
        }
    """
    clean_text = text.replace("\xa0", " ").replace("\x00", " ").strip()
    words = clean_text.split()
    word_count = len(words)
    char_count = len(clean_text)

    # 1. Minimum Content Sanity Check
    if char_count < 100 or word_count < 25:
        return {
            "is_valid": False,
            "confidence_score": 0.0,
            "document_type": "Insufficient Content / Blank Document",
            "detected_sections": [],
            "candidate_signals": {},
            "detected_skills": [],
            "rejection_reason": (
                f"Document contains insufficient readable content ({word_count} words). "
                "A genuine resume or CV requires comprehensive background details."
            ),
            "diagnostics": {"word_count": word_count, "char_count": char_count}
        }

    lower_text = clean_text.lower()
    lines = [line.strip() for line in clean_text.splitlines() if line.strip()]

    # 2. Check Candidate Identity & Contact Markers
    email_matches = re.findall(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", clean_text)
    phone_matches = re.findall(r"(?:\+?\d{1,3}[\s.-]?)?(?:\(?\d{2,5}\)?[\s.-]?)?\d{3,5}[\s.-]?\d{4,5}", clean_text)
    clean_phones = [p.strip() for p in phone_matches if 10 <= len(re.sub(r"\D", "", p)) <= 13]
    has_linkedin = bool(re.search(r"linkedin\.com/(?:in|pub)/", lower_text))
    has_github = bool(re.search(r"github\.com/", lower_text))

    candidate_signals = {
        "has_email": len(email_matches) > 0,
        "email_count": len(email_matches),
        "has_phone": len(clean_phones) > 0,
        "phone_count": len(clean_phones),
        "has_linkedin": has_linkedin,
        "has_github": has_github,
    }

    # 3. Detect Resume Sections
    detected_sections = []
    section_scores = 0.0

    for section_name, patterns in RESUME_SECTION_PATTERNS.items():
        found = False
        # First check line-by-line (for exact heading lines and colon prefixes)
        for line in lines:
            line_clean = re.sub(r"^[\s\d\.\-•✦*|#:]+\s*", "", line).strip().lower()
            colon_prefix = line_clean.split(":", 1)[0].strip() if ":" in line_clean else line_clean
            for pat in patterns:
                if (
                    re.search(pat, line_clean, re.IGNORECASE)
                    or re.search(pat, colon_prefix, re.IGNORECASE)
                ):
                    found = True
                    break
            if found:
                break

        # If not found as single line, check in whole text
        if not found:
            for pat in patterns:
                if re.search(pat, clean_text, re.IGNORECASE):
                    found = True
                    break

        if found:
            detected_sections.append(section_name)
            if section_name in ("experience", "education"):
                section_scores += 25.0
            elif section_name == "skills":
                section_scores += 20.0
            elif section_name in ("projects", "summary"):
                section_scores += 15.0
            elif section_name == "certifications":
                section_scores += 10.0

    # 4. Detect Recognized Domain Skills
    detected_skills = []
    for sk in _UNIFIED_SKILL_SET:
        # Match using word boundaries for accuracy
        pattern = r"\b" + re.escape(sk) + r"\b"
        if re.search(pattern, lower_text):
            detected_skills.append(sk.title())
            if len(detected_skills) >= 15:
                break

    # 5. Check Non-Resume Disqualifiers (Invoices, Research Papers, Legal, Medical, etc.)
    disqualifier_matches: Dict[str, List[str]] = {}
    for doc_type, patterns in DISQUALIFIER_PATTERNS.items():
        matched_tokens = []
        for pat in patterns:
            if re.search(pat, lower_text):
                matched_tokens.append(pat)
        if matched_tokens:
            disqualifier_matches[doc_type] = matched_tokens

    # Analyze Disqualifier Dominance
    detected_non_resume_type = None

    # A. Invoice / Receipt Check:
    invoice_tokens = disqualifier_matches.get("Invoice / Billing Document", [])
    if len(invoice_tokens) >= 3 and len(detected_sections) <= 1 and not candidate_signals["has_phone"]:
        detected_non_resume_type = "Invoice / Billing Document"

    # B. Academic Research Paper Check:
    paper_tokens = disqualifier_matches.get("Academic Research Paper / Thesis", [])
    has_abstract = any("abstract" in t for t in paper_tokens)
    has_keywords = any("keywords" in t for t in paper_tokens)
    has_references = any("references" in t or "doi" in t or "arxiv" in t or "ieee" in t for t in paper_tokens)
    if has_abstract and (has_keywords or has_references or len(paper_tokens) >= 3):
        # Even if "education" or "skills" mentioned somewhere in the paper,
        # an academic research paper structure has abstract + keywords / doi and no personal work experience
        if "experience" not in detected_sections and not candidate_signals["has_phone"]:
            detected_non_resume_type = "Academic Research Paper / Journal Article"

    # C. Legal Contract / Terms Check:
    legal_tokens = disqualifier_matches.get("Legal Contract / Agreement", [])
    if len(legal_tokens) >= 3 and len(detected_sections) <= 1 and not candidate_signals["has_phone"]:
        detected_non_resume_type = "Legal Contract / Agreement"

    # D. Financial Statement Check:
    finance_tokens = disqualifier_matches.get("Financial Statement / Bank Statement", [])
    if len(finance_tokens) >= 2 and len(detected_sections) <= 1 and not candidate_signals["has_phone"]:
        detected_non_resume_type = "Financial Statement / Bank Statement"

    # E. Medical Report Check:
    med_tokens = disqualifier_matches.get("Medical / Clinical Report", [])
    if len(med_tokens) >= 3 and len(detected_sections) <= 1 and not candidate_signals["has_phone"]:
        detected_non_resume_type = "Medical / Clinical Report"

    # 6. Compute Confidence Score
    # Baseline from sections (up to 60)
    score = min(60.0, section_scores)

    # Candidate contact signals (up to 20)
    if candidate_signals["has_email"]:
        score += 8.0
    if candidate_signals["has_phone"]:
        score += 8.0
    if candidate_signals["has_linkedin"] or candidate_signals["has_github"]:
        score += 4.0

    # Skill presence bonus (up to 20)
    if len(detected_skills) >= 6:
        score += 20.0
    elif len(detected_skills) >= 3:
        score += 12.0
    elif len(detected_skills) >= 1:
        score += 5.0

    # Apply disqualifier penalty if non-resume traits detected
    if detected_non_resume_type:
        score = max(5.0, score - 60.0)

    score = round(min(100.0, max(0.0, score)), 1)

    # 7. Final Validation Decision
    # A valid resume must:
    # - Not be flagged as a specific non-resume type
    # - Have confidence score >= 35.0
    # - Have at least 2 distinct resume sections OR (at least 1 major section + email/phone + 2+ skills)
    is_valid = False
    rejection_reason = None
    final_doc_type = "Candidate Resume / CV"

    if detected_non_resume_type:
        is_valid = False
        final_doc_type = detected_non_resume_type
        rejection_reason = (
            f"The uploaded file appears to be a '{detected_non_resume_type}'. "
            "ResuMind AI is exclusively calibrated for candidate resumes and curriculum vitae (CVs)."
        )
    elif len(detected_sections) >= 2 and score >= 35.0:
        is_valid = True
    elif len(detected_sections) == 1 and (candidate_signals["has_email"] or candidate_signals["has_phone"]) and len(detected_skills) >= 2 and score >= 35.0:
        is_valid = True
    else:
        is_valid = False
        final_doc_type = "Generic Document / Non-Resume"
        missing_parts = []
        if "experience" not in detected_sections:
            missing_parts.append("Work Experience")
        if "education" not in detected_sections:
            missing_parts.append("Education")
        if "skills" not in detected_sections:
            missing_parts.append("Skills")

        missing_str = ", ".join(missing_parts) if missing_parts else "standard career sections"
        rejection_reason = (
            f"The document does not appear to be a valid Resume or CV (Confidence: {score}%). "
            f"Missing essential resume anchors: {missing_str}. "
            "Please upload an authentic text-based candidate resume."
        )

    return {
        "is_valid": is_valid,
        "confidence_score": score,
        "document_type": final_doc_type,
        "detected_sections": detected_sections,
        "candidate_signals": candidate_signals,
        "detected_skills": detected_skills[:10],
        "rejection_reason": rejection_reason,
        "diagnostics": {
            "word_count": word_count,
            "char_count": char_count,
            "detected_sections_count": len(detected_sections),
            "disqualifier_matches": {k: len(v) for k, v in disqualifier_matches.items() if v}
        }
    }


def is_valid_resume_pdf(pdf_path: str | Path) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Convenience helper to extract text from a PDF file path and run validation.

    Returns:
        (is_valid, message, validation_data)
    """
    import pymupdf

    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        return False, f"File not found: {pdf_path}", {}

    text_parts = []
    try:
        with pymupdf.open(pdf_path) as doc:
            for page in doc:
                txt = page.get_text("text", sort=True)
                if not txt or len(txt.strip()) < 15:
                    blocks = page.get_text("blocks")
                    txt = "\n".join(b[4] for b in blocks if len(b) > 4 and str(b[4]).strip())
                if txt.strip():
                    text_parts.append(txt)
    except Exception as e:
        return False, f"Unable to read PDF file: {e}", {}

    raw_text = "\n".join(text_parts).strip()
    val = validate_resume_document(raw_text)
    msg = "Valid Resume" if val["is_valid"] else (val["rejection_reason"] or "Invalid resume document")
    return val["is_valid"], msg, val


def assert_valid_resume(text: str, filename: Optional[str] = None):
    """
    Raises ValueError with descriptive message if the document fails resume validation.
    """
    val = validate_resume_document(text)
    if not val["is_valid"]:
        fname_prefix = f"[{filename}] " if filename else ""
        raise ValueError(f"{fname_prefix}{val['rejection_reason']}")
