from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from geoalchemy2 import Geometry
from .database import Base
from datetime import datetime

class RoadSection(Base):
    __tablename__ = "road_sections"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    # Géométrie de type Ligne (le tronçon de route)
    geom = Column(Geometry('LINESTRING', srid=4326)) 
    avg_score = Column(Float, default=0.0)
    urgency_level = Column(String, default="faible") # faible, modere, urgent

class Defect(Base):
    __tablename__ = "defects"
    id = Column(Integer, primary_key=True, index=True)
    section_id = Column(Integer, ForeignKey("road_sections.id")) # Lien vers le tronçon
    defect_type = Column(String) # fissure, nid_de_poule
    length = Column(Float)
    width = Column(Float)
    depth = Column(Float, nullable=True) # Peut venir de la stéréoscopie ou estimation
    ai_confidence = Column(Float) # Score venant de YOLO
    severity_score = Column(Float) # Calculé par ton service
    # Géométrie de type Point (position exacte du défaut)
    geom = Column(Geometry('POINT', srid=4326)) 
    created_at = Column(DateTime, default=datetime.utcnow)