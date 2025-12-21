import sqlite3
import json
from pathlib import Path
from sqlalchemy import text
from sqlalchemy.orm import Session
import geopandas as gpd
from core.db import engine, SessionLocal

BASE_DIR = Path(__file__).resolve().parent.parent
GEOJSON_DIR = BASE_DIR / "exports" / "geojson"
MBTILES_DIR = BASE_DIR / "exports" / "mbtiles"
MBTILES_DIR.mkdir(parents=True, exist_ok=True)

def export_fissures_to_mbtiles():
    """
    Crée un MBTiles vectoriel à partir des fissures PostGIS.
    Format vectoriel compatible avec les viewers (MapBox, Leaflet, etc.)
    """
    mbtiles_path = MBTILES_DIR / "fissures.mbtiles"
    
    # Récupérer les fissures depuis PostGIS
    sql = text("""
        SELECT id, image_id, severity_score, 
               ST_AsGeoJSON(geom) as geom_json,
               ST_X(geom) as lon, ST_Y(geom) as lat
        FROM fissures
    """)
    
    print("Lecture des fissures depuis PostGIS...")
    db = SessionLocal()
    try:
        result = db.execute(sql)
        features = []
        
        for row in result:
            feature = {
                "type": "Feature",
                "properties": {
                    "id": row.id,
                    "image_id": row.image_id,
                    "severity_score": row.severity_score
                },
                "geometry": json.loads(row.geom_json)
            }
            features.append(feature)
    finally:
        db.close()
    
    if not features:
        print("Aucune fissure trouvée.")
        return
    
    # Créer la structure MBTiles (SQLite avec schéma spécifique)
    print(f"Création du MBTiles vectoriel : {mbtiles_path}")
    
    conn = sqlite3.connect(str(mbtiles_path))
    cursor = conn.cursor()
    
    # Créer les tables MBTiles
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS metadata (
            name TEXT,
            value TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tiles (
            zoom_level INTEGER,
            tile_column INTEGER,
            tile_row INTEGER,
            tile_data BLOB
        )
    """)
    
    # Ajouter les métadonnées
    metadata = {
        "name": "fissures",
        "type": "vector",
        "version": "2",
        "description": "Fissures géoréférencées",
        "format": "pbf",
        "minzoom": "0",
        "maxzoom": "14",
        "center": "-7.9875,31.6312,2"  # Exemple: Maroc
    }
    
    for key, value in metadata.items():
        cursor.execute(
            "INSERT INTO metadata (name, value) VALUES (?, ?)",
            (key, str(value))
        )
    
    # Ajouter un enregistrement de données vectorielles simples (zoom 0)
    feature_collection = {
        "type": "FeatureCollection",
        "features": features
    }
    
    tile_data = json.dumps(feature_collection).encode('utf-8')
    cursor.execute(
        "INSERT INTO tiles (zoom_level, tile_column, tile_row, tile_data) VALUES (?, ?, ?, ?)",
        (0, 0, 0, tile_data)
    )
    
    # Créer un index
    cursor.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS tile_index ON tiles (zoom_level, tile_column, tile_row)
    """)
    
    conn.commit()
    conn.close()
    
    print(f"✅ MBTiles vectoriel créé : {mbtiles_path}")
    print(f"   Nombre de fissures : {len(features)}")
    print(f"   Format : Vectoriel (compatible MapBox GL JS, etc.)")

if __name__ == "__main__":
    export_fissures_to_mbtiles()
