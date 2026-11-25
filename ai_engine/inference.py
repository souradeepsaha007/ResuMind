
from pathlib import Path

import joblib
import numpy as np
import torch

from ai_engine.skill_model import SouraSkillNet


ROOT = Path(__file__).resolve().parents[1]
MODEL_DIR = ROOT / "models"

MODEL_PATH = MODEL_DIR / "soura_skill_model.pth"
VECTORIZER_PATH = MODEL_DIR / "soura_vectorizer.joblib"

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)


class SouraSkillPredictor:

    def __init__(self):

        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                "Soura SkillNet is not trained yet. "
                "Run: python training/train_skills.py"
            )

        if not VECTORIZER_PATH.exists():
            raise FileNotFoundError(
                "Soura vectorizer is missing. "
                "Train the model first."
            )

        checkpoint = torch.load(
            MODEL_PATH,
            map_location="cpu",
            weights_only=True
        )

        self.labels = checkpoint["labels"]

        self.vectorizer = joblib.load(VECTORIZER_PATH)

        self.model = SouraSkillNet(
            input_size=checkpoint["input_size"],
            number_of_labels=len(self.labels)
        )

        self.model.load_state_dict(checkpoint["state_dict"])
        self.model.to(DEVICE)
        self.model.eval()

    def predict(self, resume_text, threshold=0.5):

        if not resume_text or not resume_text.strip():
            return []

        features = self.vectorizer.transform(
            [resume_text]
        ).toarray()

        tensor = torch.tensor(
            features,
            dtype=torch.float32
        ).to(DEVICE)

        with torch.no_grad():

            probabilities = torch.sigmoid(
                self.model(tensor)
            )[0].cpu().numpy()

        results = []

        for label, confidence in zip(
            self.labels,
            probabilities
        ):

            results.append({
                "skill": label,
                "confidence": round(float(confidence), 4),
                "predicted_present": bool(
                    confidence >= threshold
                )
            })

        return sorted(
            results,
            key=lambda item: item["confidence"],
            reverse=True
        )


_predictor = None


def predict_skills(resume_text, threshold=0.5):

    global _predictor

    if _predictor is None:
        _predictor = SouraSkillPredictor()

    return _predictor.predict(
        resume_text,
        threshold=threshold
    )
