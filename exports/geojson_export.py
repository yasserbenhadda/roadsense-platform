import os
from pathlib import Path

import geopandas as gpd
from sqlalchemy import text

from core.db import engine

# Dossier de sortie
BASE_DIR = Path(__file__).resolve().parent.parent
EXPORT_DIR = BASE_DIR / "exports" / "geojson"
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

def export_fissures_to_geojson():
    """
    Lit la table 'fissures' dans PostGIS et génère un fichier GeoJSON.
    """

    # Requête SQL : on récupère id, image_id, severity_score, et la géométrie
    sql = text("""
        SELECT id, image_id, severity_score, geom
        FROM fissures
    """)

    print("Connexion à la base et lecture des fissures...")
    gdf = gpd.read_postgis(sql, con=engine, geom_col="geom")

    if gdf.empty:
        print("Aucune fissure trouvée dans la base.")
        return

    output_path = EXPORT_DIR / "fissures.geojson"
    print(f"Export vers {output_path} ...")
    gdf.to_file(output_path, driver="GeoJSON")
    print("Export terminé ✅")

if __name__ == "__main__":
    export_fissures_to_geojson()
