"""Mask R-CNN model wrapper for inference."""
from pathlib import Path
import cv2
import numpy as np
from typing import List, Dict, Tuple, Optional
from app.utils.config_loader import config
import logging

logger = logging.getLogger(__name__)

# Try to import detectron2, but handle gracefully if not available
try:
    import torch
    from detectron2 import model_zoo
    from detectron2.engine import DefaultPredictor
    from detectron2.config import get_cfg
    DETECTRON2_AVAILABLE = True
except ImportError:
    DETECTRON2_AVAILABLE = False
    logger.warning("Detectron2 not available. Mask R-CNN detection will not work.")


class MaskRCNNCrackDetector:
    """Mask R-CNN model for crack detection and segmentation."""
    
    def __init__(self, weights_path: Optional[str] = None):
        """Initialize Mask R-CNN model.
        
        Args:
            weights_path: Path to model weights file
        """
        if not DETECTRON2_AVAILABLE:
            raise ImportError("Detectron2 is not installed. Please install it with: pip install 'git+https://github.com/facebookresearch/detectron2.git'")
        
        weights_path = weights_path or config.get("models.mask_rcnn.weights_path", "weights/mask_rcnn_cracks.pth")
        
        cfg = get_cfg()
        cfg.merge_from_file(model_zoo.get_config_file("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml"))
        cfg.MODEL.ROI_HEADS.NUM_CLASSES = 2  # crack and pothole classes
        cfg.MODEL.WEIGHTS = str(weights_path) if Path(weights_path).exists() else model_zoo.get_checkpoint_url("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml")
        cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = config.get("models.mask_rcnn.confidence_threshold", 0.5)
        cfg.MODEL.DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
        
        self.predictor = DefaultPredictor(cfg)
        self.confidence_threshold = config.get("models.mask_rcnn.confidence_threshold", 0.5)
    
    def detect(self, image: np.ndarray) -> Tuple[List[Dict], np.ndarray]:
        """Detect cracks with masks in image.
        
        Args:
            image: Input image (BGR format)
        
        Returns:
            Tuple of (detections list, combined mask)
        """
        outputs = self.predictor(image)
        
        instances = outputs["instances"]
        detections = []
        masks_list = []
        
        # Get predictions
        boxes = instances.pred_boxes.tensor.cpu().numpy()
        scores = instances.scores.cpu().numpy()
        classes = instances.pred_classes.cpu().numpy()
        masks = instances.pred_masks.cpu().numpy() if instances.has("pred_masks") else None
        
        for i in range(len(boxes)):
            if scores[i] >= self.confidence_threshold:
                box = boxes[i].tolist()  # [x1, y1, x2, y2]
                mask = masks[i] if masks is not None else None
                
                if mask is not None:
                    # Convert mask to uint8
                    mask_uint8 = (mask * 255).astype(np.uint8)
                    masks_list.append(mask_uint8)
                
                # Map class ID to class name
                class_names_map = {0: "crack", 1: "pothole"}
                class_name = class_names_map.get(int(classes[i]), f"class_{int(classes[i])}")
                
                detections.append({
                    "bbox": box,
                    "confidence": float(scores[i]),
                    "class_id": int(classes[i]),
                    "class_name": class_name,
                    "has_mask": mask is not None
                })
        
        # Combine all masks
        combined_mask = np.zeros_like(image[:, :, 0], dtype=np.uint8)
        if masks_list:
            for mask in masks_list:
                combined_mask = np.maximum(combined_mask, mask)
        
        return detections, combined_mask

