

import pymupdf

def extract_resume_text(pdf_path):
    document = pymupdf.open(pdf_path)

    resume_text = ""

    for page in document:
        resume_text += page.get_text()

    document.close()

    return resume_text


if __name__ == "__main__":
    pdf_path = input("Enter your PDF resume path: ").strip().strip('"')

if pdf_path.startswith("file:///"):
    pdf_path = pdf_path.replace("file:///", "")
    pdf_path = pdf_path.replace("/", "\\")

    try:
        text = extract_resume_text(pdf_path)

        if text.strip():
            print("\nResume text extracted successfully!\n")
            print(text)
        else:
            print("No text found in this PDF.")

    except Exception as e:
        print("Error:", e)
