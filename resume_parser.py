import sys
from pathlib import Path
import pymupdf


def extract_resume_text(pdf_path):
    """Extracts plain text from a given PDF resume path using PyMuPDF."""
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    document = pymupdf.open(pdf_path)
    resume_text = "\n".join(page.get_text() for page in document)
    document.close()
    return resume_text


if __name__ == "__main__":
    if len(sys.argv) > 1:
        target_path = sys.argv[1].strip().strip('"')
    elif sys.stdin.isatty():
        target_path = input("Enter your PDF resume path: ").strip().strip('"')
    else:
        target_path = "sample_resume.pdf"

    if Path(target_path).exists():
        text = extract_resume_text(target_path)
        print(f"\nExtracted {len(text)} characters from {target_path}:\n")
        print(text[:300] + "...")
    else:
        print(f"Usage: python resume_parser.py <path_to_resume.pdf>")
