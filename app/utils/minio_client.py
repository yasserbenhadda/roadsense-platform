"""MinIO client for storing and retrieving images."""
import io
from typing import Optional, BinaryIO
from minio import Minio
from minio.error import S3Error
import logging
from app.utils.config_loader import config

logger = logging.getLogger(__name__)


class MinIOClient:
    """Client for interacting with MinIO storage."""
    
    def __init__(self):
        """Initialize MinIO client."""
        self.client = Minio(
            config.get("minio.endpoint"),
            access_key=config.get("minio.access_key"),
            secret_key=config.get("minio.secret_key"),
            secure=config.get("minio.secure", False)
        )
        self.bucket_name = config.get("minio.bucket_name")
        self.annotated_bucket = config.get("minio.annotated_bucket")
        self._ensure_buckets()
    
    def _ensure_buckets(self):
        """Ensure required buckets exist."""
        buckets = [self.bucket_name, self.annotated_bucket]
        for bucket in buckets:
            try:
                if not self.client.bucket_exists(bucket):
                    self.client.make_bucket(bucket)
                    logger.info(f"Created bucket: {bucket}")
            except S3Error as e:
                logger.error(f"Error creating bucket {bucket}: {e}")
    
    def upload_image(self, image_data: bytes, object_name: str, bucket: Optional[str] = None) -> bool:
        """Upload image to MinIO.
        
        Args:
            image_data: Image bytes
            object_name: Object name in bucket
            bucket: Bucket name (defaults to main bucket)
        
        Returns:
            True if successful, False otherwise
        """
        bucket = bucket or self.bucket_name
        try:
            image_stream = io.BytesIO(image_data)
            self.client.put_object(
                bucket,
                object_name,
                image_stream,
                length=len(image_data),
                content_type="image/jpeg"
            )
            logger.info(f"Uploaded image: {object_name} to bucket: {bucket}")
            return True
        except S3Error as e:
            logger.error(f"Error uploading image {object_name}: {e}")
            return False
    
    def download_image(self, object_name: str, bucket: Optional[str] = None) -> Optional[bytes]:
        """Download image from MinIO.
        
        Args:
            object_name: Object name in bucket
            bucket: Bucket name (defaults to main bucket)
        
        Returns:
            Image bytes or None if error
        """
        bucket = bucket or self.bucket_name
        try:
            response = self.client.get_object(bucket, object_name)
            image_data = response.read()
            response.close()
            response.release_conn()
            return image_data
        except S3Error as e:
            logger.error(f"Error downloading image {object_name}: {e}")
            return None
    
    def upload_annotated_image(self, image_data: bytes, object_name: str) -> bool:
        """Upload annotated image to annotated bucket.
        
        Args:
            image_data: Annotated image bytes
            object_name: Object name in bucket
        
        Returns:
            True if successful, False otherwise
        """
        return self.upload_image(image_data, object_name, self.annotated_bucket)
    
    def list_images(self, prefix: str = "", bucket: Optional[str] = None):
        """List images in bucket.
        
        Args:
            prefix: Prefix to filter objects
            bucket: Bucket name (defaults to main bucket)
        
        Returns:
            List of object names
        """
        bucket = bucket or self.bucket_name
        try:
            objects = self.client.list_objects(bucket, prefix=prefix, recursive=True)
            return [obj.object_name for obj in objects]
        except S3Error as e:
            logger.error(f"Error listing images: {e}")
            return []

