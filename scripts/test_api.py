#!/usr/bin/env python3
"""Script to test the API endpoints."""
import requests
import json
from pathlib import Path


def test_health_check(base_url: str = "http://localhost:8000"):
    """Test health check endpoint."""
    print("Testing health check...")
    response = requests.get(f"{base_url}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")


def test_detect(base_url: str = "http://localhost:8000", image_path: str = None):
    """Test detection endpoint."""
    if image_path is None:
        print("No image provided for detection test")
        return
    
    if not Path(image_path).exists():
        print(f"Image not found: {image_path}")
        return
    
    print(f"Testing detection with image: {image_path}")
    
    with open(image_path, "rb") as f:
        files = {"image": f}
        data = {
            "model": "yolov8",
            "return_image": "false",
            "save_to_minio": "false"
        }
        response = requests.post(f"{base_url}/detect", files=files, data=data)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Model: {result['model']}")
        print(f"Number of detections: {result['num_detections']}")
        print(f"Inference time: {result['inference_time_ms']} ms")
        print(f"Image size: {result['image_size']}")
        if result['detections']:
            print("Detections:")
            for i, det in enumerate(result['detections'], 1):
                print(f"  {i}. Confidence: {det['confidence']:.2f}, BBox: {det['bbox']}")
    else:
        print(f"Error: {response.text}")
    print()


def test_metrics(base_url: str = "http://localhost:8000"):
    """Test metrics endpoint."""
    print("Testing metrics endpoint...")
    response = requests.get(f"{base_url}/metrics")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test API endpoints")
    parser.add_argument("--url", type=str, default="http://localhost:8000", help="API base URL")
    parser.add_argument("--image", type=str, help="Path to test image")
    
    args = parser.parse_args()
    
    print("=" * 50)
    print("API Testing")
    print("=" * 50)
    print()
    
    test_health_check(args.url)
    test_metrics(args.url)
    
    if args.image:
        test_detect(args.url, args.image)
    else:
        print("Skipping detection test (no image provided)")
        print("Use --image <path> to test detection endpoint")

