

import pymupdf
from llm_analyzer import analyse_resume

print("===== SOURA RESUME AI =====")

# Get any PDF resume
pdf_path = input("\nEnter PDF resume path: ").strip().strip('"')

if pdf_path.startswith("file:///"):
    pdf_path = pdf_path.replace("file:///", "")
    pdf_path = pdf_path.replace("/", "\\")
# Extract resume text
try:
    document = pymupdf.open(pdf_path)

    resume_text = ""

    for page in document:
        resume_text += page.get_text()

    document.close()

    if not resume_text.strip():
        print("No readable text found in this PDF.")
        raise SystemExit

    print("\nResume extracted successfully!")

except Exception as e:
    print("\nPDF Error:", e)
    raise SystemExit

# Get job description
job_description = input(
    "\nEnter job description (paste it here): "
).strip()

if not job_description:
    print("Please enter a job description.")
    raise SystemExit

# Analyse using Gemma AI
print("\nAnalysing resume... Please wait.")

try:
    result = analyse_resume(resume_text, job_description)

    print("\n===== RESUME ANALYSIS REPORT =====\n")
    print(result)

except Exception as e:
    print("\nAnalysis Error:", e)
