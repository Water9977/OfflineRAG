import json
import os
from typing import List, Dict, Tuple
import numpy as np

class LocalVectorDB:
    """
    A lightweight, single-file vector database written in pure Python & NumPy.
    Capped at under 80 lines to maintain absolute clarity and academic transparency.
    """
    def __init__(self, data_dir: str = "offlinerag/data"):
        self.data_dir = data_dir
        self.db_path = os.path.join(data_dir, "vector_index.json")
        self.chunks: List[Dict] = []
        self._ensure_data_dir()
        self.load()

    def _ensure_data_dir(self):
        os.makedirs(self.data_dir, exist_ok=True)

    def add_chunk(self, content: str, metadata: Dict, embedding: List[float]):
        """Adds a code chunk, its metadata, and its coordinate vector to the index."""
        self.chunks.append({
            "content": content,
            "metadata": metadata,
            "embedding": embedding
        })

    def save(self):
        """Saves the index as a standard, human-readable JSON file."""
        with open(self.db_path, "w", encoding="utf-8") as f:
            json.dump(self.chunks, f, indent=2, ensure_ascii=False)

    def load(self):
        """Loads the index if it exists, otherwise starts fresh."""
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, "r", encoding="utf-8") as f:
                    self.chunks = json.load(f)
            except Exception:
                self.chunks = []

    def clear(self):
        """Wipes the database clean."""
        self.chunks = []
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def search(self, query_embedding: List[float], top_k: int = 3) -> List[Tuple[Dict, float]]:
        """
        Performs exact semantic search using the Cosine Similarity formula:
        similarity = (A • B) / (||A|| * ||B||)
        """
        if not self.chunks:
            return []

        # Convert index embeddings and query embedding to NumPy matrices
        embeddings_matrix = np.array([c["embedding"] for c in self.chunks], dtype=np.float32)
        q = np.array(query_embedding, dtype=np.float32)

        # Vectorized Cosine Similarity calculation
        dot_product = np.dot(embeddings_matrix, q)
        matrix_norms = np.linalg.norm(embeddings_matrix, axis=1)
        query_norm = np.linalg.norm(q)

        # Prevent division by zero with a tiny epsilon (1e-9)
        similarities = dot_product / (matrix_norms * query_norm + 1e-9)

        # Get the sorted indices in descending order
        sorted_indices = np.argsort(similarities)[::-1]

        results = []
        for i in sorted_indices[:top_k]:
            match_chunk = {
                "content": self.chunks[i]["content"],
                "metadata": self.chunks[i]["metadata"]
            }
            results.append((match_chunk, float(similarities[i])))
            
        return results
