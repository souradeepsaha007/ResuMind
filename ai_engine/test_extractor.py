
import json
from pathlib import Path

from ai_engine.field_extractor import extract_field_analysis


resume_path = input("Enter the full path of your resume PDF: ").strip().strip('"')

try:
    result = extract_field_analysis(resume_path)

    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)

    output_file = output_dir / "resume_analysis.json"

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(result, file, indent=4, ensure_ascii=False)

    print("\n===== SOURA RESUME AI ANALYSIS =====")
    print(json.dumps(result, indent=4, ensure_ascii=False))

    print("\nAnalysis saved to:", output_file)

except Exception as error:
    print("\nError:", error)
