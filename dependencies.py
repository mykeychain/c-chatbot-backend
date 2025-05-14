from sqlalchemy.orm import Session
from typing import Generator

from database import SessionLocal

# Dependency to provide DB session to API endpoints
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
