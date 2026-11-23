
from matcher import calculate_match

resume = """
Python Java SQL Excel
"""

job_description = """
Required skills:
Python Java SQL Git Django
"""

result = calculate_match(resume, job_description)

print("\n========== JOB SUITABILITY TEST ==========")

print("\n1. RESUME SKILLS:")
print(result["resume_skills"])

print("\n2. REQUIRED JOB SKILLS:")
print(result["required_skills"])

print("\n3. MATCHED SKILLS:")
print(result["matched_skills"])

print("\n4. MISSING SKILLS:")
print(result["missing_skills"])

print("\n5. JOB SUITABILITY:")
print(result["match_score"], "%")

print("\n========== TEST COMPLETED ==========")
