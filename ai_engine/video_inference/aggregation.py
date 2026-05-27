import numpy as np
from typing import List, Dict, Any

class TemporalPredictionAggregator:
    """
    Implements mathematical prediction fusion methods to aggregate 
    frame-level classification scores into a solid video decision.
    """
    @staticmethod
    def aggregate_mean(scores: List[float], threshold: float = 0.5) -> Dict[str, Any]:
        """
        Fuses predictions by calculating the simple mathematical mean of all scores.
        """
        if not scores:
            return {"prediction": "REAL", "confidence": 100.0, "score": 0.0}
            
        mean_score = float(np.mean(scores))
        is_fake = mean_score >= threshold
        confidence = mean_score if is_fake else (1.0 - mean_score)
        
        return {
            "prediction": "FAKE" if is_fake else "REAL",
            "confidence": round(float(confidence * 100), 2),
            "score": mean_score
        }

    @staticmethod
    def aggregate_majority_vote(scores: List[float], threshold: float = 0.5) -> Dict[str, Any]:
        """
        Fuses predictions using a ratio check (percentage of frames flagged as FAKE).
        """
        if not scores:
            return {"prediction": "REAL", "confidence": 100.0, "score": 0.0}
            
        fake_votes = sum(1 for s in scores if s >= threshold)
        fake_ratio = fake_votes / len(scores)
        
        is_fake = fake_ratio > 0.4 # Flag as FAKE if >40% frames are manipulated
        confidence = fake_ratio if is_fake else (1.0 - fake_ratio)
        
        return {
            "prediction": "FAKE" if is_fake else "REAL",
            "confidence": round(float(confidence * 100), 2),
            "score": fake_ratio
        }
