"""FastAPI application for crack detection service."""
import time
import logging
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np
from PIL import Image
import io
from typing import Optional
import base64

from app.models.yolov8_model import YOLOv8CrackDetector
from app.models.mask_rcnn_model import MaskRCNNCrackDetector
from app.utils.minio_client import MinIOClient
from app.utils.database import Database
from app.utils.config_loader import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Crack Detection API",
    description="Microservice IA pour la détection de fissures routières",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize models (lazy loading)
yolov8_detector: Optional[YOLOv8CrackDetector] = None
mask_rcnn_detector: Optional[MaskRCNNCrackDetector] = None
minio_client: Optional[MinIOClient] = None
database: Optional[Database] = None


def get_yolov8_detector() -> YOLOv8CrackDetector:
    """Get or initialize YOLOv8 detector."""
    global yolov8_detector
    if yolov8_detector is None:
        try:
            logger.info("Initializing YOLOv8 detector...")
            yolov8_detector = YOLOv8CrackDetector()
        except ImportError as e:
            logger.error(f"Failed to initialize YOLOv8: {e}")
            raise HTTPException(status_code=503, detail=f"YOLOv8 model not available: {str(e)}")
    return yolov8_detector


def get_mask_rcnn_detector() -> MaskRCNNCrackDetector:
    """Get or initialize Mask R-CNN detector."""
    global mask_rcnn_detector
    if mask_rcnn_detector is None:
        try:
            logger.info("Initializing Mask R-CNN detector...")
            mask_rcnn_detector = MaskRCNNCrackDetector()
        except ImportError as e:
            logger.error(f"Failed to initialize Mask R-CNN: {e}")
            raise HTTPException(status_code=503, detail=f"Mask R-CNN model not available: {str(e)}")
    return mask_rcnn_detector


def get_minio_client() -> MinIOClient:
    """Get or initialize MinIO client."""
    global minio_client
    if minio_client is None:
        logger.info("Initializing MinIO client...")
        minio_client = MinIOClient()
    return minio_client


def get_database() -> Database:
    """Get or initialize database."""
    global database
    if database is None:
        logger.info("Initializing database...")
        database = Database()
    return database


def load_image_from_bytes(image_bytes: bytes) -> np.ndarray:
    """Load image from bytes.
    
    Args:
        image_bytes: Image bytes
    
    Returns:
        Image as numpy array (BGR format)
    """
    image = Image.open(io.BytesIO(image_bytes))
    image = image.convert("RGB")
    image_array = np.array(image)
    # Convert RGB to BGR for OpenCV
    image_bgr = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
    return image_bgr


def draw_detections(image: np.ndarray, detections: list, masks: Optional[np.ndarray] = None) -> np.ndarray:
    """Draw detections on image.
    
    Args:
        image: Input image
        detections: List of detections
        masks: Optional combined mask
    
    Returns:
        Annotated image
    """
    annotated = image.copy()
    
    # Draw bounding boxes
    for det in detections:
        bbox = det["bbox"]
        conf = det["confidence"]
        x1, y1, x2, y2 = map(int, bbox)
        
        # Draw rectangle
        cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)
        
        # Draw label
        label = f"Crack: {conf:.2f}"
        cv2.putText(annotated, label, (x1, y1 - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    # Draw mask overlay
    if masks is not None:
        mask_colored = cv2.applyColorMap(masks, cv2.COLORMAP_JET)
        annotated = cv2.addWeighted(annotated, 0.7, mask_colored, 0.3, 0)
    
    return annotated


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Crack Detection API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/detect")
async def detect_cracks(
    image: UploadFile = File(...),
    model: str = "yolov8",
    return_image: bool = False,
    save_to_minio: bool = False
):
    """Detect cracks in uploaded image.
    
    Args:
        image: Uploaded image file
        model: Model to use ("yolov8" or "mask_rcnn")
        return_image: Whether to return annotated image
        save_to_minio: Whether to save annotated image to MinIO
    
    Returns:
        Detection results with bounding boxes, masks, and confidence scores
    """
    start_time = time.time()
    
    try:
        # Read image
        image_bytes = await image.read()
        if len(image_bytes) > config.get("api.max_image_size", 10485760):
            raise HTTPException(status_code=400, detail="Image too large")
        
        image_array = load_image_from_bytes(image_bytes)
        original_height, original_width = image_array.shape[:2]
        
        # Run detection
        if model.lower() == "yolov8":
            detector = get_yolov8_detector()
            detections, masks = detector.detect_with_masks(image_array)
        elif model.lower() == "mask_rcnn":
            detector = get_mask_rcnn_detector()
            detections, masks = detector.detect(image_array)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown model: {model}")
        
        inference_time = (time.time() - start_time) * 1000  # Convert to ms
        
        # Prepare response
        response = {
            "model": model,
            "num_detections": len(detections),
            "detections": detections,
            "inference_time_ms": round(inference_time, 2),
            "image_size": {
                "width": original_width,
                "height": original_height
            }
        }
        
        # Add mask if available
        if masks is not None:
            # Encode mask as base64
            _, mask_buffer = cv2.imencode('.png', masks)
            mask_base64 = base64.b64encode(mask_buffer).decode('utf-8')
            response["mask_base64"] = mask_base64
        
        # Draw annotations and save if requested
        if return_image or save_to_minio:
            annotated_image = draw_detections(image_array, detections, masks)
            _, img_buffer = cv2.imencode('.jpg', annotated_image)
            annotated_bytes = img_buffer.tobytes()
            
            if return_image:
                annotated_base64 = base64.b64encode(annotated_bytes).decode('utf-8')
                response["annotated_image_base64"] = annotated_base64
            
            if save_to_minio:
                minio = get_minio_client()
                object_name = f"annotated_{int(time.time())}_{image.filename}"
                minio.upload_annotated_image(annotated_bytes, object_name)
                response["minio_object_name"] = object_name
        
        # Check performance targets
        target_time = config.get("targets.inference_time_ms", 300)
        if inference_time > target_time:
            logger.warning(f"Inference time {inference_time:.2f}ms exceeds target {target_time}ms")
        
        # Save to database if available
        try:
            db = get_database()
            if db.session is not None:
                db.save_detection_result(
                    image_filename=image.filename or "unknown",
                    model_name=model,
                    num_detections=len(detections),
                    detections=detections,
                    inference_time_ms=inference_time,
                    image_width=original_width,
                    image_height=original_height,
                    minio_object_name=response.get("minio_object_name")
                )
        except Exception as e:
            logger.warning(f"Failed to save to database: {e}")
        
        return JSONResponse(content=response)
    
    except Exception as e:
        logger.error(f"Error during detection: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Detection failed: {str(e)}")


@app.post("/detect/batch")
async def detect_cracks_batch(
    images: list[UploadFile] = File(...),
    model: str = "yolov8"
):
    """Detect cracks in multiple images.
    
    Args:
        images: List of uploaded image files
        model: Model to use ("yolov8" or "mask_rcnn")
    
    Returns:
        List of detection results
    """
    results = []
    
    for image in images:
        try:
            result = await detect_cracks(image, model, return_image=False, save_to_minio=False)
            results.append(result)
        except Exception as e:
            results.append({
                "filename": image.filename,
                "error": str(e)
            })
    
    return {"results": results, "total": len(results)}


@app.get("/metrics")
async def get_metrics():
    """Get model performance metrics."""
    # This would typically query a metrics database
    # For now, return placeholder
    return {
        "yolov8": {
            "map50": 0.0,
            "map50_95": 0.0,
            "avg_inference_time_ms": 0.0
        },
        "mask_rcnn": {
            "map50": 0.0,
            "map50_95": 0.0,
            "avg_inference_time_ms": 0.0
        }
    }


@app.get("/results")
async def get_detection_results(
    limit: int = 100,
    model_name: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """Get detection results from PostgreSQL database.
    
    Args:
        limit: Maximum number of results to return
        model_name: Filter by model name (yolov8, mask_rcnn)
        start_date: Filter by start date (ISO format: YYYY-MM-DD)
        end_date: Filter by end date (ISO format: YYYY-MM-DD)
    
    Returns:
        List of detection results
    """
    try:
        db = get_database()
        if db.session is None:
            raise HTTPException(status_code=503, detail="Database not available")
        
        from datetime import datetime
        from sqlalchemy import and_
        from app.utils.database import DetectionResult
        
        query = db.session.query(DetectionResult)
        
        # Apply filters
        if model_name:
            query = query.filter(DetectionResult.model_name == model_name)
        
        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date)
                query = query.filter(DetectionResult.created_at >= start_dt)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid start_date format. Use YYYY-MM-DD")
        
        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date)
                query = query.filter(DetectionResult.created_at <= end_dt)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid end_date format. Use YYYY-MM-DD")
        
        # Get results
        results = query.order_by(DetectionResult.created_at.desc()).limit(limit).all()
        
        # Convert to dict
        results_list = []
        for result in results:
            results_list.append({
                "id": result.id,
                "image_filename": result.image_filename,
                "model_name": result.model_name,
                "num_detections": result.num_detections,
                "detections": result.detections,
                "inference_time_ms": result.inference_time_ms,
                "image_size": {
                    "width": result.image_width,
                    "height": result.image_height
                },
                "minio_object_name": result.minio_object_name,
                "created_at": result.created_at.isoformat() if result.created_at else None
            })
        
        return {
            "total": len(results_list),
            "results": results_list
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching results: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch results: {str(e)}")


@app.get("/results/stats")
async def get_detection_stats():
    """Get statistics about detection results.
    
    Returns:
        Statistics summary
    """
    try:
        db = get_database()
        if db.session is None:
            raise HTTPException(status_code=503, detail="Database not available")
        
        from sqlalchemy import func
        from app.utils.database import DetectionResult
        
        # Get statistics
        total_detections = db.session.query(func.count(DetectionResult.id)).scalar() or 0
        avg_inference_time = db.session.query(func.avg(DetectionResult.inference_time_ms)).scalar() or 0
        total_images = db.session.query(func.count(func.distinct(DetectionResult.image_filename))).scalar() or 0
        
        # Get model-specific stats
        model_stats = {}
        for model_name in ["yolov8", "mask_rcnn"]:
            model_query = db.session.query(DetectionResult).filter(
                DetectionResult.model_name == model_name
            )
            model_count = model_query.count()
            model_avg_time = db.session.query(func.avg(DetectionResult.inference_time_ms)).filter(
                DetectionResult.model_name == model_name
            ).scalar() or 0
            
            if model_count > 0:
                model_stats[model_name] = {
                    "total_detections": model_count,
                    "avg_inference_time_ms": round(model_avg_time, 2)
                }
        
        return {
            "total_detections": total_detections,
            "total_unique_images": total_images,
            "avg_inference_time_ms": round(avg_inference_time, 2),
            "models": model_stats
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch stats: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    host = config.get("api.host", "0.0.0.0")
    port = config.get("api.port", 8000)
    uvicorn.run(app, host=host, port=port)

