import torch
import torch.nn as nn
import timm
import math
from ai_engine.utils.logger import setup_logger

logger = setup_logger("temporal_transformer")

class PositionalEncoding(nn.Module):
    """
    Standard sinusoidal positional encoding mapping sequence indices.
    """
    def __init__(self, d_model: int, max_len: int = 100):
        super(PositionalEncoding, self).__init__()
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        self.register_buffer('pe', pe.unsqueeze(0))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Adds coordinate mapping to sequence tensor (Batch, Seq, Dim)
        return x + self.pe[:, :x.size(1)]

class TemporalTransformerClassifier(nn.Module):
    """
    Transformer-based sequence network designed to compute self-attention correlations
    between sequential frame representations.
    """
    def __init__(self, cnn_backbone: str = "resnet18", num_heads: int = 4, num_layers: int = 2, num_classes: int = 1, pretrained: bool = True, dropout_rate: float = 0.5):
        super(TemporalTransformerClassifier, self).__init__()
        
        logger.info(f"Instantiating Temporal Transformer: Backbone={cnn_backbone}, Heads={num_heads}, Layers={num_layers}")
        
        self.feature_extractor = timm.create_model(
            cnn_backbone, pretrained=pretrained, num_classes=0
        )
        
        for param in self.feature_extractor.parameters():
            param.requires_grad = False
            
        num_features = self.feature_extractor.num_features
        
        self.pos_encoder = PositionalEncoding(d_model=num_features)
        
        # Transformer Encoder Block
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=num_features,
            nhead=num_heads,
            dim_feedforward=num_features * 2,
            dropout=dropout_rate,
            batch_first=True
        )
        self.transformer_encoder = nn.TransformerEncoder(
            encoder_layer, num_layers=num_layers
        )
        
        # Pooling parameter (Mean sequence representation)
        self.classifier = nn.Sequential(
            nn.Dropout(p=dropout_rate),
            nn.Linear(num_features, num_classes),
            nn.Sigmoid()
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Input shape: (Batch, Sequence_Length, C, H, W)
        """
        batch_size, seq_len, C, H, W = x.size()
        
        x_flattened = x.view(batch_size * seq_len, C, H, W)
        spatial_features = self.feature_extractor(x_flattened)
        
        # Transform mapping shape: (Batch, Seq, Features)
        transformer_input = spatial_features.view(batch_size, seq_len, -1)
        transformer_input = self.pos_encoder(transformer_input)
        
        # Run self-attention layers
        attention_out = self.transformer_encoder(transformer_input)
        
        # Mean sequence pooling (aggregates temporal information)
        seq_mean = torch.mean(attention_out, dim=1)
        
        predictions = self.classifier(seq_mean)
        return predictions
