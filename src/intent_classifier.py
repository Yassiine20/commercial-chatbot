"""
Intent Classifier using trained DistilBERT model
Detects out-of-context messages in the chatbot
"""
import torch
from transformers import DistilBertTokenizer
from models.intent_classifier import DistilBertIntentClassifier


class IntentClassifier:
    """Wrapper for DistilBERT intent classification model"""
    
    # Intent mapping
    LABEL_TO_INTENT = {0: 'in_context', 1: 'out_of_context'}
    
    def __init__(self, model, tokenizer, device='cpu'):
        self.model = model
        self.tokenizer = tokenizer
        self.device = device
        self.model.eval()
    
    @classmethod
    def load_from_checkpoint(cls, checkpoint_path, model_name='distilbert-base-uncased', device='cpu'):
        """
        Load trained model from checkpoint
        
        Args:
            checkpoint_path: Path to saved model weights (.pt file)
            model_name: Base model name
            device: Device to load model on ('cpu' or 'cuda')
        
        Returns:
            IntentClassifier instance
        """
        # Load checkpoint
        checkpoint = torch.load(checkpoint_path, map_location=device)
        
        # Initialize model
        model = DistilBertIntentClassifier(
            num_labels=2,
            model_name=model_name,
            dropout=0.1
        )
        
        # Load trained weights
        model.load_state_dict(checkpoint['model_state_dict'])
        model.to(device)
        model.eval()
        
        # Load tokenizer
        tokenizer = DistilBertTokenizer.from_pretrained(model_name)
        
        return cls(model, tokenizer, device)
    
    def predict(self, text, max_length=128):
        """
        Predict intent of input text
        
        Args:
            text: Input text to classify
            max_length: Maximum sequence length
        
        Returns:
            Dict with 'intent' and 'confidence'
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
            'intent': self.LABEL_TO_INTENT[pred_label],
            'confidence': confidence
        }
