
from pathlib import Path

# Main project directory
BASE_DIR = Path(__file__).resolve().parent

# Ollama model configuration
MODEL_NAME = "soura-resume-ai:latest"
BASE_MODEL = "gemma3:1b"
OLLAMA_HOST = "http://localhost:11434"

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
APP_NAME = "Soura Resume AI"
APP_VERSION = "1.0.0"

print("Soura Resume AI configuration loaded successfully!")
