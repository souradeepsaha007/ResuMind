
import re
import json
import ollama
from collections import Counter
from config import OLLAMA_HOST, MODEL_NAME as AI_MODEL


# ============================================================
# 1. CONFIGURATION
# ============================================================

def get_ollama_client():
    return ollama.Client(host=OLLAMA_HOST)


# ============================================================
# 2. COMPREHENSIVE SKILL DATABASE
# ============================================================

SKILL_DATABASE = {

    "Programming Languages": {
        "Python": ["python"],
        "Java": ["java"],
        "C": ["c programming", "c language"],
        "C++": ["c++", "cpp"],
        "C#": ["c#", "c sharp"],
        "JavaScript": ["javascript"],
        "TypeScript": ["typescript"],
        "PHP": ["php"],
        "Ruby": ["ruby"],
        "Go": ["golang"],
        "Kotlin": ["kotlin"],
        "Swift": ["swift"],
        "Dart": ["dart"],
        "R": ["r programming", "r language"],
        "SQL": ["sql"]
    },

    "Web Development": {
        "HTML": ["html"],
        "CSS": ["css"],
        "React": ["react", "react.js"],
        "Angular": ["angular"],
        "Vue.js": ["vue.js", "vuejs"],
        "Node.js": ["node.js", "nodejs"],
        "Express.js": ["express.js", "expressjs"],
        "Django": ["django"],
        "Flask": ["flask"],
        "FastAPI": ["fastapi"],
        "Bootstrap": ["bootstrap"],
        "Tailwind CSS": ["tailwind css"],
        "REST API": ["rest api", "restful api"],
        "GraphQL": ["graphql"]
    },

    "Databases": {
        "MySQL": ["mysql"],
        "PostgreSQL": ["postgresql", "postgres"],
        "MongoDB": ["mongodb", "mongo db"],
        "SQLite": ["sqlite"],
        "Oracle Database": ["oracle database"],
        "Redis": ["redis"],
        "Firebase": ["firebase"],
        "Microsoft SQL Server": ["sql server", "microsoft sql server"]
    },

    "Data Science and AI": {
        "Machine Learning": ["machine learning"],
        "Deep Learning": ["deep learning"],
        "Artificial Intelligence": ["artificial intelligence"],
        "Natural Language Processing": ["natural language processing", "nlp"],
        "Computer Vision": ["computer vision"],
        "TensorFlow": ["tensorflow"],
        "PyTorch": ["pytorch"],
        "Scikit-learn": ["scikit-learn", "sklearn"],
        "Pandas": ["pandas"],
        "NumPy": ["numpy"],
        "Matplotlib": ["matplotlib"],
        "Data Analysis": ["data analysis", "data analytics"],
        "Data Visualization": ["data visualization"],
        "Statistics": ["statistics", "statistical analysis"],
        "Generative AI": ["generative ai", "gen ai"],
        "Large Language Models": ["large language models", "llm"],
        "Prompt Engineering": ["prompt engineering"]
    },

    "Cloud and DevOps": {
        "AWS": ["aws", "amazon web services"],
        "Microsoft Azure": ["microsoft azure", "azure"],
        "Google Cloud": ["google cloud", "gcp"],
        "Docker": ["docker"],
        "Kubernetes": ["kubernetes"],
        "Jenkins": ["jenkins"],
        "Git": ["git"],
        "GitHub": ["github"],
        "GitLab": ["gitlab"],
        "Linux": ["linux"],
        "CI/CD": ["ci/cd", "continuous integration"],
        "Terraform": ["terraform"]
    },

    "Business and Office": {
        "Microsoft Excel": ["microsoft excel", "excel"],
        "Microsoft Word": ["microsoft word", "ms word"],
        "PowerPoint": ["powerpoint", "power point"],
        "Power BI": ["power bi"],
        "Tableau": ["tableau"],
        "Google Sheets": ["google sheets"],
        "SAP": ["sap"],
        "Tally": ["tally"],
        "Data Entry": ["data entry"],
        "Business Analysis": ["business analysis"],
        "Financial Analysis": ["financial analysis"],
        "Accounting": ["accounting"],
        "Bookkeeping": ["bookkeeping"],
        "Financial Reporting": ["financial reporting"],
        "Auditing": ["auditing"],
        "Budgeting": ["budgeting"],
        "Taxation": ["taxation", "tax preparation"],
        "Payroll Management": ["payroll management"]
    },

    "Marketing and Sales": {
        "Digital Marketing": ["digital marketing"],
        "SEO": ["seo", "search engine optimization"],
        "SEM": ["sem", "search engine marketing"],
        "Social Media Marketing": ["social media marketing"],
        "Social Media Management": ["social media management"],
        "Content Marketing": ["content marketing"],
        "Email Marketing": ["email marketing"],
        "Google Analytics": ["google analytics"],
        "Market Research": ["market research"],
        "Brand Management": ["brand management"],
        "Sales": ["sales"],
        "Lead Generation": ["lead generation"],
        "Customer Relationship Management": [
            "customer relationship management", "crm"
        ],
        "Public Relations": ["public relations"],
        "Copywriting": ["copywriting"],
        "Advertising": ["advertising"],
        "Market Analysis": ["market analysis"]
    },

    "Design and Creative": {
        "Graphic Design": ["graphic design"],
        "UI Design": ["ui design", "user interface design"],
        "UX Design": ["ux design", "user experience design"],
        "Figma": ["figma"],
        "Adobe Photoshop": ["adobe photoshop", "photoshop"],
        "Adobe Illustrator": ["adobe illustrator", "illustrator"],
        "Canva": ["canva"],
        "Video Editing": ["video editing"],
        "Premiere Pro": ["premiere pro"],
        "After Effects": ["after effects"],
        "Photography": ["photography"],
        "Content Creation": ["content creation"]
    },

    "Healthcare": {
        "Patient Care": ["patient care"],
        "First Aid": ["first aid"],
        "CPR": ["cpr", "cardiopulmonary resuscitation"],
        "Medical Records": ["medical records"],
        "Clinical Research": ["clinical research"],
        "Medical Terminology": ["medical terminology"],
        "Healthcare Administration": ["healthcare administration"],
        "Nursing": ["nursing"],
        "Phlebotomy": ["phlebotomy"],
        "Laboratory Techniques": ["laboratory techniques"]
    },

    "Human Resources": {
        "Recruitment": ["recruitment"],
        "Talent Acquisition": ["talent acquisition"],
        "Employee Relations": ["employee relations"],
        "Performance Management": ["performance management"],
        "HR Management": ["human resource management", "hr management"],
        "Training and Development": ["training and development"],
        "Onboarding": ["onboarding"],
        "Interviewing": ["interviewing"]
    },

    "Education": {
        "Teaching": ["teaching"],
        "Lesson Planning": ["lesson planning"],
        "Curriculum Development": ["curriculum development"],
        "Classroom Management": ["classroom management"],
        "Educational Assessment": ["educational assessment"],
        "Academic Research": ["academic research"],
        "Student Counselling": ["student counselling", "student counseling"]
    },

    "Engineering and Operations": {
        "AutoCAD": ["autocad"],
        "SolidWorks": ["solidworks"],
        "MATLAB": ["matlab"],
        "Quality Control": ["quality control"],
        "Quality Assurance": ["quality assurance"],
        "Manufacturing": ["manufacturing"],
        "Supply Chain Management": ["supply chain management"],
        "Inventory Management": ["inventory management"],
        "Logistics": ["logistics"],
        "Process Improvement": ["process improvement"],
        "Project Planning": ["project planning"],
        "Safety Management": ["safety management"]
    },

    "Human and Professional Skills": {
        "Communication": ["communication", "communication skills"],
        "Leadership": ["leadership", "team leadership"],
        "Teamwork": ["teamwork", "team work"],
        "Problem Solving": ["problem solving", "problem-solving"],
        "Critical Thinking": ["critical thinking"],
        "Time Management": ["time management"],
        "Adaptability": ["adaptability"],
        "Creativity": ["creativity"],
        "Decision Making": ["decision making"],
        "Negotiation": ["negotiation"],
        "Conflict Resolution": ["conflict resolution"],
        "Organization": ["organizational skills"],
        "Presentation Skills": ["presentation skills"],
        "Customer Service": ["customer service", "customer support"],
        "Project Management": ["project management"],
        "Agile": ["agile"],
        "Scrum": ["scrum"]
    }
}


# ============================================================
# 3. TEXT UTILITIES
# ============================================================

def clean_text(text):

    if not isinstance(text, str):
        return ""

    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def contains_phrase(text, phrase):

    pattern = (
        r"(?<![a-zA-Z0-9])"
        + re.escape(phrase.lower())
        + r"(?![a-zA-Z0-9])"
    )

    return bool(
        re.search(pattern, text.lower())
    )


# ============================================================
# 4. DICTIONARY-BASED SKILL EXTRACTION
# ============================================================

def extract_skills(text):

    text = clean_text(text)

    detected = []

    for category, skills in SKILL_DATABASE.items():

        for skill, aliases in skills.items():

            terms = [skill] + aliases

            if any(
                contains_phrase(text, term)
                for term in terms
            ):

                detected.append(skill)

    return sorted(set(detected))


def extract_skills_by_category(text):

    text = clean_text(text)

    result = {}

    for category, skills in SKILL_DATABASE.items():

        detected = []

        for skill, aliases in skills.items():

            terms = [skill] + aliases

            if any(
                contains_phrase(text, term)
                for term in terms
            ):

                detected.append(skill)

        if detected:

            result[category] = sorted(set(detected))

    return result


# ============================================================
# 5. SECTION EXTRACTION
# ============================================================

SECTION_HEADINGS = {

    "education": [
        "education",
        "academic background",
        "educational qualifications",
        "qualifications",
        "academic qualifications"
    ],

    "experience": [
        "experience",
        "work experience",
        "professional experience",
        "employment history",
        "work history",
        "professional background",
        "career history",
        "internship experience"
    ],

    "projects": [
        "projects",
        "personal projects",
        "academic projects",
        "project experience",
        "key projects"
    ],

    "certifications": [
        "certifications",
        "certificates",
        "professional certifications",
        "licenses",
        "licences",
        "credentials"
    ],

    "skills": [
        "skills",
        "technical skills",
        "core competencies",
        "key skills",
        "professional skills",
        "areas of expertise"
    ]
}


def normalize_heading(line):

    line = line.lower().strip()

    line = re.sub(r"^[#\s]+", "", line)

    line = re.sub(r"[:\-\s]+$", "", line)

    line = re.sub(r"\s+", " ", line)

    return line.strip()


def extract_sections(text):

    lines = [
        line.strip()
        for line in clean_text(text).splitlines()
        if line.strip()
    ]

    sections = {
        "education": [],
        "experience": [],
        "projects": [],
        "certifications": [],
        "skills": []
    }

    heading_lookup = {}

    for section, headings in SECTION_HEADINGS.items():

        for heading in headings:

            heading_lookup[heading] = section

    current_section = None

    for line in lines:

        heading = normalize_heading(line)

        if heading in heading_lookup:

            current_section = heading_lookup[heading]
            continue

        if current_section:

            sections[current_section].append(line)

    return {
        key: "\n".join(value)
        for key, value in sections.items()
    }


# ============================================================
# 6. EDUCATION EXTRACTION
# ============================================================

EDUCATION_TERMS = [
    "bachelor",
    "master",
    "b.tech",
    "btech",
    "m.tech",
    "mtech",
    "b.e.",
    "m.e.",
    "bca",
    "mca",
    "b.sc",
    "m.sc",
    "b.com",
    "m.com",
    "bba",
    "mba",
    "phd",
    "diploma",
    "high school",
    "secondary",
    "higher secondary",
    "university",
    "college",
    "degree"
]


def extract_education(text):

    sections = extract_sections(text)

    education_text = sections["education"]

    source_lines = (
        education_text.splitlines()
        if education_text
        else clean_text(text).splitlines()
    )

    entries = []

    for line in source_lines:

        if any(
            contains_phrase(line, term)
            for term in EDUCATION_TERMS
        ):

            entries.append(line)

    return entries


# ============================================================
# 7. EXPERIENCE EXTRACTION
# ============================================================

DATE_PATTERN = re.compile(
    r"\b(?:"
    r"Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|"
    r"May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|"
    r"Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?"
    r")\s+\d{4}\b"
    r"|\b\d{4}\s*[-–]\s*(?:\d{4}|present|current)\b",
    re.IGNORECASE
)


def extract_experience(text):

    sections = extract_sections(text)

    experience_text = sections["experience"]

    source_lines = (
        experience_text.splitlines()
        if experience_text
        else clean_text(text).splitlines()
    )

    entries = []

    for line in source_lines:

        if DATE_PATTERN.search(line):

            entries.append(line)

    return entries


def count_experience_mentions(text):

    return len(
        DATE_PATTERN.findall(clean_text(text))
    )


# ============================================================
# 8. PROJECTS AND CERTIFICATIONS
# ============================================================

def extract_projects(text):

    sections = extract_sections(text)

    return sections["projects"].splitlines() if sections["projects"] else []


def extract_certifications(text):

    sections = extract_sections(text)

    return (
        sections["certifications"].splitlines()
        if sections["certifications"]
        else []
    )


# ============================================================
# 9. KEYWORD ANALYSIS
# ============================================================

STOP_WORDS = {
    "the", "and", "for", "with", "from", "that",
    "this", "are", "you", "your", "our", "will",
    "have", "has", "was", "were", "can", "who",
    "what", "when", "where", "which", "their",
    "they", "them", "about", "into", "through",
    "such", "must", "should", "would", "could",
    "experience", "skills", "ability", "knowledge",
    "work", "working", "role", "candidate",
    "job", "responsibilities", "requirements"
}


def extract_keywords(text, limit=40):

    words = re.findall(
        r"\b[a-zA-Z][a-zA-Z0-9+#.-]{2,}\b",
        clean_text(text).lower()
    )

    filtered = [
        word for word in words
        if word not in STOP_WORDS
    ]

    counts = Counter(filtered)

    return [
        word
        for word, count in counts.most_common(limit)
    ]


def analyse_keywords(resume_text, job_description):

    resume_keywords = set(
        extract_keywords(resume_text, 100)
    )

    job_keywords = extract_keywords(
        job_description,
        100
    )

    matched = [
        word for word in job_keywords
        if word in resume_keywords
    ]

    missing = [
        word for word in job_keywords
        if word not in resume_keywords
    ]

    return {
        "resume_keywords": sorted(resume_keywords),
        "job_keywords": job_keywords,
        "matched_keywords": matched,
        "missing_keywords": missing
    }


# ============================================================
# 10. RESUME QUALITY
# ============================================================

def analyse_resume_quality(text):

    text = clean_text(text)

    words = re.findall(r"\b\w+\b", text)

    word_count = len(words)

    email_present = bool(
        re.search(
            r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}",
            text
        )
    )

    phone_present = bool(
        re.search(
            r"(?<!\d)(?:\+?\d{1,3}[\s-]?)?(?:\d[\s-]?){9,12}(?!\d)",
            text
        )
    )

    sections = extract_sections(text)

    checks = {
        "Contact email": email_present,
        "Contact phone": phone_present,
        "Education section": bool(sections["education"]),
        "Experience section": bool(sections["experience"]),
        "Skills section": bool(sections["skills"]),
        "Projects section": bool(sections["projects"]),
        "Certifications section": bool(sections["certifications"])
    }

    completed = sum(checks.values())

    quality_score = round(
        completed / len(checks) * 100,
        2
    )

    if word_count < 100:

        length_status = "Very short resume"

    elif word_count < 250:

        length_status = "Short resume"

    elif word_count <= 900:

        length_status = "Typical resume length"

    else:

        length_status = "Long resume"

    return {
        "quality_score": quality_score,
        "word_count": word_count,
        "length_status": length_status,
        "checks": checks
    }


# ============================================================
# 11. GEMMA AI SKILL EXTRACTION
# ============================================================

def extract_skills_with_gemma(resume_text, job_description):

    prompt = f"""
You are an expert resume and job requirement extraction system.

Analyse both texts carefully.

RESUME:
{resume_text[:12000]}

JOB DESCRIPTION:
{job_description[:10000]}

Identify explicitly supported skills and competencies.

Consider all career fields:

- IT and software development
- Engineering and manufacturing
- Healthcare
- Teaching and education
- Finance and accounting
- HR and recruitment
- Marketing and sales
- Business administration
- Graphic design
- Customer service
- Hospitality
- Operations and logistics
- Research
- Legal and administration

Include:
- Technical skills
- Software and tools
- Industry-specific skills
- Professional competencies
- Soft skills

Rules:
- Do not invent skills.
- Do not assume qualifications prove a skill.
- Keep resume skills and job requirements separate.
- Avoid duplicates.
- Do not include generic words.

Return ONLY valid JSON:

{{
    "resume_skills": [],
    "job_skills": []
}}
"""

    try:

        response = get_ollama_client().chat(
            model=AI_MODEL,
            format="json",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            options={
                "temperature": 0
            }
        )

        result = json.loads(
            response["message"]["content"]
        )

        resume_skills = result.get("resume_skills", [])
        job_skills = result.get("job_skills", [])

        if not isinstance(resume_skills, list):
            resume_skills = []

        if not isinstance(job_skills, list):
            job_skills = []

        resume_skills = [
            str(skill).strip()
            for skill in resume_skills
            if isinstance(skill, str) and skill.strip()
        ]

        job_skills = [
            str(skill).strip()
            for skill in job_skills
            if isinstance(skill, str) and skill.strip()
        ]

        return resume_skills, job_skills

    except Exception as error:

        print("Gemma skill extraction error:", error)

        return [], []


# ============================================================
# 12. GEMMA AI RESUME DETAIL EXTRACTION
# ============================================================

def extract_resume_details_with_gemma(resume_text):

    prompt = f"""
You are an expert resume information extraction assistant.

Extract information only when supported by the resume.

RESUME:
{resume_text[:12000]}

Return valid JSON using this structure:

{{
    "candidate_name": "",
    "email": "",
    "phone": "",
    "education": [],
    "experience": [],
    "projects": [],
    "certifications": [],
    "technical_skills": [],
    "soft_skills": []
}}

Rules:

- Do not invent information.
- Preserve dates when available.
- Include internships and volunteer experience.
- Include academic and personal projects.
- Include certification names and issuing organisations.
- Do not confuse education with work experience.
- Return empty lists when information is unavailable.
- Return JSON only.
"""

    try:

        response = get_ollama_client().chat(
            model=AI_MODEL,
            format="json",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            options={
                "temperature": 0
            }
        )

        details = json.loads(
            response["message"]["content"]
        )

        list_fields = [
            "education",
            "experience",
            "projects",
            "certifications",
            "technical_skills",
            "soft_skills"
        ]

        for field in list_fields:

            if not isinstance(details.get(field), list):

                details[field] = []

        return details

    except Exception as error:

        print("Gemma resume extraction error:", error)

        return {
            "candidate_name": "",
            "email": "",
            "phone": "",
            "education": [],
            "experience": [],
            "projects": [],
            "certifications": [],
            "technical_skills": [],
            "soft_skills": []
        }


# ============================================================
# 13. SKILL NORMALIZATION
# ============================================================

def normalize_skill_name(skill):

    skill = str(skill).strip().lower()

    skill = re.sub(
        r"[^a-z0-9+#.]",
        "",
        skill
    )

    return skill


def merge_skills(*skill_lists):

    result = {}

    for skill_list in skill_lists:

        for skill in skill_list:

            skill = str(skill).strip()

            if not skill:
                continue

            key = normalize_skill_name(skill)

            if key and key not in result:

                result[key] = skill

    return list(result.values())


# ============================================================
# 14. UNIVERSAL RESUME AND JOB MATCHING
# ============================================================

def calculate_match(resume_text, job_description):

    resume_text = clean_text(resume_text)

    job_description = clean_text(job_description)

    if not resume_text:

        raise ValueError("Resume text is empty.")

    if not job_description:

        raise ValueError("Job description is empty.")

    # A. Dictionary extraction

    dictionary_resume_skills = extract_skills(
        resume_text
    )

    dictionary_job_skills = extract_skills(
        job_description
    )

    # B. Gemma skill extraction

    ai_resume_skills, ai_job_skills = (
        extract_skills_with_gemma(
            resume_text,
            job_description
        )
    )

    # C. Merge skills

    resume_skills = merge_skills(
        dictionary_resume_skills,
        ai_resume_skills
    )

    required_skills = merge_skills(
        dictionary_job_skills,
        ai_job_skills
    )

    # D. Compare skills

    resume_skill_map = {
        normalize_skill_name(skill): skill
        for skill in resume_skills
    }

    matched_skills = []

    missing_skills = []

    for skill in required_skills:

        key = normalize_skill_name(skill)

        if key in resume_skill_map:

            matched_skills.append(skill)

        else:

            missing_skills.append(skill)

    # E. Calculate score

    if required_skills:

        match_score = round(
            len(matched_skills) /
            len(required_skills) * 100,
            2
        )

    else:

        match_score = None

    # F. Extract resume details using Gemma

    resume_details = extract_resume_details_with_gemma(
        resume_text
    )

    # G. Merge dictionary and AI resume details

    education = merge_skills(
        extract_education(resume_text),
        resume_details["education"]
    )

    experience = merge_skills(
        extract_experience(resume_text),
        resume_details["experience"]
    )

    projects = merge_skills(
        extract_projects(resume_text),
        resume_details["projects"]
    )

    certifications = merge_skills(
        extract_certifications(resume_text),
        resume_details["certifications"]
    )

    # H. Combine skill categories

    categorized_skills = extract_skills_by_category(
        resume_text
    )

    ai_extra_skills = merge_skills(
        resume_details["technical_skills"],
        resume_details["soft_skills"]
    )

    if ai_extra_skills:

        categorized_skills["Other AI-Detected Skills"] = ai_extra_skills

    # I. Extract sections and quality

    sections = extract_sections(resume_text)

    quality = analyse_resume_quality(resume_text)

    keyword_analysis = analyse_keywords(
        resume_text,
        job_description
    )

    # J. Recommendations

    recommendations = []

    if missing_skills:

        recommendations.append(
            "Review the following job requirements and develop "
            "relevant skills where appropriate: "
            + ", ".join(missing_skills)
        )

    if not education:

        recommendations.append(
            "Include your education and qualifications."
        )

    if not experience:

        recommendations.append(
            "Include relevant employment, internship or volunteer "
            "experience if available."
        )

    if not projects:

        recommendations.append(
            "Add relevant academic, professional or personal projects "
            "where applicable."
        )

    if not certifications:

        recommendations.append(
            "Include relevant certifications if you have them."
        )

    if not recommendations:

        recommendations.append(
            "Review your achievements and quantify measurable results."
        )

    # K. Return results compatible with app.py

    return {

        "match_score": match_score,

        "resume_skills": resume_skills,

        "required_skills": required_skills,

        "matched_skills": matched_skills,

        "missing_skills": missing_skills,

        "categorized_skills": categorized_skills,

        "education": education,

        "experience": experience,

        "experience_date_mentions": count_experience_mentions(
            resume_text
        ),

        "projects": projects,

        "certifications": certifications,

        "sections": sections,

        "keyword_analysis": keyword_analysis,

        "resume_quality": quality,

        "recommendations": recommendations,

        "resume_details": resume_details,

        "extraction_method": "Dictionary + Gemma AI"

    }


# ============================================================
# 15. STANDALONE RESUME ANALYSIS
# ============================================================

def analyse_resume_only(resume_text):

    resume_text = clean_text(resume_text)

    if not resume_text:

        raise ValueError("Resume text is empty.")

    details = extract_resume_details_with_gemma(
        resume_text
    )

    return {

        "skills": merge_skills(
            extract_skills(resume_text),
            details["technical_skills"],
            details["soft_skills"]
        ),

        "categorized_skills": extract_skills_by_category(
            resume_text
        ),

        "education": merge_skills(
            extract_education(resume_text),
            details["education"]
        ),

        "experience": merge_skills(
            extract_experience(resume_text),
            details["experience"]
        ),

        "projects": merge_skills(
            extract_projects(resume_text),
            details["projects"]
        ),

        "certifications": merge_skills(
            extract_certifications(resume_text),
            details["certifications"]
        ),

        "resume_details": details,

        "sections": extract_sections(resume_text),

        "quality": analyse_resume_quality(resume_text)

    }
