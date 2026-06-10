from sqlalchemy.orm import Session
from src.db.session import SessionLocal

def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()