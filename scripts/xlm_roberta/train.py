
import json
import torch
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from models.xlm_roberta import XLMRobertaClassifier
from training.trainer import Trainer
from data.preprocessing.data_loaders import get_dataloaders


def main():
    with open('configs/xlm_roberta/config.json', 'r') as f:
        config = json.load(f)
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Device: {device}\n")
    
    train_loader, val_loader, _ = get_dataloaders(
        config['batch_size'], 
        model_name=config['model_name'],
        max_length=config.get('max_length', 128)
    )
    
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
    
    # Don't move to device if using 8-bit (already handled by device_map)
    if not config.get('load_in_8bit', False):
        model = model.to(device)
    
    # Use memory-efficient optimizer
    if config.get('optimizer', 'adamw') == 'sgd':
        optimizer = torch.optim.SGD(model.parameters(), lr=config['learning_rate'], momentum=0.9)
    else:
        optimizer = torch.optim.AdamW(model.parameters(), lr=config['learning_rate'])
    
    trainer = Trainer(
        model=model,
        train_loader=train_loader,
        val_loader=val_loader,
        optimizer=optimizer,
        device=device,
        save_dir=config['save_dir'],
        gradient_accumulation_steps=config.get('gradient_accumulation_steps', 1),
        use_fp16=config.get('use_fp16', False)
    )
    
    trainer.train(config['epochs'])


if __name__ == '__main__':
    main()
