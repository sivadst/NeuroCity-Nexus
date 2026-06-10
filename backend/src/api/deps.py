from sqlalchemy.orm import Session
from src.db.session import SessionLocal, get_db_session

def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
