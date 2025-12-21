#!/bin/bash
set -e

echo "Starting Crack Detection API..."

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL..."
until python -c "import psycopg2; psycopg2.connect(host='${DB_HOST}', port=${DB_PORT}, user='${DB_USER}', password='${DB_PASSWORD}', dbname='${DB_NAME}')" 2>/dev/null; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done

echo "PostgreSQL is ready!"

# Initialize database
echo "Initializing database..."
python scripts/init_database.py || echo "Database initialization failed or already exists"

# Start the API
echo "Starting API server..."
exec uvicorn app.api.main:app --host 0.0.0.0 --port 8000

