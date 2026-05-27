import cv2
import numpy as np
from typing import Dict, Any, List, Set, Tuple
from ai_engine.utils.logger import setup_logger

logger = setup_logger("misinformation_detector")

class MisinformationDetector:
    """
    Misinformation Fingerprinting Engine.
    Computes perceptual media hashes (aHash) to track duplicate distributions 
    of known deepfake assets across index registries.
    """
    def __init__(self):
        # Fingerprint registry mapping: {ahash_hex_string: [associated_case_ids]}
        self.known_fingerprints: Dict[str, Set[str]] = {}

    def compute_average_hash(self, img_bgr: np.ndarray) -> str:
        """
        Computes 64-bit average perceptual hash (aHash) from BGR frame matrix.
        
        Args:
            img_bgr: Raw input image array.
            
        Returns:
            16-character hex string representing the image fingerprint.
        """
        try:
            # 1. Resize to 8x8 and convert to grayscale
            resized = cv2.resize(img_bgr, (8, 8), interpolation=cv2.INTER_AREA)
            gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
            
            # 2. Compute mean pixel value
            avg = gray.mean()
            
            # 3. Construct 64-bit boolean matrix: 1 if pixel > mean else 0
            diff = gray > avg
            
            # 4. Flatten and serialize to hex string
            flat_bits = diff.flatten()
            hex_str = ""
            for i in range(0, 64, 4):
                nibble = flat_bits[i:i+4]
                val = sum(b * (2 ** (3 - idx)) for idx, b in enumerate(nibble))
                hex_str += f"{val:x}"
                
            return hex_str
        except Exception as e:
            logger.error(f"Perceptual hashing computation failure: {e}")
            raise e

    def register_fake_fingerprint(self, img_bgr: np.ndarray, case_id: str) -> str:
        """
        Generates and registers fingerprint of verified deepfake.
        """
        fingerprint = self.compute_average_hash(img_bgr)
        if fingerprint not in self.known_fingerprints:
            self.known_fingerprints[fingerprint] = set()
        self.known_fingerprints[fingerprint].add(case_id)
        logger.info(f"Registered deepfake fingerprint: {fingerprint} under case: {case_id}")
        return fingerprint

    def scan_for_duplicates(self, img_bgr: np.ndarray, distance_threshold: int = 5) -> Tuple[bool, List[str]]:
        """
        Scans current asset against registered deepfake hashes using Hamming Distance.
        
        Args:
            img_bgr: Query image matrix.
            distance_threshold: Maximum bit-flips allowed (Hamming distance) to declare match.
            
        Returns:
            Tuple indicating (is_duplicate_found, [matching_case_ids])
        """
        query_hash = self.compute_average_hash(img_bgr)
        matching_cases = []
        
        for registered_hash, cases in self.known_fingerprints.items():
            # Calculate Hamming Distance (bit discrepancy) between hex hashes
            dist = sum(c1 != c2 for c1, c2 in zip(query_hash, registered_hash))
            
            if dist <= distance_threshold:
                matching_cases.extend(list(cases))
                logger.warning(
                    f"Duplicate deepfake match identified! Hamming Distance: {dist}. "
                    f"Related Cases: {list(cases)}"
                )

        is_duplicate = len(matching_cases) > 0
        return is_duplicate, list(set(matching_cases))
