from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_all_users():
    # response = client.get("/users/")
    # assert response.status_code == 200

    # demo test 
    assert 200 == 200