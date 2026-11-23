# Soura Resume AI ✦

An intelligent, AI-powered resume analyzer and career readiness platform built with **Streamlit**, **Gemma LLM (Ollama)**, and modern semantic skill matching algorithms.

---

## 🌟 Overview

Soura Resume AI evaluates candidate resumes against target job descriptions with precision. It identifies matched and missing competencies, calculates ATS-style compatibility scores, assesses resume completeness, and provides deep qualitative feedback and recommendations powered by local LLMs.

### Key Capabilities
- **Resume Intelligence**: Automatically extracts candidate contact information, education, experience, projects, and certifications from text-based PDFs.
- **Job Match Analysis**: Evaluates candidate skill sets against target role requirements using keyword extraction and taxonomy mapping.
- **Gemma AI Insights**: Deep qualitative audit identifying strengths, gaps, and actionable improvement recommendations via Ollama.
- **Visual Analytics**: Interactive breakdowns of matched vs. missing skills and section completeness.
- **PDF Report Generation**: Downloadable formal PDF audit reports generated with ReportLab.

---

## 🛠️ Tech Stack

- **Frontend & UI**: Streamlit (custom Mindly-inspired design system)
- **AI & NLP**: Ollama (`gemma3:1b` / `soura-resume-ai`), PyMuPDF (PDF extraction), Scikit-Learn
- **Visualization**: Plotly Graph Objects
- **Reporting**: ReportLab PDF Engine

---

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
cd "AI resume analyser"
```

### 2. Set Up Virtual Environment & Dependencies
```bash
python -m venv .venv
# Windows:
.\.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Start Ollama with the Model
Ensure Ollama is running and has the required model:
```bash
ollama serve
ollama pull gemma3:1b
```

### 4. Run the Streamlit Application
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 📄 License
MIT License. Crafted with precision for career excellence.
