from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from utilities.settings import setting

SQLALCHEMY_DATABASE_URL = f"{setting.db}://{setting.db_username}:{setting.db_password}@{setting.db_host}/{setting.db_name}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()