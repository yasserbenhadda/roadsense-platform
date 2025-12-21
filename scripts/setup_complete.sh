#!/bin/bash
# Complete setup script for the crack detection project

set -e

echo "Configuration complète du projet de détection de fissures"
echo "=============================================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check Python version
echo "1️⃣  Vérification de Python 3.11..."
if command -v python3.11 &> /dev/null; then
    PYTHON_VERSION=$(python3.11 --version)
    echo -e "${GREEN}$PYTHON_VERSION trouvé${NC}"
else
    echo -e "${RED}Python 3.11 non trouvé${NC}"
    echo "Veuillez installer Python 3.11"
    exit 1
fi

# Create virtual environment
echo ""
echo "2️⃣  Création de l'environnement virtuel..."
if [ ! -d "venv" ]; then
    python3.11 -m venv venv
    echo -e "${GREEN}Environnement virtuel créé${NC}"
else
    echo -e "${YELLOW}Environnement virtuel existe déjà${NC}"
fi

# Activate virtual environment
echo ""
echo "3️⃣  Activation de l'environnement virtuel..."
source venv/bin/activate
echo -e "${GREEN}Environnement activé${NC}"

# Install dependencies
echo ""
echo "4️⃣  Installation des dépendances..."
pip install --upgrade pip
pip install -r requirements.txt
echo -e "${GREEN}Dépendances installées${NC}"

# Install Detectron2 if needed
echo ""
echo "5️⃣  Installation de Detectron2 (pour Mask R-CNN)..."
if python -c "import detectron2" 2>/dev/null; then
    echo -e "${YELLOW}Detectron2 déjà installé${NC}"
else
    echo "   Installation en cours (cela peut prendre plusieurs minutes)..."
    pip install 'git+https://github.com/facebookresearch/detectron2.git' || {
        echo -e "${YELLOW}Installation de Detectron2 échouée. Vous pouvez l'installer plus tard.${NC}"
    }
fi

# Create necessary directories
echo ""
echo "6️⃣  Création des répertoires nécessaires..."
mkdir -p weights data logs reports config
echo -e "${GREEN}Répertoires créés${NC}"

# Initialize database (if PostgreSQL is available)
echo ""
echo "7️⃣  Initialisation de la base de données..."
if python scripts/init_database.py 2>/dev/null; then
    echo -e "${GREEN}Base de données initialisée${NC}"
else
    echo -e "${YELLOW}Base de données non disponible (PostgreSQL non configuré)${NC}"
    echo "   Vous pouvez l'initialiser plus tard avec: python scripts/init_database.py"
fi

# Summary
echo ""
echo "=============================================================="
echo -e "${GREEN}Configuration terminée avec succès !${NC}"
echo ""
echo "Prochaines étapes:"
echo ""
echo "1. Préparer le dataset:"
echo "   python scripts/prepare_dataset.py --source <dataset_dir> --create-yaml"
echo ""
echo "2. Entraîner les modèles:"
echo "   python scripts/train_all.py --data data/dataset.yaml --epochs 100"
echo ""
echo "3. Démarrer l'API:"
echo "   uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --reload"
echo ""
echo "4. Ou utiliser Docker:"
echo "   docker-compose up --build"
echo ""
echo "=============================================================="

