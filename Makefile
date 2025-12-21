.PHONY: help install train test docker-build docker-up docker-down clean

help:
	@echo "Commandes disponibles:"
	@echo "  make install      - Installer les dépendances"
	@echo "  make train-yolo   - Entraîner le modèle YOLOv8"
	@echo "  make train-rcnn   - Entraîner le modèle Mask R-CNN"
	@echo "  make test         - Tester l'API"
	@echo "  make docker-build - Construire l'image Docker"
	@echo "  make docker-up    - Démarrer avec Docker Compose"
	@echo "  make docker-down  - Arrêter Docker Compose"
	@echo "  make clean        - Nettoyer les fichiers temporaires"

install:
	pip install -r requirements.txt
	python -m pip install 'git+https://github.com/facebookresearch/detectron2.git'

train-yolo:
	python app/training/train_yolov8.py --data data/dataset.yaml --epochs 100

train-rcnn:
	python app/training/train_mask_rcnn.py \
		--train-json data/train_annotations.json \
		--train-images data/train \
		--val-json data/val_annotations.json \
		--val-images data/val

test:
	python scripts/test_api.py --image data/test/sample.jpg

docker-build:
	docker build -t crack-detection-api .

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

clean:
	@echo "🧹 Nettoyage du projet..."
	@find . -type d -name __pycache__ -not -path "./venv/*" -exec rm -r {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -not -path "./venv/*" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -not -path "./venv/*" -delete 2>/dev/null || true
	@find . -type f -name "*.log" -not -path "./venv/*" -delete 2>/dev/null || true
	@find . -name ".DS_Store" -delete 2>/dev/null || true
	@rm -f data/*.cache 2>/dev/null || true
	@echo "✅ Nettoyage terminé"

