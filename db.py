from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

engine = create_engine("sqlite:///data/analisis.db", future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False)
Base = declarative_base()
