from torchvision import transforms
from typing import Dict, Any

class ImageAugmentor:
    """
    Constructs torchvision transforms based on configured complexity profiles.
    """
    def __init__(self, mode: str = "medium", config: Any = None):
        self.mode = mode.lower().strip()
        self.config = config

    def get_transforms(self) -> transforms.Compose:
        """
        Returns augmentations based on target complexity modes.
        """
        if self.mode == "light":
            return transforms.Compose([
                transforms.RandomHorizontalFlip(p=0.5),
                transforms.RandomRotation(degrees=10),
            ])
            
        elif self.mode == "heavy":
            return transforms.Compose([
                transforms.RandomHorizontalFlip(p=0.5),
                transforms.RandomVerticalFlip(p=0.2),
                transforms.RandomRotation(degrees=30),
                transforms.ColorJitter(brightness=0.3, contrast=0.3, saturation=0.2, hue=0.1),
                transforms.RandomAffine(degrees=0, translate=(0.1, 0.1), scale=(0.9, 1.1)),
                transforms.GaussianBlur(kernel_size=(3, 3), sigma=(0.1, 2.0)),
            ])
            
        else: # medium (default standard training augmentations)
            return transforms.Compose([
                transforms.RandomHorizontalFlip(p=0.5),
                transforms.RandomRotation(degrees=15),
                transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.1, hue=0.05),
            ])
