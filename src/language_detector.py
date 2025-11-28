"""
Simple Language Detector using trained XLM-RoBERTa model
"""
import torch
from transformers import AutoTokenizer
from models.xlm_roberta import XLMRobertaClassifier


class LanguageDetector:
    """Wrapper for XLM-RoBERTa language detection model"""
    
    # Language mapping
    LABEL_TO_LANG = {0: 'en', 1: 'fr', 2: 'ar', 3: 'tn_latn'}
    
    def __init__(self, model, tokenizer, device='cpu'):
        self.model = model
        self.tokenizer = tokenizer
        self.device = device
        self.model.eval()
    
    @classmethod
    def load_from_checkpoint(cls, checkpoint_path, model_name='xlm-roberta-base', device='cpu'):
        """
        Load trained model from checkpoint
        
        Args:
            checkpoint_path: Path to saved model weights (.pt file)
            model_name: Base model name
            device: Device to load model on ('cpu' or 'cuda')
        
        Returns:
            LanguageDetector instance
        """
        # Initialize model (4 languages: en, fr, ar, tn_latn)
        model = XLMRobertaClassifier(
            num_labels=4,
            model_name=model_name,
            gradient_checkpointing=False,
            load_in_8bit=False,
            use_lora=False
        )
        
        # Load trained weights
        checkpoint = torch.load(checkpoint_path, map_location=device)
        model.load_state_dict(checkpoint)
        model = model.to(device)
        model.eval()
        
        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        return cls(model, tokenizer, device)
    
    def predict(self, text, max_length=128):
        """
        Predict language of input text
        
        Args:
            text: Input text to classify
            max_length: Maximum sequence length
        
        Returns:
            Dict with 'language' and 'confidence'
        """
        # Tokenize
        inputs = self.tokenizer(
            text,
            padding='max_length',
            truncation=True,
            max_length=max_length,
            return_tensors='pt'
        )
        
        # Move to device
        input_ids = inputs['input_ids'].to(self.device)
        attention_mask = inputs['attention_mask'].to(self.device)
        
        # Predict
        with torch.no_grad():
            outputs = self.model(input_ids, attention_mask)
            logits = outputs.logits
            probs = torch.softmax(logits, dim=1)
            pred_label = torch.argmax(probs, dim=1).item()
            confidence = probs[0, pred_label].item()
        
        return {
            'language': self.LABEL_TO_LANG[pred_label],
            'confidence': confidence
        }
