"""YOLOv8 model wrapper for inference."""
from pathlib import Path
import cv2
import numpy as np
from typing import List, Dict, Tuple, Optional
from app.utils.config_loader import config
import logging

logger = logging.getLogger(__name__)

# Try to import ultralytics, but handle gracefully if not available
try:
    from ultralytics import YOLO
    ULTRALYTICS_AVAILABLE = True
except ImportError:
    ULTRALYTICS_AVAILABLE = False
    logger.warning("Ultralytics not available. YOLOv8 detection will not work.")


class YOLOv8CrackDetector:
    """YOLOv8 model for crack detection."""
    
    def __init__(self, weights_path: Optional[str] = None):
        """Initialize YOLOv8 model.
        
        Args:
            weights_path: Path to model weights file
        """
        if not ULTRALYTICS_AVAILABLE:
            raise ImportError("Ultralytics is not installed. Please install it with: pip install ultralytics")
        
        weights_path = weights_path or config.get("models.yolov8.weights_path", "weights/yolov8_cracks.pt")
        
        if not Path(weights_path).exists():
            logger.warning(f"Model weights not found at {weights_path}. Using pretrained model.")
            weights_path = "yolov8n.pt"
        
        self.model = YOLO(weights_path)
        self.confidence_threshold = config.get("models.yolov8.confidence_threshold", 0.25)
        self.iou_threshold = config.get("models.yolov8.iou_threshold", 0.45)
        self.input_size = config.get("models.yolov8.input_size", 640)
    
    def detect(self, image: np.ndarray) -> List[Dict]:
        """Detect cracks in image.
        
        Args:
            image: Input image (BGR format)
        
        Returns:
            List of detections with bounding boxes, confidence scores, and class IDs
        """
        results = self.model(
            image,
            conf=self.confidence_threshold,
            iou=self.iou_threshold,
            imgsz=self.input_size
        )
        
        detections = []
        for result in results:
            boxes = result.boxes
            for i in range(len(boxes)):
                box = boxes.xyxy[i].cpu().numpy()
                conf = float(boxes.conf[i].cpu().numpy())
                cls = int(boxes.cls[i].cpu().numpy())
                
                # Map class ID to class name
                class_names_map = {0: "crack", 1: "pothole"}
                class_name = class_names_map.get(cls, f"class_{cls}")
                
                detections.append({
                    "bbox": box.tolist(),  # [x1, y1, x2, y2]
                    "confidence": conf,
                    "class_id": cls,
                    "class_name": class_name
                })
        
        return detections
    
    def detect_with_masks(self, image: np.ndarray) -> Tuple[List[Dict], Optional[np.ndarray]]:
        """Detect cracks with segmentation masks (if model supports it).
        
        Args:
            image: Input image (BGR format)
        
        Returns:
            Tuple of (detections list, combined mask)
        """
        results = self.model(image, conf=self.confidence_threshold, iou=self.iou_threshold)
        
        detections = []
        masks_list = []
        
        for result in results:
            boxes = result.boxes
            if result.masks is not None:
                masks = result.masks.data.cpu().numpy()
                
                for i in range(len(boxes)):
                    box = boxes.xyxy[i].cpu().numpy()
                    conf = float(boxes.conf[i].cpu().numpy())
                    cls = int(boxes.cls[i].cpu().numpy())
                    
                    mask = masks[i] if i < len(masks) else None
                    if mask is not None:
                        # Resize mask to original image size
                        h, w = image.shape[:2]
                        mask_resized = cv2.resize(mask, (w, h))
                        masks_list.append(mask_resized)
                    
                    # Map class ID to class name
                    class_names_map = {0: "crack", 1: "pothole"}
                    class_name = class_names_map.get(cls, f"class_{cls}")
                    
                    detections.append({
                        "bbox": box.tolist(),
                        "confidence": conf,
                        "class_id": cls,
                        "class_name": class_name,
                        "has_mask": mask is not None
                    })
        
        # Combine all masks
        combined_mask = None
        if masks_list:
            combined_mask = np.zeros_like(image[:, :, 0], dtype=np.uint8)
            for mask in masks_list:
                combined_mask = np.maximum(combined_mask, (mask > 0.5).astype(np.uint8) * 255)
        
        return detections, combined_mask

