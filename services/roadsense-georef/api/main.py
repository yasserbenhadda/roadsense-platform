from fastapi import FastAPI
from .routers import georef

app = FastAPI(
    title="RoadSense - GeoRef Microservice",
    description="Microservice de géoréférencement des fissures",
    version="0.1.0"
)

app.include_router(georef.router)
