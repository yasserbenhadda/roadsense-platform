from core.db import engine, Base
from core import models

print("Création des tables...")
Base.metadata.create_all(bind=engine)
print("Terminé.")
