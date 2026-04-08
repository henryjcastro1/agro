from db import Base, engine
from models import Rad, Sample

print("Creando tablas...")
Base.metadata.create_all(bind=engine)
print("Listo.")
