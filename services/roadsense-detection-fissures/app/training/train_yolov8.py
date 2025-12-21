"""Training script for YOLOv8 model."""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import os
from ultralytics import YOLO
import yaml
from app.utils.config_loader import config


def train_yolov8(
    data_yaml: str,
    epochs: int = None,
    imgsz: int = None,
    batch: int = None,
    device: str = None
) -> str:
    """Train YOLOv8 model for crack detection.
    
    Args:
        data_yaml: Path to dataset YAML file
        epochs: Number of training epochs
        imgsz: Image size
        batch: Batch size
        device: Device to use (cuda device, cpu, or 0,1,2,3). If None, auto-detect.
    
    Returns:
        Path to best model weights
    """
    import torch
    
    epochs = epochs or config.get("training.epochs", 100)
    imgsz = imgsz or config.get("dataset.image_size", 640)
    batch = batch or config.get("dataset.batch_size", 16)
    
    if device is None:
        if torch.cuda.is_available():
            device = "0"
            print(f"CUDA disponible, utilisation du GPU: {device}")
        else:
            device = "cpu"
            print("CUDA non disponible, utilisation du CPU")
    
    model = YOLO("yolov8n.pt")
    results = model.train(
        data=data_yaml,
        epochs=epochs,
        imgsz=imgsz,
        batch=batch,
        device=device,
        patience=config.get("training.patience", 50),
        save_period=config.get("training.save_period", 10),
        lr0=config.get("training.learning_rate", 0.01),
        weight_decay=config.get("training.weight_decay", 0.0005),
        momentum=config.get("training.momentum", 0.937),
        warmup_epochs=config.get("training.warmup_epochs", 3),
        # Augmentation
        hsv_h=config.get("augmentation.hsv_h", 0.015),
        hsv_s=config.get("augmentation.hsv_s", 0.7),
        hsv_v=config.get("augmentation.hsv_v", 0.4),
        degrees=config.get("augmentation.degrees", 10),
        translate=config.get("augmentation.translate", 0.1),
        scale=config.get("augmentation.scale", 0.5),
        flipud=config.get("augmentation.flipud", 0.0),
        fliplr=config.get("augmentation.fliplr", 0.5),
        mosaic=config.get("augmentation.mosaic", 1.0),
        mixup=config.get("augmentation.mixup", 0.1),
        project="runs/detect",
        name="yolov8_cracks",
        exist_ok=True
    )
    
    best_model_path = results.save_dir / "weights" / "best.pt"
    weights_dir = Path("weights")
    weights_dir.mkdir(exist_ok=True)
    target_path = weights_dir / "yolov8_cracks.pt"
    
    import shutil
    shutil.copy2(best_model_path, target_path)
    
    print(f"Training completed. Best model saved to: {target_path}")
    print(f"mAP50: {results.results_dict.get('metrics/mAP50(B)', 'N/A')}")
    print(f"mAP50-95: {results.results_dict.get('metrics/mAP50-95(B)', 'N/A')}")
    
    return str(target_path)


def create_dataset_yaml(
    train_dir: str,
    val_dir: str,
    test_dir: str = None,
    output_path: str = "data/dataset.yaml",
    num_classes: int = 2,
    class_names: list = None
) -> str:
    """Create YOLOv8 dataset YAML file.
    
    Args:
        train_dir: Training images directory
        val_dir: Validation images directory
        test_dir: Test images directory (optional)
        output_path: Output YAML file path
        num_classes: Number of classes
        class_names: List of class names
    
    Returns:
        Path to created YAML file
    """
    if class_names is None:
        class_names = ["crack", "pothole"]  # Support for both cracks and potholes
    
    dataset_config = {
        "path": str(Path(train_dir).parent.absolute()),
        "train": str(Path(train_dir).name),
        "val": str(Path(val_dir).name),
        "nc": num_classes,
        "names": class_names
    }
    
    if test_dir:
        dataset_config["test"] = str(Path(test_dir).name)
    
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        yaml.dump(dataset_config, f, default_flow_style=False)
    
    print(f"Dataset YAML created at: {output_path}")
    return str(output_path)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Train YOLOv8 model")
    parser.add_argument("--data", type=str, required=True, help="Path to dataset YAML")
    parser.add_argument("--epochs", type=int, default=100, help="Number of epochs")
    parser.add_argument("--imgsz", type=int, default=640, help="Image size")
    parser.add_argument("--batch", type=int, default=16, help="Batch size")
    parser.add_argument("--device", type=str, default=None,
                       help="Device (auto-detect if not specified: 'cpu' or '0' for GPU)")
    
    args = parser.parse_args()
    
    train_yolov8(
        data_yaml=args.data,
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        device=args.device
    )

