import os
import json
from pathlib import Path
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import ollama

# Load environment variables
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

app = FastAPI(
    title="Resumind Cloud API",
    version="1.0.0",
    description="REST API backend for Resumind Resume Intelligence"
)

# Configuration with intelligent defaults
API_KEY = os.getenv("APP_API_KEY", "")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
MODEL_NAME = os.getenv("OLLAMA_MODEL", "resumind:latest")

# Helper to get Ollama client
def get_ollama_client():
    return ollama.Client(host=OLLAMA_HOST)


class ResumeRequest(BaseModel):
    resume_text: str = Field(min_length=20, description="Full text extracted from candidate resume")
    job_description: str = Field(min_length=10, description="Target job description")


@app.get("/")
def home():
    return {
        "application": "Resumind",
        "status": "running",
        "backend": "Resumind AI Inference",
        "ollama_host": OLLAMA_HOST,
        "model": MODEL_NAME
    }


@app.get("/health")
def health():
    try:
        client = get_ollama_client()
        # Verify connection to Ollama
        client.list()
        return {
            "status": "healthy",
            "ollama_connection": "connected",
            "model": MODEL_NAME
        }
    except Exception as e:
        return {
            "status": "degraded",
            "ollama_connection": f"cannot connect to {OLLAMA_HOST}: {str(e)}",
            "model": MODEL_NAME
        }


@app.post("/analyze")
def analyze_resume(
    request: ResumeRequest,
    authorization: str = Header(default="")
):
    if API_KEY and authorization != f"Bearer {API_KEY}":
        raise HTTPException(status_code=401, detail="Invalid or missing API key")

    prompt = f"""
You are Resumind, an expert resume analysis assistant.

Analyze the following resume against the job description.

RESUME:
{request.resume_text[:15000]}

JOB DESCRIPTION:
{request.job_description[:8000]}

Return a structured JSON analysis containing:
1. overall_match_score (integer between 0 and 100)
2. candidate_profile_summary (short summary)
3. matched_skills (list of strings)
4. missing_skills (list of strings)
5. candidate_strengths (list of strings)
6. improvement_suggestions (list of strings)
7. final_recommendation (short verdict)

Return valid JSON only.
"""

    try:
        client = get_ollama_client()
        response = client.chat(
            model=MODEL_NAME,
            format="json",
            messages=[
                {
                    "role": "system",
                    "content": "You are Resumind, a professional AI resume analyser. Return valid JSON only."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            options={
                "temperature": 0.2
            }
        )

        result_text = response["message"]["content"]

        try:
            parsed_result = json.loads(result_text)
        except (json.JSONDecodeError, TypeError):
            parsed_result = {"analysis": result_text}

        return {
            "success": True,
            "model": MODEL_NAME,
            "analysis": parsed_result
        }

    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail=f"Resumind model inference failed: {str(error)}"
        )
