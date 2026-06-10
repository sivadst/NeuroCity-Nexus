from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.core.config import get_settings

settings = get_settings()

# Convert async URL to sync URL for SQLite
db_url = settings.database_url.replace("sqlite+aiosqlite", "sqlite")

engine = create_engine(
    db_url,
    connect_args={"check_same_thread": False} if db_url.startswith("sqlite") else {},
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)