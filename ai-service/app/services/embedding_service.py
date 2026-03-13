"""
Embedding Service — generates dense vector embeddings using sentence-transformers.
Model: sentence-transformers/all-mpnet-base-v2 (768-dim)
"""

import numpy as np
from sentence_transformers import SentenceTransformer
from app.config import settings

_model: SentenceTransformer = None


def load_model():
    global _model
    print(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
    _model = SentenceTransformer(settings.EMBEDDING_MODEL)
    print("Embedding model loaded successfully")


def encode(text: str) -> np.ndarray:
    """Generate a normalized 768-dim embedding for a string."""
    if _model is None:
        raise RuntimeError("Embedding model not loaded")
    vec = _model.encode(text, normalize_embeddings=True)
    return np.array(vec, dtype=np.float32)


def encode_batch(texts: list[str]) -> np.ndarray:
    """Generate normalized embeddings for a list of texts."""
    if _model is None:
        raise RuntimeError("Embedding model not loaded")
    vecs = _model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
    return np.array(vecs, dtype=np.float32)
