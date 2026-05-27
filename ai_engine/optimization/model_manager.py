import os
import torch
import torch.nn as nn
from typing import Dict, Any, Optional, Tuple
from ai_engine.models.model_factory import ModelFactory
from ai_engine.utils.logger import setup_logger

logger = setup_logger("model_lifecycle")

class ModelLifecycleManager:
    """
    Manages active deep learning networks in memory, coordinates runtime hot-swaps,
    performs A/B prediction routing, and supports dynamic weight rollbacks.
    """
    def __init__(self, checkpoint_dir: str = "ai_engine/checkpoints"):
        self.checkpoint_dir = checkpoint_dir
        os.makedirs(self.checkpoint_dir, exist_ok=True)
        
        # In-memory dictionary caching active instantiated models: {model_key: nn.Module}
        self.loaded_models: Dict[str, nn.Module] = {}
        # Tracks active default model path signature
        self.active_model_key: Optional[str] = None
        # Registry mapping model versions: {version: file_path}
        self.checkpoint_registry: Dict[str, str] = {}
        
        self._scan_checkpoint_directory()

    def _scan_checkpoint_directory(self) -> None:
        """
        Scans checkpoints folder to register available weight binaries.
        """
        logger.info(f"Scanning checkpoint archives at: {self.checkpoint_dir}")
        for file in os.listdir(self.checkpoint_dir):
            if file.endswith(".pth"):
                # Register version label based on file names (e.g. 'v1.0.pth')
                version_key = file.replace(".pth", "")
                full_path = os.path.join(self.checkpoint_dir, file)
                self.checkpoint_registry[version_key] = full_path
                logger.info(f"Registered weight version: {version_key} -> {full_path}")

    def load_model_to_memory(self, model_name: str, version_key: str, device: str = "cpu") -> nn.Module:
        """
        Loads a specific model backbone and sets its weights from the checkpoint registry.
        """
        cache_key = f"{model_name}_{version_key}"
        if cache_key in self.loaded_models:
            logger.info(f"Retrieving cached model from memory allocation pool: {cache_key}")
            return self.loaded_models[cache_key]

        filepath = self.checkpoint_registry.get(version_key)
        if not filepath or not os.path.exists(filepath):
            logger.warning(f"Version checkpoint {version_key} missing on disk. Creating randomly initialized backbone.")
            model = ModelFactory.create_model(model_name=model_name, pretrained=False)
        else:
            model = ModelFactory.create_model(model_name=model_name, pretrained=False)
            try:
                checkpoint = torch.load(filepath, map_location=device)
                if 'model_state_dict' in checkpoint:
                    model.load_state_dict(checkpoint['model_state_dict'])
                else:
                    model.load_state_dict(checkpoint)
                logger.info(f"Weights state dictionary parsed successfully: {filepath}")
            except Exception as e:
                logger.error(f"Failed to load weights state: {e}")
                
        model.to(device)
        model.eval()
        
        self.loaded_models[cache_key] = model
        return model

    def hot_swap_active_model(self, model_name: str, version_key: str, device: str = "cpu") -> None:
        """
        Runtime swaps active inference model graph without restarting uvicorn ASGI services.
        """
        new_key = f"{model_name}_{version_key}"
        logger.info(f"Hot-swapping active forensic model to: {new_key}")
        
        # Ensure model is initialized
        self.load_model_to_memory(model_name, version_key, device)
        self.active_model_key = new_key
        logger.info(f"Model hot-swap transaction finished successfully. Active model: {new_key}")

    def get_active_model(self, default_name: str = "efficientnet_b0", default_ver: str = "best_model", device: str = "cpu") -> nn.Module:
        """
        Returns active inference network, loading default fallback if none are set.
        """
        if not self.active_model_key:
            self.hot_swap_active_model(default_name, default_ver, device)
            
        return self.loaded_models[self.active_model_key]

    def route_ab_inference(self, image_tensor: torch.Tensor, client_id: str) -> Tuple[torch.Tensor, str]:
        """
        Performs A/B testing splits. Routes traffic based on client identity hashes.
        Routes 50% traffic to Model A, 50% to Model B.
        """
        # Load Model A and Model B keys if available, else standard fallback
        available_keys = list(self.loaded_models.keys())
        if len(available_keys) < 2:
            # Replicate key to satisfy A/B splits
            active = self.get_active_model()
            return active(image_tensor), self.active_model_key or "default"

        # Client hash routing (deterministic split)
        client_hash = hash(client_id)
        selected_key = available_keys[client_hash % 2]
        
        selected_model = self.loaded_models[selected_key]
        logger.debug(f"A/B Inference split routing: Client {client_id} -> Model {selected_key}")
        
        return selected_model(image_tensor), selected_key
