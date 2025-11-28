import json
import os
from sklearn.model_selection import train_test_split


def split_dataset(input_path, output_dir, random_state=42):
    
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    samples = data['samples']
    labels = [s['language'] for s in samples]
    
    print(f"Total samples: {len(samples)}")
    
    # Split: 70% train, 30% temp
    train_samples, temp_samples, train_labels, temp_labels = train_test_split(
        samples, labels, test_size=0.30, stratify=labels, random_state=random_state
    )
    
    # Split temp: 50% val, 50% test (15% each of original)
    val_samples, test_samples = train_test_split(
        temp_samples, test_size=0.50, stratify=temp_labels, random_state=random_state
    )
    
    os.makedirs(output_dir, exist_ok=True)
    
    for name, split_samples in [('train', train_samples), ('val', val_samples), ('test', test_samples)]:
        output_path = os.path.join(output_dir, f'{name}.json')
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump({'samples': split_samples}, f, ensure_ascii=False, indent=2)
        print(f"✓ {name}: {len(split_samples)} samples → {output_path}")
    
    print("✓ Done")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', default='data/raw/combined_dataset.json')
    parser.add_argument('--output-dir', default='data/language_detection/splits')
    parser.add_argument('--seed', type=int, default=42)
    args = parser.parse_args()
    
    split_dataset(args.input, args.output_dir, args.seed)


