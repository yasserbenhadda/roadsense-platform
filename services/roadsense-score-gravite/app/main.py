from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

# Import des modules internes
from . import models, schemas, database, logic

app = FastAPI(
    title="RoadSense-MS — Score & Priorisation",
    description="Microservice de calcul de gravité et de priorisation des interventions routières.",
    version="1.0.0"
)

# ---------------------------------------------------------
# Initialisation de la base de données
# ---------------------------------------------------------
# Note : En prod, utilisez Alembic pour les migrations. 
# Ici, create_all crée les tables si elles n'existent pas.
models.Base.metadata.create_all(bind=database.engine)


# ---------------------------------------------------------
# Fonctions Utilitaires (Logique métier interne)
# ---------------------------------------------------------
def _update_section_score(db: Session, section_id: int):
    """
    Recalcule le score moyen et le niveau d'urgence d'un tronçon
    basé sur tous les défauts qui lui sont associés.
    """
    if not section_id:
        return

    # 1. Récupérer tous les défauts du tronçon
    defects = db.query(models.Defect).filter(models.Defect.section_id == section_id).all()
    
    if not defects:
        return

    # 2. Calculer la moyenne des scores de gravité
    scores = [d.severity_score for d in defects]
    avg_score = sum(scores) / len(scores)

    # 3. Déterminer le niveau d'urgence (Logique métier)
    # Exemple simple : >75 urgent, >40 modéré, sinon faible
    # On pourrait aussi vérifier s'il y a au moins un nid de poule critique
    urgency = schemas.UrgencyLevel.FAIBLE
    if avg_score >= 75:
        urgency = schemas.UrgencyLevel.URGENT
    elif avg_score >= 40:
        urgency = schemas.UrgencyLevel.MODERE

    # 4. Mettre à jour le tronçon
    section = db.query(models.RoadSection).filter(models.RoadSection.id == section_id).first()
    if section:
        section.avg_score = avg_score
        section.urgency_level = urgency
        db.commit()
        db.refresh(section)


# ---------------------------------------------------------
# Endpoints de l'API
# ---------------------------------------------------------

@app.post(
    "/severity/compute", 
    response_model=schemas.DefectResponse, 
    status_code=status.HTTP_201_CREATED,
    tags=["Scoring"]
)
def compute_severity(defect: schemas.DefectInput, db: Session = Depends(database.get_db)):
    """
    1. Calcule le score de gravité d'un défaut.
    2. Enregistre le défaut avec sa géométrie PostGIS.
    3. Met à jour le score global du tronçon associé.
    """
    # 1. Appel au module logic pour le calcul (Algorithme hybride)
    score = logic.calculator.calculate_deterministic(
        length=defect.length,
        width=defect.width,
        ai_confidence=defect.ai_confidence,
        defect_type=defect.defect_type
    )
    
    # 2. Création de la géométrie WKT (Well-Known Text) pour PostGIS
    # Format: POINT(longitude latitude) -> Attention à l'ordre !
    point_wkt = f"POINT({defect.longitude} {defect.latitude})"
    
    # 3. Création de l'objet DB
    db_defect = models.Defect(
        defect_type=defect.defect_type,
        length=defect.length,
        width=defect.width,
        depth=defect.depth,
        ai_confidence=defect.ai_confidence,
        severity_score=score,
        geom=point_wkt,       # Géré par GeoAlchemy2
        section_id=defect.section_id
    )
    
    try:
        db.add(db_defect)
        db.commit()
        db.refresh(db_defect)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur d'écriture en base: {str(e)}")

    # 4. Agréger les scores pour le tronçon (Mise à jour Priorisation)
    if defect.section_id:
        _update_section_score(db, defect.section_id)
    
    return db_defect


@app.get(
    "/priorisation", 
    response_model=List[schemas.RoadSectionResponse],
    tags=["Priorisation"]
)
def get_priorities(
    limit: int = 10, 
    min_score: float = 0, 
    db: Session = Depends(database.get_db)
):
    """
    Retourne la liste des tronçons routiers classés par ordre de priorité (score décroissant).
    
    - **limit**: Nombre max de tronçons à retourner (défaut 10)
    - **min_score**: Filtrer les routes en bon état (défaut 0)
    """
    results = db.query(models.RoadSection)\
        .filter(models.RoadSection.avg_score >= min_score)\
        .order_by(models.RoadSection.avg_score.desc())\
        .limit(limit)\
        .all()
        
    return results

# Endpoint de santé pour Docker/Kubernetes
@app.get("/health", tags=["System"])
def health_check():
    return {"status": "ok", "service": "RoadSense-Scoring"}