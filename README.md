# RoadSense Platform (Monorepo)

## Prérequis
- Docker Desktop (avec Docker Compose)
- Git

## Lancement
```bash
docker compose up --build
```

## Accès
- MinIO Console: http://localhost:9001
- Ingestion: http://localhost:8001
- Detection: http://localhost:8002/docs
- GeoRef: http://localhost:8003/docs
- Score: http://localhost:8004/docs
- Dashboard: http://localhost:8080

## Arrêt
```bash
docker compose down
```

## Nettoyage volumes
```bash
docker compose down -v
```
