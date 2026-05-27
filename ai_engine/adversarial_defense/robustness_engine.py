import numpy as np
import torch
import torch.nn as nn
from typing import Dict, Any, Tuple
from ai_engine.adversarial_defense.attack_simulator import AdversarialAttackSimulator
from ai_engine.utils.logger import setup_logger

logger = setup_logger("robustness_engine")

class RobustnessEngine:
    """
    Forensic Robustness Evaluator.
    Benchmarks deep learning models against noise variances,
    calculating model prediction decay indexes and stability scores.
    """
    @staticmethod
    def calculate_robustness_score(
        model: nn.Module,
        input_tensor: torch.Tensor,
        epsilon: float = 0.05
    ) -> Dict[str, Any]:
        """
        Runs dual forward checks comparing clean vs. perturbed inputs 
        to calculate model prediction variance.
        
        Returns:
            Robustness benchmark summary.
        """
        logger.info("Initiating model robustness and prediction decay benchmark...")
        
        device = next(model.parameters()).device
        input_tensor = input_tensor.to(device)
        
        model.eval()
        
        # 1. Clean inference forward pass
        with torch.no_grad():
            clean_output = model(input_tensor)
            clean_prob = clean_output.mean().item()

        # 2. Simulate FGSM perturbation on input tensor
        perturbed_tensor = AdversarialAttackSimulator.simulate_fgsm_perturbation(
            input_tensor, 
            epsilon=epsilon
        )
        
        # 3. Perturbed inference forward pass
        with torch.no_grad():
            perturbed_output = model(perturbed_tensor)
            perturbed_prob = perturbed_output.mean().item()

        # 4. Calculate deviation variance metric
        prob_delta = abs(clean_prob - perturbed_prob)
        # Robustness score on scale 0.0 to 1.0 (1.0 means zero prediction decay under noise)
        robustness_score = max(0.0, 1.0 - prob_delta)

        # Categorize stability levels
        status = "STABLE"
        if robustness_score < 0.6:
            status = "VULNERABLE"
            logger.warning(f"Forensic network VULNERABLE: Prediction dropped by {prob_delta:.2f} under epsilon={epsilon}.")
        elif robustness_score < 0.85:
            status = "MODERATE_STABILITY"

        return {
            "clean_prediction_probability": round(clean_prob, 4),
            "perturbed_prediction_probability": round(perturbed_prob, 4),
            "probability_variance_delta": round(prob_delta, 4),
            "robustness_score_index": round(robustness_score, 4),
            "model_stability_status": status
        }
