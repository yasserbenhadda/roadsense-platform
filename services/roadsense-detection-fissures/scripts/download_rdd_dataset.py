#!/usr/bin/env python3
"""Script to download and prepare Road Damage Dataset (RDD) for training."""
import sys
from pathlib import Path


project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import os
import argparse
import urllib.request
import tarfile
import xml.etree.ElementTree as ET
import cv2
from tqdm import tqdm


# URLs des datasets RDD
RDD_DATASETS = {
    "rdd2020": {
        "url": "https://mycityreport.s3-ap-northeast-1.amazonaws.com/02_RoadDamageDataset/public_data/IEEE_bigdata_RDD2020/train.tar.gz",
        "description": "RDD2020 - India, Japan, Czech Republic (GRDDC 2020)"
    },
    "rdd2022": {
        "url": "https://bigdatacup.s3.ap-northeast-1.amazonaws.com/2022/CRDDC2022/RDD2022/RDD2022.zip",
        "description": "RDD2022 - Multi-national dataset (6 countries)"
    },
    "rdd2019": {
        "url": "https://mycityreport.s3-ap-northeast-1.amazonaws.com/02_RoadDamageDataset/public_data/Japan/RDD2020_data.tar.gz",
        "description": "RDD2019 - Japan dataset"
    }
}


def download_file(url: str, output_path: str):
    """Download a file with progress bar."""
    print(f"📥 Téléchargement depuis: {url}")
    print(f"Destination: {output_path}")
    
    def show_progress(block_num, block_size, total_size):
        downloaded = block_num * block_size
        percent = min(downloaded * 100 / total_size, 100)
        print(f"\r   Progression: {percent:.1f}%", end='', flush=True)
    
    urllib.request.urlretrieve(url, output_path, show_progress)
    print("\nTéléchargement terminé")


def extract_archive(archive_path: str, extract_to: str):
    """Extract tar.gz or zip archive."""
    print(f"Extraction de {archive_path} vers {extract_to}")
    
    if archive_path.endswith('.tar.gz'):
        with tarfile.open(archive_path, 'r:gz') as tar:
            tar.extractall(extract_to)
    elif archive_path.endswith('.zip'):
        import zipfile
        with zipfile.ZipFile(archive_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
    
    print("Extraction terminée")


def convert_pascal_voc_to_yolo(xml_file: str, output_txt: str, class_mapping: dict):
    """Convert PASCAL VOC XML annotation to YOLO format.
    
    Args:
        xml_file: Path to PASCAL VOC XML file
        output_txt: Path to output YOLO format file
        class_mapping: Dictionary mapping class names to class IDs
    """
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    # Get image dimensions
    size = root.find('size')
    img_width = int(size.find('width').text)
    img_height = int(size.find('height').text)
    
    yolo_annotations = []
    
    # Process each object
    for obj in root.findall('object'):
        class_name = obj.find('name').text
        
        # Map class name to ID (default to 0 for crack)
        class_id = class_mapping.get(class_name, 0)
        
        # Get bounding box
        bbox = obj.find('bndbox')
        xmin = int(bbox.find('xmin').text)
        ymin = int(bbox.find('ymin').text)
        xmax = int(bbox.find('xmax').text)
        ymax = int(bbox.find('ymax').text)
        
        # Convert to YOLO format (normalized center_x, center_y, width, height)
        center_x = ((xmin + xmax) / 2) / img_width
        center_y = ((ymin + ymax) / 2) / img_height
        width = (xmax - xmin) / img_width
        height = (ymax - ymin) / img_height
        
        yolo_annotations.append(f"{class_id} {center_x:.6f} {center_y:.6f} {width:.6f} {height:.6f}")
    
    # Write YOLO format file
    with open(output_txt, 'w') as f:
        f.write('\n'.join(yolo_annotations))


def convert_dataset_to_yolo(voc_dir: str, output_dir: str, class_mapping: dict):
    """Convert entire PASCAL VOC dataset to YOLO format.
    
    Args:
        voc_dir: Directory containing PASCAL VOC structure (JPEGImages, Annotations)
        output_dir: Output directory for YOLO format
        class_mapping: Dictionary mapping class names to class IDs
    """
    voc_path = Path(voc_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    import shutil
    
    # Find all images recursively (handle nested country folders)
    image_files = []
    for ext in ['*.jpg', '*.JPG', '*.jpeg', '*.JPEG']:
        image_files.extend(voc_path.rglob(ext))
    
    if not image_files:
        print(f"Aucune image trouvée dans: {voc_path}")
        return
    
    print(f"Conversion de {len(image_files)} images...")
    
    for img_file in tqdm(image_files):
        # Create unique filename if needed (handle duplicates from different countries)
        base_name = img_file.stem
        # Add country prefix if in subdirectory
        rel_path = img_file.relative_to(voc_path)
        if len(rel_path.parts) > 1:
            country = rel_path.parts[0]
            base_name = f"{country}_{base_name}"
        
        output_img = output_path / f"{base_name}{img_file.suffix}"
        
        # Copy image
        shutil.copy2(img_file, output_img)
        
        # Find corresponding XML file
        xml_file = img_file.with_suffix('.xml')
        if not xml_file.exists():
            # Try in Annotations directory
            xml_file = img_file.parent.parent / "Annotations" / xml_file.name
        if not xml_file.exists():
            # Try same directory
            xml_file = img_file.parent / xml_file.name
        
        if xml_file.exists():
            txt_file = output_path / f"{base_name}.txt"
            convert_pascal_voc_to_yolo(str(xml_file), str(txt_file), class_mapping)
        else:
            # Create empty annotation file
            txt_file = output_path / f"{base_name}.txt"
            txt_file.touch()


def main():
    parser = argparse.ArgumentParser(description="Download and prepare RDD dataset")
    parser.add_argument("--dataset", type=str, choices=["rdd2020", "rdd2022", "rdd2019"], 
                       default="rdd2020", help="Dataset to download")
    parser.add_argument("--download-dir", type=str, default="dataset_road_damage/downloads",
                       help="Directory to download datasets")
    parser.add_argument("--output-dir", type=str, default="data/raw",
                       help="Output directory for converted dataset")
    parser.add_argument("--skip-download", action="store_true",
                       help="Skip download, only convert existing files")
    
    args = parser.parse_args()
    
    # Class mapping for RDD datasets
    # Mapping all crack types to class 0, potholes to class 1
    class_mapping = {
        "D00": 0,  # Longitudinal Crack
        "D01": 0,  # Longitudinal Construction Joint Crack
        "D10": 0,  # Transverse Crack
        "D11": 0,  # Transverse Construction Joint Crack
        "D20": 0,  # Alligator Crack
        "D40": 1,  # Pothole
        "D43": 1,  # Crosswalk Blur
        "D44": 1,  # White Line Blur
        "crack": 0,
        "pothole": 1
    }
    
    download_dir = Path(args.download_dir)
    download_dir.mkdir(parents=True, exist_ok=True)
    
    if not args.skip_download:
        # Download dataset
        dataset_info = RDD_DATASETS[args.dataset]
        archive_name = dataset_info["url"].split("/")[-1]
        archive_path = download_dir / archive_name
        
        if not archive_path.exists():
            print(f"📥 Téléchargement du dataset: {args.dataset}")
            print(f"   {dataset_info['description']}")
            download_file(dataset_info["url"], str(archive_path))
        else:
            print(f"Archive déjà téléchargée: {archive_path}")
        
        # Extract
        extract_dir = download_dir / args.dataset
        if not extract_dir.exists() or not any(extract_dir.iterdir()):
            extract_archive(str(archive_path), str(extract_dir))
        else:
            print(f"Archive déjà extraite: {extract_dir}")
    else:
        extract_dir = download_dir / args.dataset
        if not extract_dir.exists():
            print(f"Directory not found: {extract_dir}")
            print("   Run without --skip-download first")
            return
    
    # Convert to YOLO format
    print(f"\nConversion vers format YOLO...")
    convert_dataset_to_yolo(str(extract_dir), args.output_dir, class_mapping)
    
    print(f"\nDataset préparé dans: {args.output_dir}")
    print(f"   Vous pouvez maintenant utiliser:")
    print(f"   python scripts/prepare_dataset.py --source {args.output_dir} --create-yaml")


if __name__ == "__main__":
    main()

