from models import schemas
from tests.testing_database_setup import client

def test_all_users(client):
    response = client.get("/users/")
    assert response.status_code == 200
    if response.json() != []:
        schemas.UserOut(**response.json()[0])
        
    name = "hamza"
    user_name = "hamzatest"
    email = "hamzatestuser@gmail.com"
    password = "Hamza@100"
    client.post("users/", json={"name": name, "user_name": user_name, "email": email,"password": password})
    response = client.get("/users/")
    assert response.status_code == 200
    if response.json() != []:
        schemas.UserOut(**response.json()[0])

def test_create_user(client):
    name = "hamza"
    user_name = "hamzatest"
    email = "hamzatestuser@gmail.com"
    password = "Hamza@100"
    response = client.post("users/", json={"name": name, "user_name": user_name, "email": email,"password": password})
    assert response.status_code == 201
    schemas.UserOut(**response.json())
    assert response.json().get("user_name") == user_name
    assert client.post("users/", json={"name": name, "user_name": user_name, "email": email,"password": password}).status_code == 409