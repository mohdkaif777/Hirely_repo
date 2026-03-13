"""
Classifier Service — zero-shot classification for job domain categorisation.
Model: facebook/bart-large-mnli
"""

from transformers import pipeline
from app.config import settings

_classifier = None


def load_model():
    global _classifier
    print(f"Loading classifier model: {settings.CLASSIFIER_MODEL}")
    _classifier = pipeline(
        "zero-shot-classification",
        model=settings.CLASSIFIER_MODEL,
    )
    print("Classifier model loaded successfully")


def classify(text: str, labels: list[str]) -> dict:
    """
    Classify text into one of the given labels.
    Returns dict with 'labels' and 'scores' sorted by confidence.
    """
    if _classifier is None:
        raise RuntimeError("Classifier model not loaded")
    result = _classifier(text, candidate_labels=labels, multi_label=False)
    return {
        "labels": result["labels"],
        "scores": [round(s, 4) for s in result["scores"]],
        "top_label": result["labels"][0],
        "top_score": round(result["scores"][0], 4),
    }


# Pre-defined job domains for convenience
JOB_DOMAINS = [
    "Software Engineering",
    "Data Science",
    "Product Management",
    "Design",
    "Marketing",
    "Sales",
    "Finance",
    "Human Resources",
    "DevOps",
    "Cybersecurity",
]
