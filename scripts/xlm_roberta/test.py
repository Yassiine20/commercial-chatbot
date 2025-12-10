
import json
import torch
import sys
from pathlib import Path
from tqdm import tqdm

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from models.xlm_roberta import XLMRobertaClassifier
from preprocessing.data_loaders import get_dataloaders


def evaluate_model(model, test_loader, device):
    model.eval()
    correct = 0
    total = 0
    predictions = []
    true_labels = []
    
    label_names = {0: 'en', 1: 'fr', 2: 'ar', 3: 'tn_latn'}
    
    with torch.no_grad():
        for batch in tqdm(test_loader, desc="Testing"):
            input_ids = batch['input_ids'].to(device)
            mask = batch['attention_mask'].to(device)
            labels = batch['label'].to(device)
            
            outputs = model(input_ids, mask, labels=labels)
            preds = torch.argmax(outputs.logits, dim=1)
            
            correct += (preds == labels).sum().item()
            total += labels.size(0)
            
            predictions.extend(preds.cpu().numpy())
            true_labels.extend(labels.cpu().numpy())
    
    accuracy = correct / total
    
    # Per-class accuracy
    class_correct = {i: 0 for i in range(4)}
    class_total = {i: 0 for i in range(4)}
    
    for pred, true in zip(predictions, true_labels):
        class_total[true] += 1
        if pred == true:
            class_correct[true] += 1
    
    print(f"\n{'='*50}")
    print(f"Overall Test Accuracy: {accuracy*100:.2f}%")
    print(f"{'='*50}\n")
    
    print("Per-Language Accuracy:")
    print(f"{'Language':<15} {'Accuracy':<10} {'Samples'}")
    print("-" * 40)
    for i in range(4):
        lang = label_names[i]
        acc = (class_correct[i] / class_total[i] * 100) if class_total[i] > 0 else 0
        print(f"{lang:<15} {acc:>6.2f}%     {class_total[i]:>6}")
    print("-" * 40)
    
    return accuracy, predictions, true_labels


def main():
    with open('configs/xlm_roberta/config.json', 'r') as f:
        config = json.load(f)
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Device: {device}\n")
    
    # Load test data
    _, _, test_loader = get_dataloaders(
        batch_size=32,  # Use larger batch for testing
        model_name=config['model_name'],
        max_length=config.get('max_length', 128)
    )
    
    # Load model
    print("Loading model...")
    model = XLMRobertaClassifier(
        num_labels=config['num_labels'],
        model_name=config['model_name'],
        gradient_checkpointing=config.get('gradient_checkpointing', False),
        load_in_8bit=config.get('load_in_8bit', False),
        use_lora=config.get('use_lora', False),
        lora_r=config.get('lora_r', 16),
        lora_alpha=config.get('lora_alpha', 32),
        lora_dropout=config.get('lora_dropout', 0.05)
    )
    
    # Load trained weights
    if config.get('load_in_8bit', False):
        # For 8-bit model, only load classifier weights
        checkpoint = torch.load(f"{config['save_dir']}/best_model.pt", map_location=device)
        # Filter only classifier weights
        classifier_weights = {k: v for k, v in checkpoint.items() if 'classifier' in k}
        model.load_state_dict(classifier_weights, strict=False)
        print("Loaded classifier weights from checkpoint\n")
    else:
        model.load_state_dict(torch.load(f"{config['save_dir']}/best_model.pt", map_location=device))
        model = model.to(device)
        print("Loaded full model from checkpoint\n")
    
    # Evaluate
    accuracy, predictions, true_labels = evaluate_model(model, test_loader, device)
    
    # Save results
    results = {
        'test_accuracy': float(accuracy),
        'num_samples': len(true_labels),
        'predictions': [int(p) for p in predictions],
        'true_labels': [int(t) for t in true_labels]
    }
    
    with open(f"{config['save_dir']}/test_results.json", 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to {config['save_dir']}/test_results.json")


if __name__ == '__main__':
    main()
