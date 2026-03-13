"""
FAISS Service — vector storage and similarity search.
Maintains two separate indexes: one for candidates, one for jobs.
Uses IndexFlatIP (inner product on L2-normalized vectors = cosine similarity).
"""

import os
import json
import faiss
import numpy as np
from app.config import settings


class FAISSIndex:
    """Manages a single FAISS index with ID mapping."""

    def __init__(self, name: str, dim: int = settings.EMBEDDING_DIM):
        self.name = name
        self.dim = dim
        self.index = faiss.IndexFlatIP(dim)
        self.id_map: list[str] = []  # maps FAISS row index → external ID
        self._index_path = os.path.join(settings.FAISS_INDEX_DIR, f"{name}.index")
        self._ids_path = os.path.join(settings.FAISS_INDEX_DIR, f"{name}_ids.json")

    def add(self, ext_id: str, vector: np.ndarray):
        """Add a single vector with its external ID."""
        if ext_id in self.id_map:
            # Update: remove old, add new
            idx = self.id_map.index(ext_id)
            self.id_map[idx] = ext_id  # keep same position
            # FAISS IndexFlat doesn't support in-place update, so we rebuild
            self._rebuild_without(idx, ext_id, vector)
            return

        vec = vector.reshape(1, -1).astype(np.float32)
        self.index.add(vec)
        self.id_map.append(ext_id)

    def _rebuild_without(self, old_idx: int, new_id: str, new_vector: np.ndarray):
        """Rebuild index replacing the vector at old_idx."""
        n = self.index.ntotal
        if n == 0:
            return
        # Reconstruct all vectors
        all_vecs = np.zeros((n, self.dim), dtype=np.float32)
        for i in range(n):
            all_vecs[i] = self.index.reconstruct(i)
        # Replace the old vector
        all_vecs[old_idx] = new_vector.astype(np.float32)
        # Rebuild
        self.index.reset()
        self.index.add(all_vecs)

    def search(self, query_vector: np.ndarray, top_k: int = 10) -> list[tuple[str, float]]:
        """Search for top_k most similar vectors. Returns [(id, score)]."""
        if self.index.ntotal == 0:
            return []
        k = min(top_k, self.index.ntotal)
        vec = query_vector.reshape(1, -1).astype(np.float32)
        scores, indices = self.index.search(vec, k)
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx >= 0 and idx < len(self.id_map):
                results.append((self.id_map[idx], float(score)))
        return results

    def save(self):
        """Persist index and ID map to disk."""
        os.makedirs(settings.FAISS_INDEX_DIR, exist_ok=True)
        faiss.write_index(self.index, self._index_path)
        with open(self._ids_path, "w") as f:
            json.dump(self.id_map, f)
        print(f"FAISS index '{self.name}' saved ({self.index.ntotal} vectors)")

    def load(self):
        """Load index and ID map from disk if they exist."""
        if os.path.exists(self._index_path) and os.path.exists(self._ids_path):
            self.index = faiss.read_index(self._index_path)
            with open(self._ids_path) as f:
                self.id_map = json.load(f)
            print(f"FAISS index '{self.name}' loaded ({self.index.ntotal} vectors)")
        else:
            print(f"FAISS index '{self.name}' not found on disk; starting fresh")

    @property
    def total(self) -> int:
        return self.index.ntotal


# Global indexes
candidate_index = FAISSIndex("candidates")
job_index = FAISSIndex("jobs")


def load_indexes():
    """Load both indexes from disk on startup."""
    candidate_index.load()
    job_index.load()


def save_indexes():
    """Save both indexes to disk."""
    candidate_index.save()
    job_index.save()
