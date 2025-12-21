#!/usr/bin/env python3
"""Script to prepare dataset for training."""
import sys
from pathlib import Path


project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import argparse
from app.utils.dataset_utils import split_dataset, convert_labelme_to_yolo
from app.training.train_yolov8 import create_dataset_yaml


def main():
    parser = argparse.ArgumentParser(description="Prepare dataset for training")
    parser.add_argument("--source", type=str, required=True, help="Source directory with images")
    parser.add_argument("--train-ratio", type=float, default=0.7, help="Training set ratio")
    parser.add_argument("--val-ratio", type=float, default=0.2, help="Validation set ratio")
    parser.add_argument("--test-ratio", type=float, default=0.1, help="Test set ratio")
    parser.add_argument("--output-dir", type=str, default="data", help="Output directory")
    parser.add_argument("--create-yaml", action="store_true", help="Create dataset YAML file")
    
    args = parser.parse_args()
    
    # Define output directories
    train_dir = Path(args.output_dir) / "train"
    val_dir = Path(args.output_dir) / "val"
    test_dir = Path(args.output_dir) / "test"
    
    # Split dataset
    print("Splitting dataset...")
    split_dataset(
        source_dir=args.source,
        train_dir=str(train_dir),
        val_dir=str(val_dir),
        test_dir=str(test_dir),
        train_ratio=args.train_ratio,
        val_ratio=args.val_ratio,
        test_ratio=args.test_ratio
    )
    
    # Create dataset YAML if requested
    if args.create_yaml:
        print("Creating dataset YAML...")
        create_dataset_yaml(
            train_dir=str(train_dir),
            val_dir=str(val_dir),
            test_dir=str(test_dir),
            output_path=str(Path(args.output_dir) / "dataset.yaml")
        )
    
    print("Dataset preparation completed!")


if __name__ == "__main__":
    main()

