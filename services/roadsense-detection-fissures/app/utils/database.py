"""Database utilities for storing detection results."""
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from typing import Optional
from app.utils.config_loader import config
import logging

logger = logging.getLogger(__name__)

Base = declarative_base()


class DetectionResult(Base):
    """Database model for detection results."""
    __tablename__ = "detection_results"
    
    id = Column(Integer, primary_key=True, index=True)
    image_filename = Column(String, index=True)
    model_name = Column(String)
    num_detections = Column(Integer)
    detections = Column(JSON)
    inference_time_ms = Column(Float)
    image_width = Column(Integer)
    image_height = Column(Integer)
    minio_object_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Database:
    """Database manager."""
    
    def __init__(self):
        """Initialize database connection."""
        db_host = config.get("database.host", "localhost")
        db_port = config.get("database.port", 5432)
        db_name = config.get("database.name", "crack_detection")
        db_user = config.get("database.user", "postgres")
        db_password = config.get("database.password", "postgres")
        
        database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        
        try:
            self.engine = create_engine(database_url)
            Base.metadata.create_all(bind=self.engine)
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            self.session = SessionLocal()
            logger.info("Database connection established")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            self.session = None
    
    def save_detection_result(
        self,
        image_filename: str,
        model_name: str,
        num_detections: int,
        detections: list,
        inference_time_ms: float,
        image_width: int,
        image_height: int,
        minio_object_name: Optional[str] = None
    ) -> Optional[int]:
        """Save detection result to database.
        
        Args:
            image_filename: Name of the image file
            model_name: Name of the model used
            num_detections: Number of detections
            detections: List of detection dictionaries
            inference_time_ms: Inference time in milliseconds
            image_width: Image width
            image_height: Image height
            minio_object_name: Optional MinIO object name
        
        Returns:
            ID of the saved record or None if error
        """
        if self.session is None:
            logger.warning("Database session not available")
            return None
        
        try:
            result = DetectionResult(
                image_filename=image_filename,
                model_name=model_name,
                num_detections=num_detections,
                detections=detections,
                inference_time_ms=inference_time_ms,
                image_width=image_width,
                image_height=image_height,
                minio_object_name=minio_object_name
            )
            self.session.add(result)
            self.session.commit()
            self.session.refresh(result)
            logger.info(f"Saved detection result with ID: {result.id}")
            return result.id
        except Exception as e:
            logger.error(f"Error saving detection result: {e}")
            self.session.rollback()
            return None
    
    def get_recent_results(self, limit: int = 100):
        """Get recent detection results.
        
        Args:
            limit: Maximum number of results to return
        
        Returns:
            List of detection results
        """
        if self.session is None:
            return []
        
        try:
            results = self.session.query(DetectionResult)\
                .order_by(DetectionResult.created_at.desc())\
                .limit(limit)\
                .all()
            return results
        except Exception as e:
            logger.error(f"Error fetching results: {e}")
            return []

