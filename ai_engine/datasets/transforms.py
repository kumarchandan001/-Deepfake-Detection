from torchvision import transforms
from ai_engine.preprocessing.augmentation import ImageAugmentor
from ai_engine.utils.config import Config

def get_train_transforms() -> transforms.Compose:
    """
    Retrieves training data augmentations parsed from configuration complexity modes.
    """
    config = Config()
    mode = config.get("training.augmentation_mode", "medium")
    augmentor = ImageAugmentor(mode=mode)
    return augmentor.get_transforms()

def get_val_transforms() -> transforms.Compose:
    """
    Validation datasets require raw scaling metrics with no horizontal flips.
    """
    return transforms.Compose([])
