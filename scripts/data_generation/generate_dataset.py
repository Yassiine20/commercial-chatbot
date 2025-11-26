

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.data.generators.generator import DatasetGenerator


def main():
    parser = argparse.ArgumentParser(description='Generate multilingual dataset')
    parser.add_argument('--seed', type=int, default=42, help='Random seed (default: 42)')
    parser.add_argument('--output-dir', type=str, default='data/language_detection/generated', help='Output directory (default: data/language_detection/generated)')
    
    args = parser.parse_args()
    os.makedirs(args.output_dir, exist_ok=True)
    
    generator = DatasetGenerator(seed=args.seed)
    
    samples = generator.generate_all()
    
    print("\nExporting datasets...")
    combined_path = os.path.join(args.output_dir, 'combined_dataset.json')
    generator.export_to_json(samples, combined_path)
    generator.export_by_language(samples, args.output_dir)
    
    print("\n" + "=" * 60)
    print("✓ Dataset generation complete!")
    print("=" * 60)
    print(f"\nFiles created:")
    print(f"  - {combined_path}")
    print(f"  - {args.output_dir}/<language>.json (per language)")
    print(f"\nNext: Review Tunisian dialect samples for authenticity")


if __name__ == '__main__':
    main()
