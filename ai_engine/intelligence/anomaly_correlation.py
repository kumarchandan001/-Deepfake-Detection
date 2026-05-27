import numpy as np
from typing import List, Dict, Any
from ai_engine.utils.logger import setup_logger

logger = setup_logger("anomaly_correlation")

class AnomalyCorrelator:
    """
    Forensic Cross-Media Anomaly Correlator.
    Analyzes historical forensic confidence variables and processing intervals
    to calculate correlation coefficients and cluster deepfake generator families.
    """
    @staticmethod
    def calculate_pearson_correlation(series_a: List[float], series_b: List[float]) -> float:
        """
        Calculates Pearson correlation coefficient between two numeric timelines.
        """
        if len(series_a) != len(series_b) or len(series_a) < 3:
            return 0.0
            
        arr_a = np.array(series_a)
        arr_b = np.array(series_b)
        
        # Calculate standard Pearson correlation
        std_a = np.std(arr_a)
        std_b = np.std(arr_b)
        
        if std_a <= 1e-6 or std_b <= 1e-6:
            return 0.0
            
        correlation = np.corrcoef(arr_a, arr_b)[0, 1]
        return float(correlation) if not np.isnan(correlation) else 0.0

    @staticmethod
    def cluster_anomalies_by_fingerprint(
        case_records: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Groups case records by structural similarity scores (Visual confidence vs. Audio confidence ratios).
        Allows security analysts to track coordinated campaigns using identical tool combinations.
        """
        logger.info(f"Initiating anomaly clustering over {len(case_records)} historic records...")
        
        # Generator clusters mapping: {cluster_id: [records]}
        clusters = {
            "Visual-Only (GAN/FaceSwap)": [],
            "Acoustic-Only (Voice Clone)": [],
            "Multimodal Fusion (Enterprise Threat)": []
        }

        for rec in case_records:
            v_score = rec.get("video_confidence", 0.0)
            a_score = rec.get("audio_confidence", 0.0)
            
            # Simple boundary clustering logic
            if v_score > 50.0 and a_score > 50.0:
                clusters["Multimodal Fusion (Enterprise Threat)"].append(rec)
            elif v_score > 50.0:
                clusters["Visual-Only (GAN/FaceSwap)"].append(rec)
            elif a_score > 50.0:
                clusters["Acoustic-Only (Voice Clone)"].append(rec)

        formatted_report = []
        for name, records in clusters.items():
            formatted_report.append({
                "cluster_family": name,
                "volume": len(records),
                "case_references": [r.get("case_id") for r in records if r.get("case_id")]
            })
            
        logger.info("Forensic anomaly clustering completed.")
        return formatted_report
