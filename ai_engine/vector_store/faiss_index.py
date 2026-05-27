import os
import numpy as np
from typing import Tuple, List, Optional
from ai_engine.utils.logger import setup_logger

logger = setup_logger("faiss_index")

class FAISSIndex:
    """
    Forensic FAISS Vector Database Wrapper.
    Indexes dense text representations for high-speed semantic searches,
    falling back to standard numpy matrix cosine similarity operations when offline.
    """
    def __init__(self, dimension: int = 384, index_filepath: str = "weights/vector_store/forensics.index"):
        self.dimension = dimension
        self.index_filepath = index_filepath
        os.makedirs(os.path.dirname(os.path.abspath(index_filepath)), exist_ok=True)
        
        self.index = None
        self.numpy_fallback_store: List[np.ndarray] = []
        self.metadata_store: List[dict] = []

        try:
            import faiss
            self.index = faiss.IndexFlatIP(self.dimension) # Inner Product index for cosine similarity
            logger.info("FAISS Index successfully initialized in flat-IP cosine configuration.")
        except ImportError:
            logger.warning("FAISS library not installed. Falling back to numpy cosine similarity matrix.")

    def add_vector(self, vector: np.ndarray, metadata: dict) -> None:
        """
        Pushes a dense vector and its descriptive metadata into active indices.
        """
        # Ensure correct array float32 dtype
        vector_f32 = vector.astype(np.float32).reshape(1, -1)
        
        if self.index:
            try:
                self.index.add(vector_f32)
                logger.info("Added vector successfully to native FAISS index.")
            except Exception as e:
                logger.error(f"Failed to add vector to FAISS: {e}")

        # Always append to fallback store and metadata dictionary
        self.numpy_fallback_store.append(vector.flatten())
        self.metadata_store.append(metadata)

    def search_vector(self, query_vector: np.ndarray, top_k: int = 5) -> List[Tuple[float, dict]]:
        """
        Executes a vector search query.
        
        Returns:
            List of tuples representing (similarity_score, metadata)
        """
        query_f32 = query_vector.astype(np.float32).reshape(1, -1)
        
        if self.index and self.index.ntotal > 0:
            try:
                # Query index
                distances, indices = self.index.search(query_f32, top_k)
                results = []
                for score, idx in zip(distances[0], indices[0]):
                    if idx != -1 and idx < len(self.metadata_store):
                        results.append((float(score), self.metadata_store[idx]))
                return results
            except Exception as e:
                logger.error(f"Native FAISS search execution failed: {e}")

        # Fallback Cosine Similarity Search using NumPy
        if not self.numpy_fallback_store:
            return []

        logger.info("Executing numpy vector similarity comparison...")
        matrix = np.vstack(self.numpy_fallback_store)
        query = query_vector.flatten()
        
        # Compute dot product similarities (assumes vectors are already L2 normalized)
        similarities = np.dot(matrix, query)
        
        # Sort indices by highest score
        sorted_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in sorted_indices:
            results.append((float(similarities[idx]), self.metadata_store[idx]))
            
        return results

    def save_index(self) -> None:
        """
        Persists FAISS indices to disk.
        """
        if self.index:
            try:
                import faiss
                faiss.write_index(self.index, self.index_filepath)
                logger.info(f"Native FAISS index serialized successfully to: {self.index_filepath}")
            except Exception as e:
                logger.error(f"Failed to save FAISS index: {e}")
                
        # Local JSON cache for metadata fallback
        meta_filepath = self.index_filepath + ".meta"
        try:
            with open(meta_filepath, "w", encoding="utf-8") as f:
                import json
                json.dump(self.metadata_store, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save metadata fallback: {e}")
