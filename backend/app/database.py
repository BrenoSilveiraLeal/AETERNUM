from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import settings

active_database_url = settings.postgres_url or settings.database_url
connect_args = {"check_same_thread": False} if active_database_url.startswith("sqlite") else {}
engine = create_engine(active_database_url, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
