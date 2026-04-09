# models.py

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from db import Base
from datetime import datetime

class Rad(Base):
    __tablename__ = "rads"

    id = Column(Integer, primary_key=True, index=True)
    rad_code = Column(String)
    cliente = Column(String)
    fecha = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    samples = relationship("Sample", back_populates="rad")


class Sample(Base):
    __tablename__ = "samples"

    id = Column(Integer, primary_key=True, index=True)
    rad_id = Column(Integer, ForeignKey("rads.id"))
    code = Column(String)

    n_ureico = Column(Float)
    celulas = Column(Integer)

    # CAMPOS QUE NECESITAN CEROS EXACTOS
    grasa = Column(String)
    lactosa = Column(String)
    p_crioscopico = Column(String)
    proteina = Column(String)
    solidos = Column(String)

    mesofilas = Column(Integer)
    recomendaciones = Column(String)

    rad = relationship("Rad", back_populates="samples")
