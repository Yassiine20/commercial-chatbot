"""
Simple Language Detector using trained XLM-RoBERTa model
"""
import torch
from transformers import AutoTokenizer
from models.xlm_roberta import XLMRobertaClassifier


class LanguageDetector:
    """Wrapper for XLM-RoBERTa language detection model"""
    
    # Language mapping (5th label maps to ar for compatibility)
    LABEL_TO_LANG = {0: 'en', 1: 'fr', 2: 'ar', 3: 'tn_latn', 4: 'ar'}
    
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
        # Initialize model (5 languages to match checkpoint)
        model = XLMRobertaClassifier(
            num_labels=5,
            model_name=model_name,
            gradient_checkpointing=False,
            load_in_8bit=True,
            use_lora=True,
            lora_r=16,
            lora_alpha=32,
            lora_dropout=0.05
        )
        
        # Load trained weights
        checkpoint = torch.load(checkpoint_path, map_location=device)
        model.load_state_dict(checkpoint, strict=False)
        model.eval()
        
        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        # 8-bit models are auto-loaded on GPU, so use 'cuda' as device
        actual_device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        return cls(model, tokenizer, actual_device)
    
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
