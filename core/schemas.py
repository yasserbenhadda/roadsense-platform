from pydantic import BaseModel, Field
from typing import List, Optional

class GPSPoint(BaseModel):
    lat: float = Field(..., description="Latitude en degrés décimaux")
    lon: float = Field(..., description="Longitude en degrés décimaux")

class BoundingBox(BaseModel):
    id: int
    x: float
    y: float
    w: float
    h: float
    severity_score: Optional[float] = None

class GeoRefRequest(BaseModel):
    image_id: str
    gps: GPSPoint
    boxes: List[BoundingBox]

class FissureOut(BaseModel):
    id: int
    image_id: str
    lat: float
    lon: float
    severity_score: Optional[float] = None

    class Config:
        orm_mode = True
