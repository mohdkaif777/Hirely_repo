"""
NER Service — extracts named entities (skills, tech terms) from text.
Model: dslim/bert-base-NER
"""

from transformers import pipeline
from app.config import settings

_ner_pipeline = None


def load_model():
    global _ner_pipeline
    print(f"Loading NER model: {settings.NER_MODEL}")
    _ner_pipeline = pipeline(
        "ner",
        model=settings.NER_MODEL,
        tokenizer=settings.NER_MODEL,
        aggregation_strategy="simple",
    )
    print("NER model loaded successfully")


def extract_entities(text: str) -> list[str]:
    """Extract named entities from text and return unique entity strings."""
    if _ner_pipeline is None:
        raise RuntimeError("NER model not loaded")
    results = _ner_pipeline(text)
    entities = list({r["word"].strip() for r in results if r["score"] > 0.5})
    return entities


def extract_skills(text: str, known_skills: list[str] = None) -> list[str]:
    """
    Extract skills from resume/profile text.
    Combines NER-detected entities with keyword matching against known skills.
    """
    # NER-based extraction
    ner_entities = extract_entities(text)

    # Simple keyword matching for common tech skills
    common_skills = known_skills or [
        "python", "javascript", "react", "node", "java", "c++", "sql",
        "mongodb", "postgresql", "docker", "kubernetes", "aws", "azure",
        "machine learning", "deep learning", "nlp", "data science",
        "fastapi", "django", "flask", "typescript", "html", "css",
        "git", "linux", "tensorflow", "pytorch", "pandas", "numpy",
        "rust", "go", "swift", "kotlin", "ruby", "php", "scala",
        "redis", "elasticsearch", "graphql", "rest api", "ci/cd",
        "agile", "scrum", "figma", "photoshop", "illustrator",
    ]
    text_lower = text.lower()
    keyword_matches = [s for s in common_skills if s in text_lower]

    # Combine and deduplicate
    all_skills = list(set(ner_entities + keyword_matches))
    return all_skills
