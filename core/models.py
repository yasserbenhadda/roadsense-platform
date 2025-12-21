from sqlalchemy import Column, Integer, String, Float, DateTime, func
from geoalchemy2 import Geometry
from geoalchemy2 import Geometry
from sqlalchemy import Column, Integer, String, Float, DateTime, func
from .db import Base

class Fissure(Base):
    __tablename__ = "fissures"

    id = Column(Integer, primary_key=True, index=True)
    image_id = Column(String, nullable=False)
    severity_score = Column(Float, nullable=True)
    # Point géographique en WGS84 (EPSG:4326)
    geom = Column(Geometry(geometry_type="POINT", srid=4326), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Segment(Base):
    __tablename__ = "segments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)  # optionnel
    geom = Column(Geometry(geometry_type="LINESTRING", srid=4326), nullable=False)

class Troncon(Base):
    __tablename__ = "troncons"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)  # optionnel
    importance = Column(Integer, nullable=True)
    geom = Column(Geometry(geometry_type="LINESTRING", srid=4326), nullable=False)