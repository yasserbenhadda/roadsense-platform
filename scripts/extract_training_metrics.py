#!/usr/bin/env python3
"""Script to extract metrics from YOLOv8 training results."""
import sys
from pathlib import Path


project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import argparse
import json
import yaml
from pathlib import Path
import re


def extract_yolov8_metrics(runs_dir: str = "runs/detect") -> dict:
    """Extract metrics from YOLOv8 training results.
    
    Args:
        runs_dir: Directory containing training runs
    
    Returns:
        Dictionary with metrics
    """
    runs_path = Path(runs_dir)
    if not runs_path.exists():
        return {}
    
    # Find the most recent training run
    training_dirs = sorted(runs_path.glob("yolov8_cracks*"), key=lambda x: x.stat().st_mtime, reverse=True)
    
    if not training_dirs:
        return {}
    
    latest_run = training_dirs[0]
    results_file = latest_run / "results.csv"
    
    if not results_file.exists():
        return {}
    
    # Read results.csv and extract final metrics
    metrics = {
        "map50": 0.0,
        "map50_95": 0.0,
        "avg_inference_time_ms": 0.0
    }
    
    try:
        import pandas as pd
        df = pd.read_csv(results_file)
        
        # Get the last row (final epoch)
        if len(df) > 0:
            last_row = df.iloc[-1]
            
            # Extract mAP50 and mAP50-95
            if "metrics/mAP50(B)" in df.columns:
                metrics["map50"] = float(last_row["metrics/mAP50(B)"])
            if "metrics/mAP50-95(B)" in df.columns:
                metrics["map50_95"] = float(last_row["metrics/mAP50-95(B)"])
            
            # Calculate average inference time (if available)
            if "time" in df.columns:
                metrics["avg_inference_time_ms"] = float(df["time"].mean() * 1000)  # Convert to ms
    
    except Exception as e:
        print(f"Error reading results.csv: {e}")
    
    return metrics


def extract_mask_rcnn_metrics(output_dir: str = "output/mask_rcnn") -> dict:
    """Extract metrics from Mask R-CNN training results.
    
    Args:
        output_dir: Directory containing training output
    
    Returns:
        Dictionary with metrics
    """
    output_path = Path(output_dir)
    if not output_path.exists():
        return {}
    
    # Look for metrics in log files or evaluation results
    metrics = {
        "map50": 0.0,
        "map50_95": 0.0,
        "avg_inference_time_ms": 0.0
    }
    
    # Try to find metrics in log files
    log_files = list(output_path.glob("*.log")) + list(output_path.glob("metrics.json"))
    
    for log_file in log_files:
        try:
            if log_file.suffix == ".json":
                with open(log_file, 'r') as f:
                    data = json.load(f)
                    if "map50" in data:
                        metrics["map50"] = float(data["map50"])
                    if "map50_95" in data:
                        metrics["map50_95"] = float(data["map50_95"])
        except:
            pass
    
    return metrics


def main():
    parser = argparse.ArgumentParser(description="Extract training metrics")
    parser.add_argument("--output", type=str, default="metrics.json",
                       help="Output JSON file path")
    parser.add_argument("--runs-dir", type=str, default="runs/detect",
                       help="YOLOv8 runs directory")
    parser.add_argument("--mask-rcnn-dir", type=str, default="output/mask_rcnn",
                       help="Mask R-CNN output directory")
    
    args = parser.parse_args()
    
    print("Extraction des métriques d'entraînement...")
    print("")
    
    metrics = {}
    
    # Extract YOLOv8 metrics
    print("Extraction métriques YOLOv8...")
    yolov8_metrics = extract_yolov8_metrics(args.runs_dir)
    if yolov8_metrics:
        metrics["yolov8"] = yolov8_metrics
        print(f"  mAP50: {yolov8_metrics.get('map50', 0):.2%}")
        print(f"  mAP50-95: {yolov8_metrics.get('map50_95', 0):.2%}")
    else:
        print("  Aucune métrique YOLOv8 trouvée")
        metrics["yolov8"] = {
            "map50": 0.0,
            "map50_95": 0.0,
            "avg_inference_time_ms": 0.0
        }
    
    print("")
    
    # Extract Mask R-CNN metrics
    print("Extraction métriques Mask R-CNN...")
    mask_rcnn_metrics = extract_mask_rcnn_metrics(args.mask_rcnn_dir)
    if mask_rcnn_metrics:
        metrics["mask_rcnn"] = mask_rcnn_metrics
        print(f"  mAP50: {mask_rcnn_metrics.get('map50', 0):.2%}")
        print(f"  mAP50-95: {mask_rcnn_metrics.get('map50_95', 0):.2%}")
    else:
        print("  Aucune métrique Mask R-CNN trouvée")
        metrics["mask_rcnn"] = {
            "map50": 0.0,
            "map50_95": 0.0,
            "avg_inference_time_ms": 0.0
        }
    
    # Save to file
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(metrics, f, indent=2)
    
    print("")
    print(f"Métriques sauvegardées dans: {output_path}")
    print("")
    print("Utilisez ces métriques pour:")
    print("   - Générer le rapport: python scripts/generate_report.py --metrics metrics.json")
    print("   - Valider les critères: python scripts/validate_criteria.py --metrics metrics.json")


if __name__ == "__main__":
    main()

