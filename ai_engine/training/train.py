import os
from torch.utils.data import DataLoader
from ai_engine.utils.config import Config
from ai_engine.utils.device import get_device
from ai_engine.datasets.dataset import DeepfakeImageDataset
from ai_engine.datasets.transforms import get_train_transforms, get_val_transforms
from ai_engine.models.model_factory import ModelFactory
from ai_engine.training.trainer import DeepfakeTrainer
from ai_engine.utils.logger import setup_logger

logger = setup_logger("train_entrypoint")

def main():
    logger.info("Initializing Deepfake Detection Training Gateway...")
    
    config = Config()
    
    dataset_root = config.get("dataset.root_dir", "datasets")
    target_size = tuple(config.get("dataset.target_size", [224, 224]))
    batch_size = config.get("dataset.batch_size", 16)
    
    train_dir = os.path.join(dataset_root, "train")
    val_dir = os.path.join(dataset_root, "val")
    
    if not os.path.exists(train_dir) or not os.path.exists(val_dir):
        logger.error(f"Missing dataset folders inside '{dataset_root}'. Run data generators or mount pipelines.")
        return
        
    logger.info("Instantiating dataset mapping pipelines...")
    train_dataset = DeepfakeImageDataset(
        split_dir=train_dir,
        target_size=target_size,
        transform=get_train_transforms(),
        extract_faces=True
    )
    
    val_dataset = DeepfakeImageDataset(
        split_dir=val_dir,
        target_size=target_size,
        transform=get_val_transforms(),
        extract_faces=True
    )
    
    train_loader = DataLoader(
        train_dataset, 
        batch_size=batch_size, 
        shuffle=True, 
        num_workers=config.get("dataset.num_workers", 0)
    )
    val_loader = DataLoader(
        val_dataset, 
        batch_size=batch_size, 
        shuffle=False, 
        num_workers=config.get("dataset.num_workers", 0)
    )
    
    device = get_device()
    
    model = ModelFactory.create_model(
        model_name=config.get("model.backbone", "efficientnet_b0"),
        pretrained=config.get("model.pretrained", True),
        dropout_rate=config.get("model.dropout_rate", 0.5)
    )
    
    trainer = DeepfakeTrainer(
        model=model,
        train_loader=train_loader,
        val_loader=val_loader,
        config=config,
        device=device
    )
    
    history = trainer.train()
    logger.info("Training gateway loop exited successfully.")

if __name__ == "__main__":
    main()
