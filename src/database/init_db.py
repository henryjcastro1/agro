from src.database.db import Base, engine
from src.core.models import Rad, Sample

print("Creando tablas...")
Base.metadata.create_all(bind=engine)
print("Listo.")
