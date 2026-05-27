import numpy as np
from typing import List
from ai_engine.utils.logger import setup_logger

logger = setup_logger("embedding_engine")

class EmbeddingEngine:
    """
    Forensic Semantic Text Embedding Engine.
    Encodes text summaries into high-dimensional vector space using SentenceTransformers,
    falling back to normalized character bag-of-words arrays when offline.
    """
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"Loaded sentence embedding model: {self.model_name}")
        except ImportError:
            logger.warning("sentence-transformers package not installed. Using localized bag-of-words fallbacks.")

    def get_embedding(self, text: str) -> np.ndarray:
        """
        Encodes a single sentence query.
        
        Returns:
            1D float32 numpy array representing the dense vector.
        """
        if self.model:
            try:
                # Direct neural transformer encoding
                vector = self.model.encode(text, convert_to_numpy=True)
                return vector.astype(np.float32)
            except Exception as e:
                logger.error(f"Transformer text embedding failed: {e}. Falling back.")

        # Local fallback representation: 128-dimensional character frequency vector
        vector = np.zeros(128, dtype=np.float32)
        for char in text.lower():
            idx = ord(char) % 128
            vector[idx] += 1.0
            
        # Apply L2 normalization
        norm = np.linalg.norm(vector)
        if norm > 1e-6:
            vector = vector / norm
            
        return vector

    def get_embeddings_batch(self, texts: List[str]) -> np.ndarray:
        """
        Encodes a batch of query sentences.
        """
        vectors = [self.get_embedding(t) for t in texts]
        return np.vstack(vectors).astype(np.float32)
