import torch
import torch.nn as nn
import timm
from ai_engine.utils.logger import setup_logger

logger = setup_logger("cnn_lstm_model")

class CNNLSTMClassifier(nn.Module):
    """
    Hybrid deep network extracting frame-level spatial representations 
    via pre-trained CNN backbones and modeling sequential dependencies with LSTMs.
    """
    def __init__(self, cnn_backbone: str = "resnet18", lstm_hidden_dim: int = 128, num_lstm_layers: int = 1, num_classes: int = 1, pretrained: bool = True, dropout_rate: float = 0.5):
        super(CNNLSTMClassifier, self).__init__()
        
        logger.info(f"Instantiating CNN-LSTM: CNN={cnn_backbone}, LSTM_Dim={lstm_hidden_dim}, Layers={num_lstm_layers}")
        
        # 1. Feature Extractor Backbone (Global pooling output)
        self.feature_extractor = timm.create_model(
            cnn_backbone, pretrained=pretrained, num_classes=0
        )
        
        # Freeze spatial features backbone (Optional, but highly recommended during initial training phase)
        for param in self.feature_extractor.parameters():
            param.requires_grad = False
            
        num_features = self.feature_extractor.num_features
        
        # 2. LSTM Sequence Modeling Layer
        self.lstm = nn.LSTM(
            input_size=num_features,
            hidden_size=lstm_hidden_dim,
            num_layers=num_lstm_layers,
            batch_first=True,
            bidirectional=True
        )
        
        # 3. Dense Classifier layer
        # Multiply by 2 since bidirectional is active (2 * lstm_hidden_dim)
        self.classifier = nn.Sequential(
            nn.Dropout(p=dropout_rate),
            nn.Linear(lstm_hidden_dim * 2, num_classes),
            nn.Sigmoid()
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Input shape: (Batch, Sequence_Length, C, H, W)
        """
        batch_size, seq_len, C, H, W = x.size()
        
        # Flatten temporal and batch dimensions to run feature extractor concurrently
        x_flattened = x.view(batch_size * seq_len, C, H, W)
        spatial_features = self.feature_extractor(x_flattened) # Shape: (Batch * Seq, Features)
        
        # Re-pack temporal mapping: (Batch, Sequence_Length, Features)
        lstm_input = spatial_features.view(batch_size, seq_len, -1)
        
        # LSTM forward pass
        lstm_out, _ = self.lstm(lstm_input) # Shape: (Batch, Seq, Hidden * 2)
        
        # Extract features from final temporal step (Sequence mapping aggregation)
        final_temporal_features = lstm_out[:, -1, :] # Shape: (Batch, Hidden * 2)
        
        predictions = self.classifier(final_temporal_features)
        return predictions
