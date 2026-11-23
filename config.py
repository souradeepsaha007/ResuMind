
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

# Main project directory
BASE_DIR = Path(__file__).resolve().parent

# Ollama model configuration
MODEL_NAME = os.getenv("OLLAMA_MODEL", "resumind:latest")
BASE_MODEL = os.getenv("OLLAMA_BASE_MODEL", "gemma3:1b")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

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

# PDF configuration
ALLOWED_EXTENSIONS = ["pdf"]
MAX_FILE_SIZE_MB = 10

# Application configuration
APP_NAME = "Resumind"
APP_VERSION = "1.0.0"

print("Resumind configuration loaded successfully!")
