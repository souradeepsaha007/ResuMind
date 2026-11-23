
import ollama

MODEL_NAME = "soura-resume-ai:latest"

def analyse_resume(resume_text, job_description):

    prompt = f"""
You are Soura Resume AI, an expert resume analyser.

Analyse the candidate's resume against the job description.

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Provide the following:

1. Candidate Profile
2. Skills Identified
3. Relevant Experience
4. Missing Skills
5. Resume Strengths
6. Areas for Improvement
7. Recommendations
8. Overall Suitability Score out of 100

Only use information present in the resume.
Do not invent qualifications or experience.
"""

    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return response["message"]["content"]
