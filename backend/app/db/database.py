import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# PostgreSQL URL from environment (e.g., in Docker Compose) or local SQLite fallback
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./railplan.db")

# For SQLite, ensure check_same_thread=False
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    from . import models  # Ensure all models are registered
    Base.metadata.create_all(bind=engine)
