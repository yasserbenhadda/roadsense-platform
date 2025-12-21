"""Utilities for dataset preparation and annotation."""
import os
import shutil
import random
from pathlib import Path
from typing import List, Tuple
import cv2
import numpy as np
from sklearn.model_selection import train_test_split


def split_dataset(
    source_dir: str,
    train_dir: str,
    val_dir: str,
    test_dir: str,
    train_ratio: float = 0.7,
    val_ratio: float = 0.2,
    test_ratio: float = 0.1,
    seed: int = 42
) -> None:
    """Split dataset into train/val/test sets.
    
    Args:
        source_dir: Source directory with images
        train_dir: Training set directory
        val_dir: Validation set directory
        test_dir: Test set directory
        train_ratio: Ratio for training set
        val_ratio: Ratio for validation set
        test_ratio: Ratio for test set
        seed: Random seed
    """
    assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-6, "Ratios must sum to 1.0"
    
    source_path = Path(source_dir)
    train_path = Path(train_dir)
    val_path = Path(val_dir)
    test_path = Path(test_dir)
    
    # Create directories
    for path in [train_path, val_path, test_path]:
        path.mkdir(parents=True, exist_ok=True)
    
    # Get all image files
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp'}
    images = [f for f in source_path.iterdir() 
              if f.suffix.lower() in image_extensions]
    
    # Split dataset
    random.seed(seed)
    random.shuffle(images)
    
    n_total = len(images)
    n_train = int(n_total * train_ratio)
    n_val = int(n_total * val_ratio)
    
    train_images = images[:n_train]
    val_images = images[n_train:n_train + n_val]
    test_images = images[n_train + n_val:]
    
    # Copy files
    for img in train_images:
        shutil.copy2(img, train_path / img.name)
        # Copy annotation if exists
        ann_file = img.with_suffix('.txt')
        if ann_file.exists():
            shutil.copy2(ann_file, train_path / ann_file.name)
    
    for img in val_images:
        shutil.copy2(img, val_path / img.name)
        ann_file = img.with_suffix('.txt')
        if ann_file.exists():
            shutil.copy2(ann_file, val_path / ann_file.name)
    
    for img in test_images:
        shutil.copy2(img, test_path / img.name)
        ann_file = img.with_suffix('.txt')
        if ann_file.exists():
            shutil.copy2(ann_file, test_path / ann_file.name)
    
    print(f"Dataset split completed:")
    print(f"  Train: {len(train_images)} images")
    print(f"  Val: {len(val_images)} images")
    print(f"  Test: {len(test_images)} images")


def convert_labelme_to_yolo(labelme_json: str, output_txt: str, img_width: int, img_height: int) -> None:
    """Convert LabelMe JSON annotation to YOLO format.
    
    Args:
        labelme_json: Path to LabelMe JSON file
        output_txt: Path to output YOLO format file
        img_width: Image width
        img_height: Image height
    """
    import json
    
    with open(labelme_json, 'r') as f:
        data = json.load(f)
    
    yolo_annotations = []
    for shape in data.get('shapes', []):
        if shape['shape_type'] == 'rectangle':
            # LabelMe format: [[x1, y1], [x2, y2]]
            points = shape['points']
            x1, y1 = points[0]
            x2, y2 = points[1]
            
            # Convert to YOLO format: class_id center_x center_y width height (normalized)
            center_x = ((x1 + x2) / 2) / img_width
            center_y = ((y1 + y2) / 2) / img_height
            width = abs(x2 - x1) / img_width
            height = abs(y2 - y1) / img_height
            
            # Class ID (0 for crack)
            class_id = 0
            
            yolo_annotations.append(f"{class_id} {center_x} {center_y} {width} {height}")
    
    with open(output_txt, 'w') as f:
        f.write('\n'.join(yolo_annotations))


def augment_image(image: np.ndarray, bboxes: List[List[float]] = None) -> Tuple[np.ndarray, List[List[float]]]:
    """Apply data augmentation to image and bounding boxes.
    
    Args:
        image: Input image
        bboxes: List of bounding boxes in YOLO format [class, x, y, w, h]
    
    Returns:
        Augmented image and transformed bounding boxes
    """
    # Random horizontal flip
    if random.random() > 0.5:
        image = cv2.flip(image, 1)
        if bboxes:
            for bbox in bboxes:
                bbox[1] = 1.0 - bbox[1]  # Flip center_x
    
    # Random brightness adjustment
    if random.random() > 0.5:
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        hsv[:, :, 2] = cv2.multiply(hsv[:, :, 2], random.uniform(0.7, 1.3))
        image = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    
    # Random rotation (small angles)
    if random.random() > 0.5:
        angle = random.uniform(-10, 10)
        h, w = image.shape[:2]
        M = cv2.getRotationMatrix2D((w/2, h/2), angle, 1.0)
        image = cv2.warpAffine(image, M, (w, h))
    
    return image, bboxes if bboxes else []

