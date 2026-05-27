import cv2
import numpy as np
import torch
from typing import Tuple, Optional
from ai_engine.utils.logger import setup_logger

logger = setup_logger("attack_simulator")

class AdversarialAttackSimulator:
    """
    Forensic Evasion & Perturbation Simulator.
    Simulates minor environmental modifications and Fast Gradient Sign Method (FGSM) 
    noise inputs to benchmark the robustness limits of active deep learning classifiers.
    """
    @staticmethod
    def inject_gaussian_noise(image_bgr: np.ndarray, standard_deviation: float = 15.0) -> np.ndarray:
        """
        Injects Gaussian white noise into raw image matrices.
        """
        noise = np.random.normal(0, standard_deviation, image_bgr.shape).astype(np.float32)
        noisy_image = np.clip(image_bgr.astype(np.float32) + noise, 0, 255.0).astype(np.uint8)
        return noisy_image

    @staticmethod
    def simulate_fgsm_perturbation(
        image_tensor: torch.Tensor, 
        epsilon: float = 0.05, 
        gradient_sign: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        """
        Simulates FGSM adversarial perturbation step in tensor space.
        Formula: x_perturbed = x + epsilon * sign(grad_x)
        
        Args:
            image_tensor: Normalized torch.Tensor, shape: (Batch, Channels, H, W)
            epsilon: Weight parameter of the perturbation step
            gradient_sign: Input pre-calculated gradient sign tensor (if available), 
                           else generates random sign tensor to simulate perturbation.
                           
        Returns:
            Perturbed image tensor clamped to normal [0.0, 1.0] bounds.
        """
        logger.info(f"Simulating FGSM evasion perturbation with epsilon step: {epsilon}")
        
        if gradient_sign is None:
            # Generate dummy sign tensor mimicking backward gradients output
            gradient_sign = torch.sign(torch.randn_like(image_tensor))

        # Apply perturbation steps
        perturbed_tensor = image_tensor + epsilon * gradient_sign
        
        # Clamp tensor to standard normalized bounds
        perturbed_tensor = torch.clamp(perturbed_tensor, 0.0, 1.0)
        return perturbed_tensor

# Backward compatibility wrapper for numpy metrics validation
class AttackSimulator(AdversarialAttackSimulator):
    @staticmethod
    def inject_gaussian_noise(image_bgr: np.ndarray, standard_deviation: float = 15.0) -> np.ndarray:
        return AdversarialAttackSimulator.inject_gaussian_noise(image_bgr, standard_deviation)

    @staticmethod
    def simulate_fgsm_perturbation(image_bgr: np.ndarray, epsilon: float = 0.05) -> np.ndarray:
        # Convert numpy array BGR to normalized torch tensor: (1, 3, H, W)
        # Convert BGR to RGB
        img_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        tensor = torch.tensor(img_rgb / 255.0, dtype=torch.float32).permute(2, 0, 1).unsqueeze(0)
        
        # Simulate perturbation
        perturbed_tensor = AdversarialAttackSimulator.simulate_fgsm_perturbation(tensor, epsilon)
        
        # Convert back to BGR numpy array
        perturbed_rgb = (perturbed_tensor.squeeze(0).permute(1, 2, 0).numpy() * 255.0).astype(np.uint8)
        perturbed_bgr = cv2.cvtColor(perturbed_rgb, cv2.COLOR_RGB2BGR)
        return perturbed_bgr

