import unittest
import os
import sys
import numpy as np

# Ensure workspace path imports resolve correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_engine.adversarial_defense.adversarial_detector import AdversarialDetector
from ai_engine.adversarial_defense.spoof_protection import SpoofProtection
from ai_engine.adversarial_defense.attack_simulator import AttackSimulator
from ai_engine.adversarial_defense.robustness_engine import RobustnessEngine

class TestAdversarialDefense(unittest.TestCase):
    """
    Validates Laplacian texture liveness filters, FFT spatial frequency ratio checks, 
    FGSM perturbation models, and model inference decay indexes.
    """
    def setUp(self):
        # Create a mock highly textured image (a checkerboard of alternating black and white pixels)
        self.textured_img = np.zeros((100, 100, 3), dtype=np.uint8)
        for i in range(100):
            for j in range(100):
                if (i + j) % 2 == 0:
                    self.textured_img[i, j] = [255, 255, 255]

        # Create a mock completely flat image (uniform black)
        self.flat_img = np.zeros((100, 100, 3), dtype=np.uint8)

    def test_laplacian_liveness_variance(self):
        """
        SpoofProtection should extract high edge variance for genuine textures and low for flat spoof images.
        """
        # Flat image should have near-zero edge variance
        flat_var = SpoofProtection.calculate_laplacian_variance(self.flat_img)
        self.assertAlmostEqual(flat_var, 0.0, places=4)

        # Textured image should have extremely high edge variance
        textured_var = SpoofProtection.calculate_laplacian_variance(self.textured_img)
        self.assertTrue(textured_var > 10.0)

        # Test threshold check
        report_flat = SpoofProtection.verify_liveness(self.flat_img, min_threshold=1.0)
        self.assertFalse(report_flat["liveness_verified"])
        self.assertEqual(report_flat["spoof_type"], "PRINT_SPOOF_ATTACK")

        # Set high max_threshold to prevent high-frequency synthetic pattern from triggering replay spoof moiré filters
        report_live = SpoofProtection.verify_liveness(self.textured_img, min_threshold=1.0, max_threshold=10000000.0)
        self.assertTrue(report_live["liveness_verified"])
        self.assertEqual(report_live["spoof_type"], "ORGANIC_FACE")

    def test_adversarial_fft_high_frequency_ratio(self):
        """
        AdversarialDetector should parse 2D Fast Fourier magnitude arrays and compute power spectrum ratios.
        """
        # Test textured image spectrum
        ratio, fft_mag = AdversarialDetector.calculate_high_frequency_ratio(self.textured_img)
        self.assertTrue(0.0 <= ratio <= 1.0)
        self.assertEqual(fft_mag.shape, (100, 100))

        # Test flat image spectrum (should have virtually zero high frequency content)
        ratio_flat, _ = AdversarialDetector.calculate_high_frequency_ratio(self.flat_img)
        self.assertTrue(ratio_flat < ratio)

        # Test scan wrapper
        scan = AdversarialDetector.scan_for_adversarial_perturbations(self.textured_img, anomaly_threshold=0.01)
        self.assertTrue("is_adversarial_attack" in scan)
        self.assertTrue("high_frequency_energy_ratio" in scan)

    def test_attack_simulation(self):
        """
        AttackSimulator should modify images via Gaussian and FGSM perturbations.
        """
        # Gaussian injection
        noisy = AttackSimulator.inject_gaussian_noise(self.textured_img, standard_deviation=10.0)
        self.assertEqual(noisy.shape, self.textured_img.shape)
        # Verify pixels actually changed
        self.assertFalse(np.array_equal(noisy, self.textured_img))

        # FGSM perturbation
        perturbed = AttackSimulator.simulate_fgsm_perturbation(self.textured_img, epsilon=0.05)
        self.assertEqual(perturbed.shape, self.textured_img.shape)

    def test_robustness_inference_decay(self):
        """
        RobustnessEngine should evaluate model accuracy decay between clean and perturbed inputs.
        """
        import torch
        import torch.nn as nn
        
        # Define a mock linear model
        model = nn.Sequential(nn.Linear(10, 1))
        # Initialize weights to small constant to ensure deterministic model stability in test checks
        nn.init.constant_(model[0].weight, 0.01)
        nn.init.constant_(model[0].bias, 0.0)
        tensor = torch.randn(1, 10)

        report = RobustnessEngine.calculate_robustness_score(
            model=model,
            input_tensor=tensor,
            epsilon=0.05
        )

        self.assertTrue(report["robustness_score_index"] > 0.0)
        self.assertTrue(report["clean_prediction_probability"] is not None)
        self.assertTrue(report["model_stability_status"] in ["STABLE", "MODERATE_STABILITY"])

if __name__ == "__main__":
    unittest.main()


