from core.georef_logic import compute_fissure_position
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from shapely.geometry import Point
from geoalchemy2.shape import from_shape

from core.db import get_db
from core import models, schemas

router = APIRouter(
    prefix="/georef",
    tags=["GeoRef"]
)

@router.post("/", response_model=dict)
def georef_defauts(payload: schemas.GeoRefRequest, db: Session = Depends(get_db)):
    """
    Réceptionne les défauts d'une image, les géoréférence
    et les enregistre dans la base PostGIS.
    """

    fissures_out = []

    for box in payload.boxes:
        # Pour l'instant : même coordonnée GPS pour chaque fissure
        lon = payload.gps.lon
        lat = payload.gps.lat

        shapely_point = compute_fissure_position(
    base_lon=payload.gps.lon,
    base_lat=payload.gps.lat,
    x=box.x,
    y=box.y
)

        geom = from_shape(shapely_point, srid=4326)

        fissure = models.Fissure(
            image_id=payload.image_id,
            severity_score=box.severity_score,
            geom=geom
        )

        db.add(fissure)
        db.flush()  # pour obtenir l'ID sans commit

        fissures_out.append({
            "id": fissure.id,
            "image_id": fissure.image_id,
            "lat": lat,
            "lon": lon,
            "severity_score": fissure.severity_score
        })

    db.commit()

    return {"fissures": fissures_out}
