from tests.testing_database_setup import client
from tests.utils import hash_image, create_user, login_user
from io import BytesIO
from models import schemas
import pytest

TITLE = "THIS IS SOME TITLE"
CONTENT = "THIS IS SOME CONTENT"

def create_post(model, tokens=None):
    if tokens is None:
        create_user(model)
        tokens = login_user(model)
    header = {"Authorization": "Bearer " + tokens.json().get("access_token")}
    with open("test_image.png", 'rb') as f:
        file = {"image": ("test_image.png", f, "image/png")}
        payload = {"title": TITLE, "content": CONTENT}
        return model.post("posts/", data=payload, files=file, headers=header)

@pytest.mark.order(15)
def test_create_post(client):
    response = create_post(client)
    assert response.status_code == 201
    data = response.json()
    assert data.get("title") == TITLE
    assert data.get("content") == CONTENT
    
    url = response.json().get("image").split("/posts/")[-1]
    returned_img = client.get("posts/" + url)
    
    hash1 = hash_image("test_image.png")
    hash2 = hash_image(BytesIO(returned_img.content))
    
    assert hash1 == hash2
        
@pytest.mark.order(16)
def test_get_posts(client):
    response = client.get("posts/")
    assert response.status_code == 200
    assert response.json() == []

    create_post(client)
    response = client.get("posts/")
    assert response.status_code == 200
    schemas.PostOut(**(response.json()[0]))
    
@pytest.mark.order(17)
def test_get_post_by_id(client):
    response = client.get("posts/1")
    assert response.status_code == 404
    assert response.json().get("detail") == "No post found"

    create_post(client)
    response = client.get("posts/1")
    assert response.status_code == 200
    schemas.PostOut(**(response.json()))
    
@pytest.mark.order(18)
def test_delete_post(client):
    create_user(client)
    tokens = login_user(client)
    header = {"Authorization": "Bearer " + tokens.json().get("access_token")}
    response = client.delete("posts/1", headers=header)
    response.status_code == 404
    
    create_post(client, tokens=tokens)
    response = client.delete("posts/1", headers=header)
    assert response.status_code == 200
    schemas.PostOut(**(response.json()))
    
@pytest.mark.order(19)
def test_like_post(client):
    create_user(client)
    tokens = login_user(client)
    header = {"Authorization": "Bearer " + tokens.json().get("access_token")}
    response = client.post("posts/like/1", headers=header)
    assert response.status_code == 404
    
    create_post(client, tokens=tokens)
    response = client.post("posts/like/1", headers=header)
    assert response.status_code == 200
    schemas.PostOut(**(response.json()))
    assert response.json().get("likes") == 1
    
@pytest.mark.order(20)
def test_dislike_post(client):
    create_user(client)
    tokens = login_user(client)
    header = {"Authorization": "Bearer " + tokens.json().get("access_token")}
    response = client.post("posts/dislike/1", headers=header)
    assert response.status_code == 404
    
    create_post(client, tokens=tokens)
    response = client.post("posts/like/1", headers=header)
    assert response.json().get("likes") == 1
    response = client.post("posts/dislike/1", headers=header)
    assert response.status_code == 200
    schemas.PostOut(**(response.json()))
    assert response.json().get("likes") == 0
    
def test_likes_list(client):
    response = client.get("posts/likes-list/1")
    assert response.status_code == 200
    assert response.json() == []
    
    create_user(client)
    tokens = login_user(client)
    header = {"Authorization": "Bearer " + tokens.json().get("access_token")}
    create_post(client, tokens=tokens)
    response = client.post("posts/like/1", headers=header)
    response = client.get("posts/likes-list/1")
    assert response.status_code == 200
    schemas.LikesList(**(response.json()[0]))
    
    
    
