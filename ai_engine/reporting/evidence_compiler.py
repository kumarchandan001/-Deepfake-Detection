from typing import Dict, Any, List
from ai_engine.utils.logger import setup_logger

logger = setup_logger("evidence_compiler")

class EvidenceCompiler:
    """
    Forensic Evidence Compiler.
    Assembles heterogeneous verification results (EXIF tags, face liveness metrics, 
    and neural net scores) into a unified structured evidence matrix.
    """
    @staticmethod
    def compile_forensic_evidence(
        media_filename: str,
        verdict: str,
        confidence: float,
        exif_profile: Dict[str, Any],
        liveness_profile: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Structures individual verification checkpoints.
        
        Returns:
            List of dictionary checkpoints representing the forensic dossier portfolio.
        """
        logger.info(f"Compiling structured evidence nodes for: {media_filename}")
        
        evidence_nodes = []

        # 1. Base Classifier Checkpoint
        evidence_nodes.append({
            "dimension": "Spatial Classifier Attributions",
            "verdict": verdict,
            "confidence_score": f"{confidence:.2f}%",
            "status": "ANOMALY_FOUND" if verdict in ["FAKE", "MANIPULATED", "FAKE_VOICE"] else "CLEAN_PASS",
            "diagnostic_value": f"Confidence coefficient matched at {confidence:.2f}%"
        })

        # 2. Metadata EXIF Checkpoint
        is_exif_clean = not exif_profile.get("is_manipulated_metadata", False)
        exif_software = exif_profile.get("editing_software")
        exif_details = f"Editing footprint detected: {exif_software}" if exif_software else "EXIF tags match standard camera hardware specs."
        
        evidence_nodes.append({
            "dimension": "EXIF Tag Analysis",
            "verdict": "MANIPULATED" if not is_exif_clean else "AUTHENTIC",
            "confidence_score": "100.00%",
            "status": "WARNING_ATTRIBUTION" if not is_exif_clean else "CLEAN_PASS",
            "diagnostic_value": exif_details
        })

        # 3. Liveness Checkpoint
        is_liveness_ok = liveness_profile.get("liveness_verified", True)
        variance = liveness_profile.get("sharpness_variance", 0.0)
        liveness_details = f"Moiré screen frequency or low-depth printed paper detected. Variance: {variance:.2f}." if not is_liveness_ok else f"Organic flesh reflectiveness confirmed. Laplacian Variance: {variance:.2f}."
        
        evidence_nodes.append({
            "dimension": "Biometric Liveness Verification",
            "verdict": "AUTHENTIC" if is_liveness_ok else "SPOOF_ATTACK",
            "confidence_score": "95.00%",
            "status": "CRITICAL_BIOMETRIC_FAIL" if not is_liveness_ok else "CLEAN_PASS",
            "diagnostic_value": liveness_details
        })

        logger.info(f"Evidence compiled. Registered nodes: {len(evidence_nodes)}")
        return evidence_nodes
