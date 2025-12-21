# seed_data.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, RoadSection
from app.schemas import UrgencyLevel

# Doit correspondre à ton docker-compose (localhost car on lance ce script depuis ta machine)
DATABASE_URL = "postgresql://user:password@localhost:5432/roadsense_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    session = SessionLocal()
    
    # Vérifier si des données existent déjà
    if session.query(RoadSection).count() > 0:
        print("La base contient déjà des tronçons.")
        return

    print("Création des tronçons de test...")
    
    # Création de 3 tronçons fictifs
    # Note: On utilise une géométrie simple (Ligne droite)
    section1 = RoadSection(
        name="Route Nationale 1 - Km 10-12",
        avg_score=0,
        urgency_level=UrgencyLevel.FAIBLE,
        # WKT pour une ligne (Format PostGIS)
        geom="LINESTRING(-7.6 33.5, -7.61 33.51)" 
    )
    
    section2 = RoadSection(
        name="Boulevard Mohammed V",
        avg_score=0,
        urgency_level=UrgencyLevel.FAIBLE,
        geom="LINESTRING(-7.5 33.5, -7.55 33.55)"
    )

    session.add(section1)
    session.add(section2)
    session.commit()
    
    print(f"Tronçons créés avec succès ! IDs: {section1.id}, {section2.id}")
    session.close()

if __name__ == "__main__":
    init_db()