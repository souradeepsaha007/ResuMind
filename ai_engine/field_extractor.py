
import re

from ai_engine.resume_observer import (
    observe_resume,
    SECTION_ALIASES
)


def extract_education(text):
    """Extract education entries using common degree patterns."""

    degree_patterns = [
        r"\bB\.?Tech\b|\bBachelor of Technology\b",
        r"\bM\.?Tech\b|\bMaster of Technology\b",
        r"\bB\.?E\.?\b|\bBachelor of Engineering\b",
        r"\bM\.?E\.?\b|\bMaster of Engineering\b",
        r"\bB\.?Sc\b|\bBachelor of Science\b",
        r"\bM\.?Sc\b|\bMaster of Science\b",
        r"\bB\.?Com\b|\bBachelor of Commerce\b",
        r"\bM\.?Com\b|\bMaster of Commerce\b",
        r"\bB\.?A\b|\bBachelor of Arts\b",
        r"\bM\.?A\b|\bMaster of Arts\b",
        r"\bB\.?C\.?A\b|\bBachelor of Computer Applications\b",
        r"\bM\.?C\.?A\b|\bMaster of Computer Applications\b",
        r"\bMBA\b|\bMaster of Business Administration\b",
        r"\bPh\.?D\b|\bDoctor of Philosophy\b",
        r"\bDiploma\b",
        r"\bHigher Secondary\b",
        r"\bSecondary\b"
    ]

    lines = text.splitlines()
    results = []

    for line in lines:
        line = line.strip()

        if not line:
            continue

        for pattern in degree_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                results.append(line)
                break

    return list(dict.fromkeys(results))


def extract_years(text):
    """Find possible academic and employment years."""

    return sorted(set(
        re.findall(
            r"\b(?:19|20)\d{2}\b",
            text
        )
    ))


def extract_experience_entries(text):
    """Identify lines containing common employment indicators."""

    indicators = [
        "developer", "engineer", "manager", "intern",
        "executive", "analyst", "assistant", "teacher",
        "accountant", "consultant", "designer",
        "supervisor", "coordinator", "technician",
        "officer", "nurse", "sales", "recruiter"
    ]

    results = []

    for line in text.splitlines():

        cleaned = line.strip()

        if not cleaned:
            continue

        if any(
            word in cleaned.lower()
            for word in indicators
        ):
            results.append(cleaned)

    return list(dict.fromkeys(results))


def extract_field_analysis(pdf_path):

    observed = observe_resume(pdf_path)

    text = observed["full_text"]

    result = {
        "file_name": observed["file_name"],
        "career_category": observed["resume_category"],

        "personal_information": {
            "emails": observed["contact_information"]["emails"],
            "phone_numbers": observed["contact_information"]["phone_numbers"],
            "links": observed["contact_information"]["links"]
        },

        "professional_summary": observed["professional_summary"],

        "career_objective": observed["career_objective"],

        "education": {
            "section_text": observed["education"],
            "possible_qualifications": extract_education(text),
            "years_found": extract_years(text)
        },

        "experience": {
            "section_text": observed["work_experience"],
            "possible_job_titles": extract_experience_entries(
                observed["work_experience"]
            ),
            "years_of_experience_mentioned":
                observed["experience_years_mentioned"]
        },

        "skills": observed["skills"],

        "projects": observed["projects"],

        "certifications": observed["certifications"],

        "achievements": observed["achievements"],

        "languages": observed["languages"],

        "interests": observed["interests"],

        "references": observed["references"]
    }

    return result
