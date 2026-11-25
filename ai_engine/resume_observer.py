
import re
from pathlib import Path

import pymupdf


# =====================================================
# SOURA RESUME AI - UNIVERSAL RESUME OBSERVER
# Supports IT and NON-IT resume categories
# =====================================================

SKILL_DATABASE = {
    "IT & SOFTWARE": [
        "Python", "Java", "C", "C++", "C#", "JavaScript",
        "TypeScript", "PHP", "Ruby", "Go", "Rust", "Kotlin",
        "Swift", "R", "Dart", "Scala", "Perl", "MATLAB",
        "HTML", "CSS", "React", "Angular", "Vue", "Node.js",
        "Express.js", "Django", "Flask", "FastAPI", "Spring Boot",
        ".NET", "ASP.NET", "Laravel", "Bootstrap", "Next.js"
    ],

    "DATABASE": [
        "SQL", "MySQL", "PostgreSQL", "MongoDB", "SQLite",
        "Oracle", "Redis", "Firebase", "Supabase",
        "Microsoft SQL Server", "Cassandra", "DynamoDB"
    ],

    "DATA SCIENCE & AI": [
        "Machine Learning", "Deep Learning", "Artificial Intelligence",
        "Natural Language Processing", "Computer Vision",
        "TensorFlow", "PyTorch", "Scikit-learn", "Pandas",
        "NumPy", "Matplotlib", "Seaborn", "Power BI", "Tableau",
        "Data Analysis", "Data Visualization", "Statistics",
        "Generative AI", "Large Language Models", "LLM",
        "Data Science", "Data Engineering"
    ],

    "CLOUD & DEVOPS": [
        "AWS", "Microsoft Azure", "Google Cloud", "Docker",
        "Kubernetes", "Jenkins", "Git", "GitHub", "GitLab",
        "Linux", "Terraform", "Ansible", "CI/CD",
        "Cloud Computing", "DevOps"
    ],

    "CYBERSECURITY & NETWORKING": [
        "Cybersecurity", "Network Security", "Ethical Hacking",
        "Penetration Testing", "Cryptography", "Firewall",
        "Cisco", "Networking", "TCP/IP", "DNS", "VPN",
        "Wireshark", "Nmap", "SIEM", "Incident Response"
    ],

    "ACCOUNTING & FINANCE": [
        "Accounting", "Financial Accounting", "Bookkeeping",
        "Financial Reporting", "Financial Analysis", "Auditing",
        "Taxation", "GST", "Tally", "Tally ERP", "QuickBooks",
        "Accounts Payable", "Accounts Receivable",
        "Budgeting", "Payroll", "Cost Accounting",
        "Financial Planning", "Bank Reconciliation"
    ],

    "SALES & MARKETING": [
        "Sales", "Digital Marketing", "SEO", "SEM",
        "Social Media Marketing", "Content Marketing",
        "Email Marketing", "Lead Generation", "CRM",
        "Market Research", "Brand Management", "Advertising",
        "Customer Acquisition", "Salesforce", "HubSpot"
    ],

    "HUMAN RESOURCES": [
        "Human Resources", "Recruitment", "Talent Acquisition",
        "Employee Relations", "Payroll Management",
        "Performance Management", "HR Operations",
        "Training and Development", "HRIS", "Onboarding"
    ],

    "MANAGEMENT & ADMINISTRATION": [
        "Project Management", "Team Management",
        "Operations Management", "Business Administration",
        "Strategic Planning", "Business Development",
        "Office Administration", "Documentation",
        "Supply Chain Management", "Inventory Management",
        "Logistics", "Vendor Management"
    ],

    "CUSTOMER SERVICE & HOSPITALITY": [
        "Customer Service", "Customer Support",
        "Client Relationship Management", "Communication",
        "Complaint Resolution", "Guest Relations",
        "Hotel Management", "Front Office Operations",
        "Reservation Management", "Food and Beverage Service"
    ],

    "ENGINEERING & MANUFACTURING": [
        "AutoCAD", "SolidWorks", "CATIA", "Revit",
        "ANSYS", "PLC", "SCADA", "Quality Control",
        "Quality Assurance", "Production Planning",
        "Mechanical Design", "Electrical Maintenance",
        "Lean Manufacturing", "Six Sigma"
    ],

    "HEALTHCARE": [
        "Patient Care", "Clinical Documentation",
        "Medical Coding", "Medical Billing",
        "Healthcare Administration", "Nursing",
        "Phlebotomy", "First Aid", "Medical Records"
    ],

    "EDUCATION": [
        "Teaching", "Lesson Planning", "Curriculum Development",
        "Classroom Management", "Student Assessment",
        "Educational Technology", "Academic Research",
        "Training", "Mentoring"
    ],

    "GENERAL PROFESSIONAL SKILLS": [
        "Leadership", "Teamwork", "Problem Solving",
        "Critical Thinking", "Time Management",
        "Decision Making", "Adaptability",
        "Interpersonal Skills", "Negotiation",
        "Presentation Skills", "Written Communication"
    ]
}


SECTION_ALIASES = {
    "professional_summary": [
        "professional summary", "summary", "profile",
        "career profile", "professional profile",
        "about me", "executive summary"
    ],

    "objective": [
        "career objective", "objective",
        "career goal", "professional objective"
    ],

    "education": [
        "education", "academic background",
        "educational qualifications", "academic qualifications"
    ],

    "experience": [
        "work experience", "professional experience",
        "employment history", "career history",
        "experience", "internship experience"
    ],

    "skills": [
        "skills", "technical skills", "core competencies",
        "key skills", "areas of expertise",
        "professional skills", "competencies"
    ],

    "projects": [
        "projects", "academic projects",
        "personal projects", "key projects"
    ],

    "certifications": [
        "certifications", "certificates",
        "licenses", "training and certifications"
    ],

    "achievements": [
        "achievements", "awards", "honors",
        "accomplishments"
    ],

    "languages": [
        "languages", "language proficiency"
    ],

    "interests": [
        "interests", "hobbies", "activities"
    ],

    "references": [
        "references", "referees"
    ]
}


# =====================================================
# PDF TEXT EXTRACTION
# =====================================================

def extract_pdf_text(file_path):

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if file_path.suffix.lower() != ".pdf":
        raise ValueError("This version accepts PDF files only.")

    text = []

    with pymupdf.open(file_path) as document:

        for page_number, page in enumerate(document, start=1):

            page_text = page.get_text("text")

            if page_text.strip():
                text.append(page_text)

    return "\n".join(text)


# =====================================================
# TEXT CLEANING
# =====================================================

def clean_text(text):

    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


# =====================================================
# CONTACT INFORMATION
# =====================================================

def extract_email(text):

    pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"

    matches = re.findall(pattern, text)

    return list(dict.fromkeys(matches))


def extract_phone(text):

    pattern = r"(?<!\w)(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{2,5}\)?[-.\s]?)?\d{6,10}(?!\w)"

    matches = re.findall(pattern, text)

    return list(dict.fromkeys(
        match.strip() for match in matches
        if len(re.sub(r"\D", "", match)) >= 10
    ))


def extract_links(text):

    pattern = r"(?:https?://|www\.)[^\s,;]+"

    matches = re.findall(pattern, text, flags=re.IGNORECASE)

    return list(dict.fromkeys(matches))


# =====================================================
# SECTION DETECTION
# =====================================================

def identify_sections(text):

    sections = {
        name: [] for name in SECTION_ALIASES
    }

    current_section = "other"

    for line in text.splitlines():

        line = line.strip()

        if not line:
            continue

        normalized = re.sub(r"[:\-]+$", "", line.lower()).strip()

        detected_section = None

        for section, aliases in SECTION_ALIASES.items():

            if normalized in aliases:
                detected_section = section
                break

        if detected_section:
            current_section = detected_section
            continue

        if current_section != "other":
            sections[current_section].append(line)

    return {
        key: "\n".join(value).strip()
        for key, value in sections.items()
    }


# =====================================================
# SKILL DETECTION
# =====================================================

def detect_skills(text):

    found = {}

    for category, skills in SKILL_DATABASE.items():

        category_matches = []

        for skill in skills:

            pattern = (
                r"(?<![a-zA-Z0-9])"
                + re.escape(skill)
                + r"(?![a-zA-Z0-9])"
            )

            if re.search(pattern, text, flags=re.IGNORECASE):
                category_matches.append(skill)

        if category_matches:
            found[category] = sorted(
                set(category_matches),
                key=str.lower
            )

    return found


# =====================================================
# CAREER CATEGORY DETECTION
# =====================================================

IT_CATEGORIES = {
    "IT & SOFTWARE",
    "DATABASE",
    "DATA SCIENCE & AI",
    "CLOUD & DEVOPS",
    "CYBERSECURITY & NETWORKING"
}


def classify_resume(skills):

    categories = [
        category
        for category, detected in skills.items()
        if detected
    ]

    it_matches = [
        category for category in categories
        if category in IT_CATEGORIES
    ]

    non_it_matches = [
        category for category in categories
        if category not in IT_CATEGORIES
        and category != "GENERAL PROFESSIONAL SKILLS"
    ]

    if it_matches and non_it_matches:
        return "HYBRID / MULTI-DOMAIN"

    if it_matches:
        return "IT"

    if non_it_matches:
        return "NON-IT"

    return "UNCLASSIFIED"


# =====================================================
# EXPERIENCE INDICATORS
# =====================================================

def detect_experience_years(text):

    patterns = [
        r"(\d+(?:\.\d+)?)\+?\s+years?\s+of\s+experience",
        r"(\d+(?:\.\d+)?)\+?\s+years?\s+experience"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE
        )

        if match:
            return float(match.group(1))

    return None


# =====================================================
# MAIN RESUME OBSERVER
# =====================================================

def observe_resume(file_path):

    raw_text = extract_pdf_text(file_path)

    text = clean_text(raw_text)

    sections = identify_sections(text)

    skills = detect_skills(text)

    result = {

        "file_name": Path(file_path).name,

        "resume_category": classify_resume(skills),

        "contact_information": {
            "emails": extract_email(text),
            "phone_numbers": extract_phone(text),
            "links": extract_links(text)
        },

        "professional_summary": sections["professional_summary"],

        "career_objective": sections["objective"],

        "education": sections["education"],

        "work_experience": sections["experience"],

        "skills": skills,

        "projects": sections["projects"],

        "certifications": sections["certifications"],

        "achievements": sections["achievements"],

        "languages": sections["languages"],

        "interests": sections["interests"],

        "references": sections["references"],

        "experience_years_mentioned": detect_experience_years(text),

        "full_text": text

    }

    return result


# =====================================================
# COMMAND LINE TEST
# =====================================================

if __name__ == "__main__":

    import sys
    import json

    if len(sys.argv) < 2:

        print(
            'Usage: python -m ai_engine.resume_observer "resume.pdf"'
        )

        sys.exit(1)

    resume_path = sys.argv[1]

    try:

        result = observe_resume(resume_path)

        print("\n========== SOURA RESUME AI ==========\n")

        print(
            json.dumps(
                result,
                indent=4,
                ensure_ascii=False
            )
        )

        print("\n========== ANALYSIS COMPLETED ==========")

    except Exception as error:

        print("Resume analysis failed:", error)
