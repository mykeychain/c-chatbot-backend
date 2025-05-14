import datetime
from database import SessionLocal
from models import User

def seed_one_user():
    db = SessionLocal()

    try:
        new_user = User()
        new_user.id = "1"

        if not db.query(User).first():
            db.add(new_user)
            db.commit()
            print(f"✅ Created user with id={new_user.id!r}")
        
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_one_user()
