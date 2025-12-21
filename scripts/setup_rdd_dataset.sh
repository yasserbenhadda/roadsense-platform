#!/bin/bash
# Script pour télécharger et configurer le dataset RDD

echo "Configuration du dataset Road Damage Detection"
echo "=================================================="
echo ""

# Activer l'environnement virtuel si disponible
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Options disponibles
echo "Datasets disponibles:"
echo "  1. RDD2020 - India, Japan, Czech Republic (recommandé pour commencer)"
echo "  2. RDD2022 - Multi-national (6 pays, plus grand)"
echo "  3. RDD2019 - Japan dataset"
echo ""

read -p "Choisissez un dataset (1-3) [1]: " choice
choice=${choice:-1}

case $choice in
    1)
        DATASET="rdd2020"
        ;;
    2)
        DATASET="rdd2022"
        ;;
    3)
        DATASET="rdd2019"
        ;;
    *)
        echo "Choix invalide, utilisation de RDD2020"
        DATASET="rdd2020"
        ;;
esac

echo ""
echo "📥 Téléchargement et préparation du dataset: $DATASET"
echo ""

# Exécuter le script Python
python scripts/download_rdd_dataset.py --dataset "$DATASET"

echo ""
echo "Configuration terminée !"
echo ""
echo "Prochaines étapes:"
echo "  1. Préparer le dataset:"
echo "     python scripts/prepare_dataset.py --source data/raw --create-yaml"
echo ""
echo "  2. Entraîner le modèle:"
echo "     python app/training/train_yolov8.py --data data/dataset.yaml"

