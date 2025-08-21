from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from ..core.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def init_db() -> None:
    # Ensure pgvector extension exists (ignore if already created)
    try:
        with engine.connect() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            conn.commit()
    except Exception:
        # Safe fail: user may not be superuser; skip silently
        pass
    # Import models to register metadata
    from ..models import customer, interaction, churn, document
    Base.metadata.create_all(bind=engine)


# Dependency for routes

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
