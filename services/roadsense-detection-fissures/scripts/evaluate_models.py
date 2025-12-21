#!/usr/bin/env python3
"""Script to evaluate trained models."""
import sys
from pathlib import Path


project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import argparse
import time
import cv2
import numpy as np
from app.models.yolov8_model import YOLOv8CrackDetector
from app.models.mask_rcnn_model import MaskRCNNCrackDetector


def evaluate_model(detector, test_images_dir: str):
    """Evaluate model on test images.
    
    Args:
        detector: Model detector instance
        test_images_dir: Directory containing test images
    
    Returns:
        Dictionary with evaluation metrics
    """
    test_path = Path(test_images_dir)
    image_files = list(test_path.glob("*.jpg")) + list(test_path.glob("*.png"))
    
    inference_times = []
    num_detections = []
    
    for img_file in image_files:
        image = cv2.imread(str(img_file))
        if image is None:
            continue
        
        start_time = time.time()
        if isinstance(detector, YOLOv8CrackDetector):
            detections, _ = detector.detect_with_masks(image)
        else:
            detections, _ = detector.detect(image)
        inference_time = (time.time() - start_time) * 1000  # ms
        
        inference_times.append(inference_time)
        num_detections.append(len(detections))
    
    return {
        "avg_inference_time_ms": np.mean(inference_times),
        "std_inference_time_ms": np.std(inference_times),
        "min_inference_time_ms": np.min(inference_times),
        "max_inference_time_ms": np.max(inference_times),
        "avg_detections": np.mean(num_detections),
        "total_images": len(image_files)
    }


def main():
    parser = argparse.ArgumentParser(description="Evaluate trained models")
    parser.add_argument("--test-dir", type=str, required=True, help="Test images directory")
    parser.add_argument("--yolov8-weights", type=str, help="YOLOv8 weights path")
    parser.add_argument("--mask-rcnn-weights", type=str, help="Mask R-CNN weights path")
    
    args = parser.parse_args()
    
    results = {}
    
    # Evaluate YOLOv8
    if args.yolov8_weights and Path(args.yolov8_weights).exists():
        print("Evaluating YOLOv8...")
        detector = YOLOv8CrackDetector(weights_path=args.yolov8_weights)
        results["yolov8"] = evaluate_model(detector, args.test_dir)
        print(f"YOLOv8 Results: {results['yolov8']}")
    
    # Evaluate Mask R-CNN
    if args.mask_rcnn_weights and Path(args.mask_rcnn_weights).exists():
        print("Evaluating Mask R-CNN...")
        detector = MaskRCNNCrackDetector(weights_path=args.mask_rcnn_weights)
        results["mask_rcnn"] = evaluate_model(detector, args.test_dir)
        print(f"Mask R-CNN Results: {results['mask_rcnn']}")
    
    # Print summary
    print("\n=== Evaluation Summary ===")
    for model_name, metrics in results.items():
        print(f"\n{model_name.upper()}:")
        print(f"  Average inference time: {metrics['avg_inference_time_ms']:.2f} ms")
        print(f"  Std inference time: {metrics['std_inference_time_ms']:.2f} ms")
        print(f"  Average detections per image: {metrics['avg_detections']:.2f}")
        print(f"  Total images tested: {metrics['total_images']}")


if __name__ == "__main__":
    main()

