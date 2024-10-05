from fastapi.testclient import TestClient
import pytest
from app import app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from utilities.settings import setting
from models.database_orm import get_db, Base
import redis
from models.redis_setup import get_rds

def override_get_rds():
    rds = redis.Redis(host=setting.redis_host, port=setting.redis_port, db=1)
    try:
        rds.flushall()
        yield rds
    finally:
        rds.close()
        
SQLALCHEMY_DATABASE_URL = f"{setting.db}://{setting.db_username}:{setting.db_password}@{setting.db_host}:{setting.test_db_port}/{setting.db_name}_test"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

@pytest.fixture
def client():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield TestClient(app)

TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_rds] = override_get_rds
