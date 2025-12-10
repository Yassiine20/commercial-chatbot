"""Prepare intent classification splits from the expanded dataset."""

from pathlib import Path
import sys

# Add src to path for using split_dataset
sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "preprocessing"))

from split_dataset import split_dataset


def main():
    # Use the expanded dataset that already contains combined samples
    expanded_path = Path("data/intent_classification/raw/training_data_expanded.json")
    if not expanded_path.exists():
        raise FileNotFoundError(f"Expanded dataset not found: {expanded_path}")

    print("=" * 60)
    print("Intent Classification Dataset Preparation")
    print("=" * 60)

    print(f"\n[1] Using expanded dataset at: {expanded_path}")

    # Split into train/val/test and save under splits
    output_dir = "data/intent_classification/splits"
    print(f"\n[2] Splitting into train/val/test → {output_dir}")
    split_dataset(str(expanded_path), output_dir, random_state=42)

    print("\n" + "=" * 60)
    print("Dataset preparation complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
