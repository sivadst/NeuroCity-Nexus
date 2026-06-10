from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Adjust this import to match your actual config location
try:
    from src.core.config import get_settings
    settings = get_settings()
    db_url = settings.database_url.replace("sqlite+aiosqlite", "sqlite")
except ImportError:
    # Fallback if config doesn't exist yet
    db_url = "sqlite:///./neurocity.db"

engine = create_engine(
    db_url,
    connect_args={"check_same_thread": False} if db_url.startswith("sqlite") else {},
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)