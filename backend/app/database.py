from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database SQLite lokal (akan otomatis membuat file lms.db)
SQLALCHEMY_DATABASE_URL = "sqlite:///./lms.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency untuk mendapatkan session database di API
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()