#!/usr/bin/env python3
"""Script to initialize PostgreSQL database tables."""
import sys
from pathlib import Path


project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import argparse
from app.utils.database import Base, Database
from app.utils.config_loader import config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_database(drop_existing: bool = False):
    """Initialize database tables.
    
    Args:
        drop_existing: If True, drop existing tables before creating
    """
    db_host = config.get("database.host", "localhost")
    db_port = config.get("database.port", 5432)
    db_name = config.get("database.name", "crack_detection")
    db_user = config.get("database.user", "postgres")
    db_password = config.get("database.password", "postgres")
    
    from sqlalchemy import create_engine
    
    database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    
    try:
        logger.info(f"Connecting to database: {db_host}:{db_port}/{db_name}")
        engine = create_engine(database_url)
        
        if drop_existing:
            logger.warning("Dropping existing tables...")
            Base.metadata.drop_all(bind=engine)
        
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        
        logger.info("Database initialized successfully!")
        
        # Verify by creating a database instance
        db = Database()
        if db.session is not None:
            logger.info("Database connection verified!")
            db.session.close()
        else:
            logger.warning("Database connection could not be verified")
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


def main():
    parser = argparse.ArgumentParser(description="Initialize PostgreSQL database")
    parser.add_argument("--drop", action="store_true",
                       help="Drop existing tables before creating (WARNING: This will delete all data)")
    
    args = parser.parse_args()
    
    print("Initialisation de la base de donnees PostgreSQL")
    print("=" * 50)
    print("")
    
    if args.drop:
        response = input("ATTENTION: Cela va supprimer toutes les donnees existantes. Continuer? (yes/no): ")
        if response.lower() != "yes":
            print("Operation annulee")
            return 1
    
    return init_database(drop_existing=args.drop)


if __name__ == "__main__":
    exit(main())

