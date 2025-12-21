#!/usr/bin/env python3
"""Script to export trained models to ONNX format."""
import sys
from pathlib import Path


project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import argparse
from pathlib import Path
import torch
from ultralytics import YOLO
from app.utils.config_loader import config


def export_yolov8_to_onnx(weights_path: str, output_path: str = None, imgsz: int = 640):
    """Export YOLOv8 model to ONNX format.
    
    Args:
        weights_path: Path to YOLOv8 weights file (.pt)
        output_path: Output ONNX file path (optional)
        imgsz: Image size for export
    
    Returns:
        Path to exported ONNX file
    """
    if not Path(weights_path).exists():
        raise FileNotFoundError(f"Model weights not found: {weights_path}")
    
    model = YOLO(weights_path)
    
    # Export to ONNX
    output_path = output_path or str(Path(weights_path).with_suffix('.onnx'))
    
    print(f"Exporting YOLOv8 model to ONNX...")
    print(f"   Input: {weights_path}")
    print(f"   Output: {output_path}")
    
    # Export with optimizations
    success = model.export(
        format='onnx',
        imgsz=imgsz,
        optimize=True,
        simplify=True,
        opset=12  # ONNX opset version
    )
    
    if success:
        # Find the exported file
        exported_file = Path(weights_path).parent / f"{Path(weights_path).stem}.onnx"
        if exported_file.exists():
            # Move to output path if different
            if str(exported_file) != output_path:
                import shutil
                shutil.move(str(exported_file), output_path)
            print(f"Model exported successfully to: {output_path}")
            return output_path
        else:
            raise FileNotFoundError("ONNX export completed but file not found")
    else:
        raise RuntimeError("ONNX export failed")


def export_mask_rcnn_to_onnx(weights_path: str, output_path: str = None):
    """Export Mask R-CNN model to ONNX format.
    
    Args:
        weights_path: Path to Mask R-CNN weights file (.pth)
        output_path: Output ONNX file path (optional)
    
    Returns:
        Path to exported ONNX file
    """
    try:
        import torch
        from detectron2 import model_zoo
        from detectron2.config import get_cfg
        from detectron2.engine import DefaultPredictor
    except ImportError:
        raise ImportError("Detectron2 not installed. Cannot export Mask R-CNN to ONNX.")
    
    if not Path(weights_path).exists():
        raise FileNotFoundError(f"Model weights not found: {weights_path}")
    
    cfg = get_cfg()
    cfg.merge_from_file(model_zoo.get_config_file("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml"))
    cfg.MODEL.ROI_HEADS.NUM_CLASSES = 2
    cfg.MODEL.WEIGHTS = str(weights_path)
    cfg.MODEL.DEVICE = "cpu"  # ONNX export requires CPU
    
    # Create a dummy input
    dummy_input = torch.randn(1, 3, 800, 800)
    
    # Load model
    model = DefaultPredictor(cfg).model
    model.eval()
    
    output_path = output_path or str(Path(weights_path).with_suffix('.onnx'))
    
    print(f"Exporting Mask R-CNN model to ONNX...")
    print(f"   Input: {weights_path}")
    print(f"   Output: {output_path}")
    
    # Export to ONNX
    torch.onnx.export(
        model,
        dummy_input,
        output_path,
        input_names=['input'],
        output_names=['output'],
        dynamic_axes={'input': {0: 'batch_size'}, 'output': {0: 'batch_size'}},
        opset_version=12
    )
    
    if Path(output_path).exists():
        print(f"Model exported successfully to: {output_path}")
        return output_path
    else:
        raise FileNotFoundError("ONNX export failed")


def main():
    parser = argparse.ArgumentParser(description="Export trained models to ONNX format")
    parser.add_argument("--model", type=str, choices=["yolov8", "mask_rcnn"], required=True,
                       help="Model type to export")
    parser.add_argument("--weights", type=str, required=True,
                       help="Path to model weights file")
    parser.add_argument("--output", type=str, default=None,
                       help="Output ONNX file path (optional)")
    parser.add_argument("--imgsz", type=int, default=640,
                       help="Image size for YOLOv8 export")
    
    args = parser.parse_args()
    
    try:
        if args.model == "yolov8":
            output_path = export_yolov8_to_onnx(args.weights, args.output, args.imgsz)
        elif args.model == "mask_rcnn":
            output_path = export_mask_rcnn_to_onnx(args.weights, args.output)
        
        print(f"\nExport completed successfully!")
        print(f"   ONNX model: {output_path}")
        print(f"\nYou can now use this ONNX model for inference in other frameworks.")
        
    except Exception as e:
        print(f"Export failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())

