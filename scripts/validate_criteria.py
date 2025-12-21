#!/usr/bin/env python3
"""Script to validate project criteria."""
import sys
from pathlib import Path


project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import argparse
import json
import requests
from pathlib import Path
import time


def validate_map50(map50_value: float, target: float = 0.85) -> tuple[bool, str]:
    """Validate mAP50 criterion.
    
    Args:
        map50_value: mAP50 value to validate
        target: Target mAP50 (default: 0.85)
    
    Returns:
        Tuple of (is_valid, message)
    """
    if map50_value >= target:
        return True, f"mAP50 = {map50_value:.2%} >= {target:.0%} (target)"
    else:
        return False, f"mAP50 = {map50_value:.2%} < {target:.0%} (target)"


def validate_inference_time(inference_time_ms: float, target: float = 300.0) -> tuple[bool, str]:
    """Validate inference time criterion.
    
    Args:
        inference_time_ms: Inference time in milliseconds
        target: Target time in ms (default: 300)
    
    Returns:
        Tuple of (is_valid, message)
    """
    if inference_time_ms <= target:
        return True, f"Inference time = {inference_time_ms:.2f}ms <= {target}ms (target)"
    else:
        return False, f"Inference time = {inference_time_ms:.2f}ms > {target}ms (target)"


def test_api_response_time(api_url: str = "http://localhost:8000", test_image_path: str = None) -> float:
    """Test API response time.
    
    Args:
        api_url: API base URL
        test_image_path: Path to test image (optional)
    
    Returns:
        Average inference time in milliseconds
    """
    if test_image_path and Path(test_image_path).exists():
        # Test with actual image
        times = []
        for _ in range(5):  # Test 5 times
            start = time.time()
            try:
                with open(test_image_path, "rb") as f:
                    response = requests.post(
                        f"{api_url}/detect",
                        files={"image": f},
                        data={"model": "yolov8"},
                        timeout=10
                    )
                elapsed = (time.time() - start) * 1000
                if response.status_code == 200:
                    result = response.json()
                    times.append(result.get("inference_time_ms", elapsed))
            except Exception as e:
                print(f"Error testing API: {e}")
                return 0.0
        
        return sum(times) / len(times) if times else 0.0
    else:
        # Test health endpoint
        try:
            start = time.time()
            response = requests.get(f"{api_url}/health", timeout=5)
            elapsed = (time.time() - start) * 1000
            return elapsed if response.status_code == 200 else 0.0
        except:
            return 0.0


def validate_from_metrics_file(metrics_file: str) -> dict:
    """Validate criteria from metrics JSON file.
    
    Args:
        metrics_file: Path to metrics JSON file
    
    Returns:
        Validation results dictionary
    """
    with open(metrics_file, 'r') as f:
        metrics = json.load(f)
    
    results = {
        "map50_validation": {},
        "inference_time_validation": {},
        "overall": True
    }
    
    for model_name, model_metrics in metrics.items():
        map50 = model_metrics.get("map50", 0)
        inference_time = model_metrics.get("avg_inference_time_ms", 0)
        
        # Validate mAP50
        map50_valid, map50_msg = validate_map50(map50)
        results["map50_validation"][model_name] = {
            "valid": map50_valid,
            "message": map50_msg,
            "value": map50
        }
        
        # Validate inference time
        time_valid, time_msg = validate_inference_time(inference_time)
        results["inference_time_validation"][model_name] = {
            "valid": time_valid,
            "message": time_msg,
            "value": inference_time
        }
        
        if not map50_valid or not time_valid:
            results["overall"] = False
    
    return results


def main():
    parser = argparse.ArgumentParser(description="Validate project criteria")
    parser.add_argument("--metrics", type=str, help="Path to metrics JSON file")
    parser.add_argument("--api-url", type=str, default="http://localhost:8000",
                       help="API URL for testing")
    parser.add_argument("--test-image", type=str, help="Path to test image for API testing")
    
    args = parser.parse_args()
    
    print("Validation des critères du projet")
    print("=" * 50)
    print("")
    
    all_valid = True
    
    # Validate from metrics file if provided
    if args.metrics and Path(args.metrics).exists():
        print("Validation depuis le fichier de métriques...")
        results = validate_from_metrics_file(args.metrics)
        
        print("\n📈 Validation mAP50:")
        for model, validation in results["map50_validation"].items():
            print(f"  {model.upper()}: {validation['message']}")
            if not validation["valid"]:
                all_valid = False
        
        print("\n⏱️  Validation temps d'inférence:")
        for model, validation in results["inference_time_validation"].items():
            print(f"  {model.upper()}: {validation['message']}")
            if not validation["valid"]:
                all_valid = False
    
    # Test API if available
    print("\n🌐 Test de l'API...")
    try:
        response = requests.get(f"{args.api_url}/health", timeout=5)
        if response.status_code == 200:
            print("  API accessible")
            
            # Test inference time
            avg_time = test_api_response_time(args.api_url, args.test_image)
            if avg_time > 0:
                time_valid, time_msg = validate_inference_time(avg_time)
                print(f"  {time_msg}")
                if not time_valid:
                    all_valid = False
        else:
            print("  API non accessible")
            all_valid = False
    except Exception as e:
        print(f"  Erreur de connexion à l'API: {e}")
        all_valid = False
    
    # Final result
    print("\n" + "=" * 50)
    if all_valid:
        print("Tous les critères sont validés !")
        return 0
    else:
        print("Certains critères ne sont pas validés")
        return 1


if __name__ == "__main__":
    exit(main())

