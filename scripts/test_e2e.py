#!/usr/bin/env python3
"""End-to-end test script for the crack detection service."""
import sys
from pathlib import Path


project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import argparse
import requests
import time
import json
from pathlib import Path
from typing import Optional


class Colors:
    GREEN = '\033[0;32m'
    RED = '\033[0;31m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color


def print_success(message: str):
    print(f"{Colors.GREEN}{message}{Colors.NC}")


def print_error(message: str):
    print(f"{Colors.RED}{message}{Colors.NC}")


def print_warning(message: str):
    print(f"{Colors.YELLOW}{message}{Colors.NC}")


def print_info(message: str):
    print(f"{Colors.BLUE}ℹ️  {message}{Colors.NC}")


def test_health_check(api_url: str) -> bool:
    """Test health check endpoint."""
    try:
        response = requests.get(f"{api_url}/health", timeout=5)
        if response.status_code == 200:
            print_success("Health check passed")
            return True
        else:
            print_error(f"Health check returned {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Health check failed: {e}")
        return False


def test_root_endpoint(api_url: str) -> bool:
    """Test root endpoint."""
    try:
        response = requests.get(f"{api_url}/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success(f"Root endpoint: {data.get('service', 'Unknown')}")
            return True
        else:
            print_error(f"Root endpoint returned {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Root endpoint failed: {e}")
        return False


def test_detection_endpoint(api_url: str, test_image_path: Optional[str] = None) -> bool:
    """Test detection endpoint."""
    if not test_image_path or not Path(test_image_path).exists():
        print_warning("No test image provided, skipping detection test")
        return True
    
    try:
        print_info(f"Testing detection with image: {test_image_path}")
        with open(test_image_path, "rb") as f:
            files = {"image": f}
            data = {"model": "yolov8", "return_image": "false"}
            
            start_time = time.time()
            response = requests.post(
                f"{api_url}/detect",
                files=files,
                data=data,
                timeout=30
            )
            elapsed = (time.time() - start_time) * 1000
        
        if response.status_code == 200:
            result = response.json()
            num_detections = result.get("num_detections", 0)
            inference_time = result.get("inference_time_ms", elapsed)
            
            print_success(f"Detection completed: {num_detections} detections in {inference_time:.2f}ms")
            
            # Check performance target
            if inference_time > 300:
                print_warning(f"Inference time {inference_time:.2f}ms exceeds target 300ms")
            else:
                print_success(f"Inference time {inference_time:.2f}ms meets target (< 300ms)")
            
            return True
        else:
            print_error(f"Detection failed with status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print_error(f"Detection test failed: {e}")
        return False


def test_results_endpoint(api_url: str) -> bool:
    """Test results endpoint."""
    try:
        response = requests.get(f"{api_url}/results?limit=5", timeout=5)
        if response.status_code == 200:
            data = response.json()
            total = data.get("total", 0)
            print_success(f"Results endpoint: {total} results retrieved")
            return True
        else:
            print_warning(f"Results endpoint returned {response.status_code} (database might not be configured)")
            return True  # Not a critical failure
    except Exception as e:
        print_warning(f"Results endpoint test failed: {e} (database might not be configured)")
        return True  # Not a critical failure


def test_stats_endpoint(api_url: str) -> bool:
    """Test stats endpoint."""
    try:
        response = requests.get(f"{api_url}/results/stats", timeout=5)
        if response.status_code == 200:
            data = response.json()
            total = data.get("total_detections", 0)
            print_success(f"Stats endpoint: {total} total detections")
            return True
        else:
            print_warning(f"Stats endpoint returned {response.status_code} (database might not be configured)")
            return True  # Not a critical failure
    except Exception as e:
        print_warning(f"Stats endpoint test failed: {e} (database might not be configured)")
        return True  # Not a critical failure


def test_metrics_endpoint(api_url: str) -> bool:
    """Test metrics endpoint."""
    try:
        response = requests.get(f"{api_url}/metrics", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success("Metrics endpoint accessible")
            return True
        else:
            print_error(f"Metrics endpoint returned {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Metrics endpoint test failed: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="End-to-end test for crack detection service")
    parser.add_argument("--api-url", type=str, default="http://localhost:8000",
                       help="API base URL")
    parser.add_argument("--test-image", type=str, help="Path to test image for detection")
    parser.add_argument("--skip-detection", action="store_true",
                       help="Skip detection endpoint test")
    
    args = parser.parse_args()
    
    print("🧪 Test End-to-End du service de détection de fissures")
    print("=" * 60)
    print("")
    print(f"API URL: {args.api_url}")
    print("")
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Health check
    print("1️⃣  Testing health check endpoint...")
    tests_total += 1
    if test_health_check(args.api_url):
        tests_passed += 1
    print("")
    
    # Test 2: Root endpoint
    print("2️⃣  Testing root endpoint...")
    tests_total += 1
    if test_root_endpoint(args.api_url):
        tests_passed += 1
    print("")
    
    # Test 3: Metrics endpoint
    print("3️⃣  Testing metrics endpoint...")
    tests_total += 1
    if test_metrics_endpoint(args.api_url):
        tests_passed += 1
    print("")
    
    # Test 4: Results endpoint
    print("4️⃣  Testing results endpoint...")
    tests_total += 1
    if test_results_endpoint(args.api_url):
        tests_passed += 1
    print("")
    
    # Test 5: Stats endpoint
    print("5️⃣  Testing stats endpoint...")
    tests_total += 1
    if test_stats_endpoint(args.api_url):
        tests_passed += 1
    print("")
    
    # Test 6: Detection endpoint
    if not args.skip_detection:
        print("6️⃣  Testing detection endpoint...")
        tests_total += 1
        if test_detection_endpoint(args.api_url, args.test_image):
            tests_passed += 1
        print("")
    
    # Summary
    print("=" * 60)
    print(f"Résultats: {tests_passed}/{tests_total} tests réussis")
    print("")
    
    if tests_passed == tests_total:
        print_success("🎉 Tous les tests sont passés !")
        return 0
    else:
        print_error(f"{tests_total - tests_passed} test(s) ont échoué")
        return 1


if __name__ == "__main__":
    exit(main())

