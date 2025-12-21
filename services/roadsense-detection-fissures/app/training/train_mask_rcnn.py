"""Training script for Mask R-CNN model using Detectron2."""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import os
import torch
from detectron2 import model_zoo
from detectron2.engine import DefaultTrainer, DefaultPredictor
from detectron2.config import get_cfg
from detectron2.data import DatasetCatalog, MetadataCatalog, build_detection_train_loader
from detectron2.data.datasets import register_coco_instances
from detectron2.utils.visualizer import Visualizer
from detectron2.evaluation import COCOEvaluator
import cv2
from app.utils.config_loader import config


def register_dataset(dataset_name: str, json_file: str, image_root: str):
    """Register COCO format dataset.
    
    Args:
        dataset_name: Name of the dataset
        json_file: Path to COCO JSON annotation file
        image_root: Root directory of images
    """
    register_coco_instances(dataset_name, {}, json_file, image_root)
    MetadataCatalog.get(dataset_name).set(thing_classes=["crack", "pothole"])


def train_mask_rcnn(
    train_dataset_name: str,
    val_dataset_name: str,
    output_dir: str = "output/mask_rcnn",
    epochs: int = None,
    batch_size: int = None,
    learning_rate: float = None,
    device: str = None
) -> str:
    """Train Mask R-CNN model for crack detection.
    
    Args:
        train_dataset_name: Name of registered training dataset
        val_dataset_name: Name of registered validation dataset
        output_dir: Output directory for model checkpoints
        epochs: Number of training epochs
        batch_size: Batch size per image
        learning_rate: Learning rate
        device: Device to use (cuda or cpu). If None, auto-detect.
    
    Returns:
        Path to best model weights
    """
    if device is None:
        if torch.cuda.is_available():
            device = "cuda"
            print(f"CUDA disponible, utilisation du GPU")
        else:
            device = "cpu"
            print("CUDA non disponible, utilisation du CPU")
    
    epochs = epochs or config.get("training.epochs", 100)
    batch_size = batch_size or config.get("dataset.batch_size", 16)
    learning_rate = learning_rate or config.get("training.learning_rate", 0.01)
    
    cfg = get_cfg()
    cfg.merge_from_file(model_zoo.get_config_file("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml"))
    cfg.DATASETS.TRAIN = (train_dataset_name,)
    cfg.DATASETS.TEST = (val_dataset_name,)
    cfg.DATALOADER.NUM_WORKERS = config.get("dataset.num_workers", 4)
    cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml")
    cfg.SOLVER.IMS_PER_BATCH = batch_size
    cfg.SOLVER.BASE_LR = learning_rate
    cfg.SOLVER.MAX_ITER = epochs * 1000  # Approximate
    cfg.SOLVER.STEPS = []
    cfg.MODEL.ROI_HEADS.BATCH_SIZE_PER_IMAGE = 512
    cfg.MODEL.ROI_HEADS.NUM_CLASSES = 1
    cfg.MODEL.DEVICE = device
    cfg.OUTPUT_DIR = output_dir
    
    os.makedirs(output_dir, exist_ok=True)
    
    trainer = DefaultTrainer(cfg)
    trainer.resume_or_load(resume=False)
    trainer.train()
    
    weights_path = Path(output_dir) / "model_final.pth"
    target_path = Path("weights") / "mask_rcnn_cracks.pth"
    target_path.parent.mkdir(exist_ok=True)
    
    import shutil
    shutil.copy2(weights_path, target_path)
    
    print(f"Training completed. Model saved to: {target_path}")
    
    return str(target_path)


def convert_yolo_to_coco(
    images_dir: str,
    labels_dir: str,
    output_json: str,
    class_names: list = None
):
    """Convert YOLO format annotations to COCO format.
    
    Args:
        images_dir: Directory containing images
        images_dir: Directory containing YOLO format labels
        output_json: Output COCO JSON file path
        class_names: List of class names
    """
    import json
    from pathlib import Path
    
    if class_names is None:
        class_names = ["crack"]
    
    images_path = Path(images_dir)
    labels_path = Path(labels_dir)
    
    coco_data = {
        "images": [],
        "annotations": [],
        "categories": [{"id": i, "name": name} for i, name in enumerate(class_names)]
    }
    
    image_id = 0
    annotation_id = 0
    
    for img_file in images_path.glob("*.jpg"):
        img = cv2.imread(str(img_file))
        if img is None:
            continue
        
        h, w = img.shape[:2]
        
        coco_data["images"].append({
            "id": image_id,
            "file_name": img_file.name,
            "width": w,
            "height": h
        })
        
        label_file = labels_path / img_file.with_suffix(".txt").name
        if label_file.exists():
            with open(label_file, 'r') as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) == 5:
                        class_id, center_x, center_y, width, height = map(float, parts)
                        
                        x = (center_x - width / 2) * w
                        y = (center_y - height / 2) * h
                        bbox_width = width * w
                        bbox_height = height * h
                        
                        coco_data["annotations"].append({
                            "id": annotation_id,
                            "image_id": image_id,
                            "category_id": int(class_id),
                            "bbox": [x, y, bbox_width, bbox_height],
                            "area": bbox_width * bbox_height,
                            "iscrowd": 0,
                            "segmentation": []
                        })
                        annotation_id += 1
        
        image_id += 1
    
    with open(output_json, 'w') as f:
        json.dump(coco_data, f, indent=2)
    
    print(f"COCO format JSON created at: {output_json}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Train Mask R-CNN model")
    parser.add_argument("--train-json", type=str, required=True, help="Training COCO JSON")
    parser.add_argument("--train-images", type=str, required=True, help="Training images directory")
    parser.add_argument("--val-json", type=str, required=True, help="Validation COCO JSON")
    parser.add_argument("--val-images", type=str, required=True, help="Validation images directory")
    parser.add_argument("--epochs", type=int, default=100, help="Number of epochs")
    parser.add_argument("--batch-size", type=int, default=16, help="Batch size")
    parser.add_argument("--lr", type=float, default=0.01, help="Learning rate")
    parser.add_argument("--device", type=str, default=None,
                       help="Device (auto-detect if not specified: 'cpu' or 'cuda')")
    
    args = parser.parse_args()
    
    register_dataset("cracks_train", args.train_json, args.train_images)
    register_dataset("cracks_val", args.val_json, args.val_images)
    
    train_mask_rcnn(
        train_dataset_name="cracks_train",
        val_dataset_name="cracks_val",
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.lr,
        device=args.device
    )

