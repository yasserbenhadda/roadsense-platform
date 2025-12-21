# RoadSense - GeoRef Microservice

Microservice de géoréférencement des fissures pour la plateforme RoadSense.

## Description

Ce microservice gère la géoréférencement des fissures détectées sur les routes, permettant de localiser précisément chaque fissure sur une carte géographique.

## Stack Technologique

- **FastAPI** - Framework web Python haute performance
- **SQLAlchemy** - ORM pour la gestion de base de données
- **GeoAlchemy2** - Extension géospatiale pour SQLAlchemy
- **PostgreSQL + PostGIS** - Base de données géospatiale
- **Docker** - Containerisation
- **Pydantic** - Validation de données

## Installation

### Prérequis

- Python 3.10+
- Docker & Docker Compose
- Git

### Setup Local

1. **Cloner le repository**
```bash
git clone https://github.com/RoadSense-MS/roadsense-georef.git
cd roadsense-georef
```

2. **Créer un environnement virtuel**
```bash
python -m venv venv
# Sur Windows
venv\Scripts\activate
# Sur Linux/Mac
source venv/bin/activate
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Configurer les variables d'environnement**
Créez un fichier `.env` à la racine du projet :
```
DATABASE_URL=postgresql://yasser:yasser@localhost:5432/roadsense
```

## Démarrage

### Avec Docker Compose

```bash
docker-compose up -d
```

Cela démarrera la base de données PostgreSQL + PostGIS.

### Lancer l'API

```bash
uvicorn api.main:app --reload
```

L'API sera accessible sur `http://localhost:8000`

### Documentation Interactive

- **Swagger UI** : `http://localhost:8000/docs`
- **ReDoc** : `http://localhost:8000/redoc`

## Structure du Projet

```
roadsense-georef/
├── api/                    # Couche API FastAPI
│   ├── __init__.py
│   ├── main.py            # Point d'entrée de l'application
│   └── routers/           # Routes de l'API
│       ├── __init__.py
│       └── georef.py      # Routes de géoréférencement
├── core/                   # Logique métier
│   ├── __init__.py
│   ├── db.py              # Configuration de la base de données
│   ├── models.py          # Modèles SQLAlchemy
│   └── schemas.py         # Schémas Pydantic
├── exports/                # Module d'export de données
│   ├── __init__.py
│   ├── geojson_export.py  # Export des fissures en GeoJSON
│   └── geojson/           # Fichiers GeoJSON générés
│       └── fissures.geojson
├── .env                    # Variables d'environnement (à créer)
├── requirements.txt        # Dépendances Python
├── docker-compose.yml      # Configuration Docker
└── README.md              # Ce fichier
```

## Endpoints Disponibles

### Géoréférencement
- `GET /georef/` - Récupérer les données de géoréférencement

## Exports de Données

Le module `exports/` permet d'exporter les données des fissures dans différents formats :

### GeoJSON Export
```bash
python -m exports.geojson_export
```

Cela génère un fichier `exports/geojson/fissures.geojson` contenant toutes les fissures georéférencées au format GeoJSON.

**Format GeoJSON :**
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {
        "id": "fissure_001",
        "severity": "high",
        "date_detected": "2025-11-26"
      },
      "geometry": {
        "type": "LineString",
        "coordinates": [[lon, lat], [lon, lat]]
      }
    }
  ]
}
```

## Développement

### Ajouter une nouvelle dépendance

```bash
pip install <package_name>
pip freeze > requirements.txt
```

### Lancer les tests

```bash
pytest
```

## Base de Données

La base de données utilise PostgreSQL avec l'extension PostGIS pour les opérations géospatiales.

**Identifiants par défaut :**
- User: `yasser`
- Password: `yasser`
- Database: `roadsense`
- Port: `5432`

## Contribution

1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## Licence

Ce projet est propriété de RoadSense-MS.

## Support

Pour toute question ou problème, veuillez ouvrir une issue sur GitHub.
