#!/usr/bin/env python3
"""Script to train both YOLOv8 and Mask R-CNN models."""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import argparse
import subprocess
import time
import yaml
from pathlib import Path


def run_command(cmd: list, description: str) -> bool:
    """Run a command and return success status."""
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}")
    print(f"Command: {' '.join(cmd)}")
    print("")
    
    start_time = time.time()
    result = subprocess.run(cmd, cwd=project_root)
    elapsed = time.time() - start_time
    
    if result.returncode == 0:
        print(f"\n{description} completed in {elapsed/60:.1f} minutes")
        return True
    else:
        print(f"\n{description} failed with exit code {result.returncode}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Train both YOLOv8 and Mask R-CNN models")
    parser.add_argument("--data", type=str, default="data/dataset.yaml",
                       help="Path to dataset YAML file")
    parser.add_argument("--epochs", type=int, default=100,
                       help="Number of training epochs")
    parser.add_argument("--imgsz", type=int, default=640,
                       help="Image size for training")
    parser.add_argument("--batch", type=int, default=16,
                       help="Batch size")
    parser.add_argument("--yolov8-only", action="store_true",
                       help="Train only YOLOv8")
    parser.add_argument("--mask-rcnn-only", action="store_true",
                       help="Train only Mask R-CNN")
    args = parser.parse_args()
    
    dataset_path = Path(args.data)
    if not dataset_path.exists():
        print(f"Dataset file not found: {dataset_path}")
        print("Please prepare the dataset first:")
        print("   python scripts/prepare_dataset.py --source <dataset_dir> --create-yaml")
        return 1
    
    with open(dataset_path, 'r') as f:
        dataset_config = yaml.safe_load(f)
    
    base_path = Path(dataset_config.get('path', dataset_path.parent))
    train_subdir = dataset_config.get('train', 'train')
    val_subdir = dataset_config.get('val', 'val')
    
    train_dir = base_path / train_subdir
    val_dir = base_path / val_subdir
    
    if not train_dir.exists() or not val_dir.exists():
        print(f"Dataset directories not found:")
        print(f"   Base path: {base_path}")
        print(f"   Train: {train_dir}")
        print(f"   Val: {val_dir}")
        return 1
    
    print("Entraînement des modèles de détection de fissures")
    print("=" * 60)
    print(f"Dataset: {args.data}")
    print(f"Epochs: {args.epochs}")
    print(f"Image size: {args.imgsz}")
    print(f"Batch size: {args.batch}")
    print("")
    
    all_success = True
    
    if not args.mask_rcnn_only:
        yolov8_cmd = [
            "python", "app/training/train_yolov8.py",
            "--data", args.data,
            "--epochs", str(args.epochs),
            "--imgsz", str(args.imgsz),
            "--batch", str(args.batch)
        ]
        
        if not run_command(yolov8_cmd, "Training YOLOv8"):
            all_success = False
            if not args.yolov8_only:
                print("\nYOLOv8 training failed. Continue with Mask R-CNN? (y/n): ", end="")
                response = input().strip().lower()
                if response != 'y':
                    return 1
    
    if not args.yolov8_only:
        print("\n" + "="*60)
        print("Converting YOLO dataset to COCO format for Mask R-CNN...")
        print("="*60)
        
        coco_dir = Path("data/coco_format")
        coco_dir.mkdir(parents=True, exist_ok=True)
        
        train_json = coco_dir / "train.json"
        val_json = coco_dir / "val.json"
        
        from app.training.train_mask_rcnn import convert_yolo_to_coco
        
        class_names = dataset_config.get('names', ['crack', 'pothole'])
        
        print(f"Converting training set...")
        convert_yolo_to_coco(
            images_dir=str(train_dir),
            labels_dir=str(train_dir),
            output_json=str(train_json),
            class_names=class_names
        )
        
        print(f"Converting validation set...")
        convert_yolo_to_coco(
            images_dir=str(val_dir),
            labels_dir=str(val_dir),
            output_json=str(val_json),
            class_names=class_names
        )
        
        mask_rcnn_cmd = [
            "python", "app/training/train_mask_rcnn.py",
            "--train-json", str(train_json),
            "--train-images", str(train_dir),
            "--val-json", str(val_json),
            "--val-images", str(val_dir),
            "--epochs", str(args.epochs),
            "--batch-size", str(args.batch)
        ]
        
        if not run_command(mask_rcnn_cmd, "Training Mask R-CNN"):
            all_success = False
    
    print("\n" + "=" * 60)
    if all_success:
        print("Entraînement terminé avec succès !")
        print("")
        print("Prochaines étapes:")
        print("   1. Extraire les métriques:")
        print("      python scripts/extract_training_metrics.py --output metrics.json")
        print("")
        print("   2. Générer le rapport:")
        print("      python scripts/generate_report.py --metrics metrics.json --output reports")
        print("")
        print("   3. Exporter en ONNX:")
        print("      python scripts/export_to_onnx.py --model yolov8 --weights weights/yolov8_cracks.pt")
        print("      python scripts/export_to_onnx.py --model mask_rcnn --weights weights/mask_rcnn_cracks.pth")
        print("")
        print("   4. Valider les critères:")
        print("      python scripts/validate_criteria.py --metrics metrics.json")
        return 0
    else:
        print("Certains entraînements ont échoué")
        return 1


if __name__ == "__main__":
    exit(main())

