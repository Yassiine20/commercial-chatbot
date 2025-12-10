"""
DistilBERT Intent Classifier Model
Binary classification for in-context vs out-of-context detection
"""
import torch
import torch.nn as nn
from transformers import DistilBertModel, DistilBertConfig


class DistilBertIntentClassifier(nn.Module):
    """
    DistilBERT-based binary classifier for intent classification
    
    Args:
        num_labels: Number of classes (default: 2 for binary classification)
        model_name: Pre-trained model name (default: 'distilbert-base-uncased')
        dropout: Dropout probability (default: 0.1)
    """
    
    def __init__(self, num_labels=2, model_name='distilbert-base-uncased', dropout=0.1):
        super().__init__()
        
        # Load pretrained DistilBERT
        self.distilbert = DistilBertModel.from_pretrained(model_name)
        hidden_size = self.distilbert.config.hidden_size
        
        # Classification head
        self.classifier = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(hidden_size, num_labels)
        )
        
        self.num_labels = num_labels
        self.loss_fn = nn.CrossEntropyLoss()
    
    def forward(self, input_ids, attention_mask, labels=None):
        """
        Forward pass
        
        Args:
            input_ids: Input token IDs [batch_size, seq_len]
            attention_mask: Attention mask [batch_size, seq_len]
            labels: Ground truth labels [batch_size] (optional)
            
        Returns:
            SimpleNamespace with loss and logits
        """
        # Get DistilBERT outputs
        outputs = self.distilbert(input_ids=input_ids, attention_mask=attention_mask)
        
        # Use CLS token representation (first token)
        pooled_output = outputs.last_hidden_state[:, 0, :]
        
        # Classification
        logits = self.classifier(pooled_output)
        
        # Calculate loss if labels provided
        loss = None
        if labels is not None:
            loss = self.loss_fn(logits, labels)
        
        # Return in HuggingFace format
        from types import SimpleNamespace
        return SimpleNamespace(loss=loss, logits=logits)
    
    def save_checkpoint(self, path):
        """Save model checkpoint"""
        torch.save({
            'model_state_dict': self.state_dict(),
            'num_labels': self.num_labels
        }, path)
        print(f"✓ Model checkpoint saved to {path}")
    
    @classmethod
    def load_checkpoint(cls, path, model_name='distilbert-base-uncased', device='cpu'):
        """Load model from checkpoint"""
        checkpoint = torch.load(path, map_location=device)
        model = cls(num_labels=checkpoint['num_labels'], model_name=model_name)
        model.load_state_dict(checkpoint['model_state_dict'])
        model.to(device)
        model.eval()
        return model
