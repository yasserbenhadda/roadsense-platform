"""Configuration loader for the crack detection service."""
import os
import yaml
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Configuration manager for the application."""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize configuration from YAML file and environment variables."""
        self.config_path = Path(config_path)
        self.config = self._load_yaml()
        self._override_with_env()
    
    def _load_yaml(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def _override_with_env(self):
        """Override configuration with environment variables."""
        # MinIO
        if os.getenv("MINIO_ENDPOINT"):
            self.config["minio"]["endpoint"] = os.getenv("MINIO_ENDPOINT")
        if os.getenv("MINIO_ACCESS_KEY"):
            self.config["minio"]["access_key"] = os.getenv("MINIO_ACCESS_KEY")
        if os.getenv("MINIO_SECRET_KEY"):
            self.config["minio"]["secret_key"] = os.getenv("MINIO_SECRET_KEY")
        if os.getenv("MINIO_BUCKET_NAME"):
            self.config["minio"]["bucket_name"] = os.getenv("MINIO_BUCKET_NAME")
        
        # Database
        if os.getenv("DB_HOST"):
            self.config["database"]["host"] = os.getenv("DB_HOST")
        if os.getenv("DB_PORT"):
            self.config["database"]["port"] = int(os.getenv("DB_PORT"))
        if os.getenv("DB_NAME"):
            self.config["database"]["name"] = os.getenv("DB_NAME")
        if os.getenv("DB_USER"):
            self.config["database"]["user"] = os.getenv("DB_USER")
        if os.getenv("DB_PASSWORD"):
            self.config["database"]["password"] = os.getenv("DB_PASSWORD")
        
        # API
        if os.getenv("API_HOST"):
            self.config["api"]["host"] = os.getenv("API_HOST")
        if os.getenv("API_PORT"):
            self.config["api"]["port"] = int(os.getenv("API_PORT"))
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key (supports nested keys with dots)."""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        return value


# Global config instance
config = Config()

