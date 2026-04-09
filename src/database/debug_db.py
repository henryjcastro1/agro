from src.database.db import SessionLocal
from src.core.models import Rad, Sample

db = SessionLocal()

print("RADS:", db.query(Rad).count())
print("SAMPLES:", db.query(Sample).count())

for rad in db.query(Rad).all():
    print("RAD:", rad.rad_code)
    for s in rad.samples:
        print("   Sample:", s.code, s.grasa, s.lactosa, s.solidos)
