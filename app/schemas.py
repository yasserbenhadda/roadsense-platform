from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

# --- Enums pour la validation stricte ---
class DefectType(str, Enum):
    FISSURE = "fissure"
    NID_DE_POULE = "nid_de_poule"
    ARRACHEMENT = "arrachement"
    AUTRE = "autre"

class UrgencyLevel(str, Enum):
    FAIBLE = "faible"
    MODERE = "modere"
    URGENT = "urgent"

# ==========================================
# SCHEMAS POUR LES DÉFAUTS (Defects)
# ==========================================

# Base commune (champs partagés)
class DefectBase(BaseModel):
    defect_type: DefectType = Field(..., description="Le type de défaut détecté")
    length: float = Field(..., gt=0, description="Longueur en mètres")
    width: float = Field(..., gt=0, description="Largeur en mètres")
    depth: Optional[float] = Field(None, ge=0, description="Profondeur estimée en mètres (optionnel)")
    ai_confidence: float = Field(..., ge=0, le=1, description="Confiance de l'IA (entre 0 et 1)")
    
    # Coordonnées GPS simples pour l'input (plus facile que WKT)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)

# INPUT : Ce que l'API reçoit via POST /severity/compute
class DefectInput(DefectBase):
    # On peut ajouter ici l'ID du tronçon si on le connaît déjà, 
    # sinon le système GeoRef le trouvera via les coordonnées.
    section_id: Optional[int] = None 

# OUTPUT : Ce que l'API renvoie au client
class DefectResponse(DefectBase):
    id: int
    severity_score: float
    created_at: datetime

    # Permet à Pydantic de lire les objets SQLAlchemy (ORM)
    class Config:
        from_attributes = True 

# ==========================================
# SCHEMAS POUR LA PRIORISATION (Road Sections)
# ==========================================

class RoadSectionBase(BaseModel):
    name: str
    avg_score: float
    urgency_level: UrgencyLevel

# OUTPUT : Pour la liste priorisée GET /priorisation
class RoadSectionResponse(RoadSectionBase):
    id: int
    # On pourrait ajouter le nombre de défauts ici si besoin
    defect_count: Optional[int] = 0

    class Config:
        from_attributes = True