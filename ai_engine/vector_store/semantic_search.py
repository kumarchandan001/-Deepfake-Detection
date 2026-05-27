from typing import List, Tuple, Dict, Any
from ai_engine.vector_store.embedding_engine import EmbeddingEngine
from ai_engine.vector_store.faiss_index import FAISSIndex
from ai_engine.utils.logger import setup_logger

logger = setup_logger("semantic_search")

class SemanticSearchManager:
    """
    Forensic Semantic Search Coordinator.
    Binds the dense text embedding transformer and FAISS vector index,
    exposing natural language queries across past cases database files.
    """
    def __init__(self):
        self.embeddings = EmbeddingEngine()
        # Sentence Transformer all-MiniLM outputs 384 dimensions dense vectors
        # If fallback is used, the engine matches L2-normalized 128-dimensional counts
        dim = 384 if self.embeddings.model is not None else 128
        self.vector_db = FAISSIndex(dimension=dim)
        logger.info("Semantic Search Manager successfully initialized.")

    def index_case_report(self, case_id: str, summary_text: str, verdict: str) -> None:
        """
        Encodes and indexes a new case report summary.
        """
        logger.info(f"Indexing case [{case_id}] summary into vector database...")
        
        # 1. Generate text embedding vector
        vector = self.embeddings.get_embedding(summary_text)
        
        # 2. Add to vector index with metadata payload
        metadata = {
            "case_id": case_id,
            "summary": summary_text,
            "verdict": verdict
        }
        self.vector_db.add_vector(vector, metadata)

    def query_similar_incidents(self, query_phrase: str, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Queries the vector index for incidents matching the semantic query criteria.
        
        Returns:
            List of dictionaries representing matched records with similarity indicators.
        """
        logger.info(f"Querying similar incidents for: '{query_phrase}'")
        
        # 1. Generate query text embedding vector
        query_vector = self.embeddings.get_embedding(query_phrase)
        
        # 2. Search FAISS index
        matches = self.vector_db.search_vector(query_vector, top_k=limit)
        
        formatted_matches = []
        for score, meta in matches:
            formatted_matches.append({
                "case_id": meta.get("case_id"),
                "summary": meta.get("summary"),
                "verdict": meta.get("verdict"),
                "semantic_similarity_coefficient": round(score, 4)
            })
            
        logger.info(f"Search query finished. Matches returned: {len(formatted_matches)}")
        return formatted_matches
