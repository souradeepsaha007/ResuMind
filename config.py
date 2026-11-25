import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import torch

# Load environment variables
load_dotenv()

# Main project directory
BASE_DIR = Path(__file__).resolve().parent

# Project folders
MODEL_DIR = BASE_DIR / "models"
DATASET_DIR = BASE_DIR / "dataset"
TRAINING_DIR = BASE_DIR / "training"
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "outputs"

# Automatically create folders
for folder in [
    MODEL_DIR,
    DATASET_DIR,
    TRAINING_DIR,
    UPLOAD_DIR,
    OUTPUT_DIR
]:
    folder.mkdir(parents=True, exist_ok=True)

# Custom PyTorch Model Paths
SKILL_MODEL_PATH = MODEL_DIR / "soura_skill_model.pth"
SKILL_VECTORIZER_PATH = MODEL_DIR / "soura_vectorizer.joblib"
MATCH_MODEL_PATH = MODEL_DIR / "resumind_match_model.pth"
MATCH_VECTORIZER_PATH = MODEL_DIR / "resumind_match_vectorizer.joblib"

# Compute device
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# PDF configuration
ALLOWED_EXTENSIONS = ["pdf"]
MAX_FILE_SIZE_MB = 10

# Application configuration
APP_NAME = "Resumind AI"
APP_VERSION = "2.0.0"

print(f"Resumind AI configuration loaded successfully! (Device: {DEVICE})")
