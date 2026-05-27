import cv2
import numpy as np
from typing import Dict, Any, Tuple
from ai_engine.utils.logger import setup_logger

logger = setup_logger("adversarial_detector")

class AdversarialDetector:
    """
    Adversarial Perturbation Detection Engine.
    Performs 2D Fast Fourier Transform (FFT) frequency spectrum checks
    to identify high-frequency adversarial noise (FGSM, PGD, Carlini-Wagner).
    """
    @staticmethod
    def calculate_high_frequency_ratio(image_bgr: np.ndarray) -> Tuple[float, np.ndarray]:
        """
        Computes the ratio of high-frequency power in the image spectrum using 2D FFT.
        
        Args:
            image_bgr: Query image matrix (H x W x C).
            
        Returns:
            Tuple containing (high_frequency_ratio, power_spectrum_db)
        """
        # 1. Convert to grayscale and convert to float32
        gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY).astype(np.float32)
        h, w = gray.shape
        
        # 2. Compute 2D Fast Fourier Transform
        f_transform = np.fft.fft2(gray)
        # Shift zero-frequency component to center of spectrum
        f_shift = np.fft.fftshift(f_transform)
        
        # 3. Calculate Power Spectrum magnitude
        magnitude_spectrum = np.abs(f_shift)
        
        # 4. Partition spectrum into high vs low frequency zones using central radial radius
        cy, cx = h // 2, w // 2
        radius = min(h, w) // 10 # Central mask boundaries (10% of minimum dimension)
        
        # Create circular low-frequency mask
        y, x = np.ogrid[-cy:h-cy, -cx:w-cx]
        low_freq_mask = x*x + y*y <= radius*radius
        
        # Calculate energy sums
        total_energy = np.sum(magnitude_spectrum)
        low_energy = np.sum(magnitude_spectrum[low_freq_mask])
        high_energy = total_energy - low_energy
        
        if total_energy <= 1e-6:
            return 0.0, np.zeros_like(magnitude_spectrum)

        hf_ratio = float(high_energy / total_energy)
        
        # Decibel scale mapping for diagnostics representation
        spectrum_db = 20 * np.log1p(magnitude_spectrum)
        
        return hf_ratio, spectrum_db

    @staticmethod
    def scan_for_adversarial_perturbations(
        image_bgr: np.ndarray, 
        anomaly_threshold: float = 0.85
    ) -> Dict[str, Any]:
        """
        Scans input frame for adversarial signatures.
        Unnatural high-frequency spikes indicate evasion noise.
        """
        logger.info("Initiating 2D-FFT frequency spectrum scan for adversarial noise...")
        
        hf_ratio, _ = AdversarialDetector.calculate_high_frequency_ratio(image_bgr)
        is_attack = hf_ratio > anomaly_threshold

        report = {
            "is_adversarial_attack": is_attack,
            "high_frequency_energy_ratio": round(hf_ratio, 4),
            "noise_threshold_limit": anomaly_threshold,
            "risk_verdict": "ATTACK_DETECTED" if is_attack else "SAFE_SPECTRUM"
        }
        
        if is_attack:
            logger.critical(
                f"ADVERSARIAL ATTACK BLOCKED: High-frequency energy spike identified: {hf_ratio:.4f} "
                f"(Threshold: {anomaly_threshold})"
            )
            
        return report
