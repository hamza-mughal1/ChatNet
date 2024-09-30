from tests.utils import create_user, login_user, create_post, COMMENT_CONTENT
from tests.testing_database_setup import client
from models import schemas
import pytest

def create_comment(model):
    create_user(model)
    tokens = login_user(model)
    header = {"Authorization": "Bearer " + tokens.json().get("access_token")}
    create_post(model, tokens=tokens)
    return model.post("comments/1", json={"content": COMMENT_CONTENT}, headers=header), header

@pytest.mark.order(25)
def test_create_comment(client):
    response = create_comment(client)[0]
    assert response.status_code == 201
    schemas.CommentOut(**response.json())
    assert response.json().get("content") == COMMENT_CONTENT
    
@pytest.mark.order(26)
def test_get_comment(client):
    header = create_comment(client)[1]
    response = client.get("comments/1", headers=header)
    assert response.status_code == 200
    schemas.CommentOut(**(response.json()[0]))
    
@pytest.mark.order(27)
def test_delete_comment(client):
    header = create_comment(client)[1]
    response = client.get("comments/1", headers=header)
    assert response.status_code == 200
    schemas.CommentOut(**(response.json()[0]))
    client.delete("comments/1", headers=header)
    response = client.get("comments/1", headers=header)
    assert response.status_code == 200
    assert response.json() == []
    
    
@pytest.mark.order(28)
def test_get_comment_by_user(client):
    header = create_comment(client)[1]
    response = client.get("comments/by-user/", headers=header)
    assert response.status_code == 200
    schemas.CommentOut(**(response.json()[0]))
    
@pytest.mark.order(29)
def test_get_comment_by_id(client):
    response = client.get("comments/by-comment-id/1")
    assert response.status_code == 404
    create_comment(client)
    response = client.get("comments/by-comment-id/1")
    assert response.status_code == 200
    schemas.CommentOut(**(response.json()))