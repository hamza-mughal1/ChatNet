from models import schemas
from tests.testing_database_setup import client
from jose import jwt
from models import Oauth2
from io import BytesIO
import pytest
from tests.utils import hash_image, UserData, create_user, login_user

@pytest.mark.order(1)
def test_create_user(client):
    response = create_user(client)
    assert response.status_code == 201
    schemas.UserOut(**response.json())
    assert response.json().get("user_name") == UserData.user_name.value
    assert create_user(client).status_code == 409

@pytest.mark.order(2)
def test_all_users(client):
    response = client.get("/users/")
    assert response.status_code == 200
    assert response.json() == []
        
    create_user(client)
    response = client.get("/users/")
    assert response.status_code == 200
    schemas.UserOut(**response.json()[0])
    
@pytest.mark.order(3)
def test_get_user(client):
    response = client.get("users/1")
    assert response.status_code == 404
    assert response.json().get('detail') == "user not found"
    
    
    create_user(client)
    response = client.get("users/1")
    assert response.status_code == 200
    schemas.UserOut(**response.json())
    
@pytest.mark.order(4)
def test_login_user(client):
    response = login_user(client)
    assert response.status_code == 403
    
    create_user(client)
    response = login_user(client)
    assert response.status_code == 200
    data = jwt.decode(response.json().get("access_token"), Oauth2.SECRET_KEY, algorithms=Oauth2.ALGORITHM)
    assert data.get("user_name") == UserData.user_name.value
    
@pytest.mark.order(5)
def test_update_user(client):
    create_user(client)
    tokens = login_user(client)
    header = {"Authorization": "Bearer " + tokens.json().get("access_token")}
    response = client.put("users/", json={"name": UserData.name.value + "test", "bio": "testbio", "user_name": UserData.user_name.value + "test", "email": "test" + UserData.email.value}, headers=header) 
    assert response.status_code == 200
    assert response.json().get("name") == UserData.name.value + "test"
    assert response.json().get("user_name") == UserData.user_name.value + "test"
    assert response.json().get("bio") == "testbio"
    
@pytest.mark.order(6)
def test_logout_user(client):
    create_user(client)
    tokens = login_user(client)
    header_logout = {"Authorization": "Bearer " + tokens.json().get("access_token"), "Refresh-token": tokens.json().get("refresh_token")}
    header = {"Authorization": "Bearer " + tokens.json().get("access_token")}
    response = client.put("users/", json={"name": UserData.name.value + "test", "bio": "testbio", "user_name": UserData.user_name.value + "test", "email": "test" + UserData.email.value}, headers=header) 
    assert response.status_code == 200
    client.post("logout", headers=header_logout)
    response = client.put("users/", json={"name": UserData.name.value + "test", "bio": "testbio", "user_name": UserData.user_name.value + "test", "email": "test" + UserData.email.value}, headers=header)
    assert response.status_code == 403
    
@pytest.mark.order(7)
def test_logout_all_user(client):
    create_user(client)
    tokens = login_user(client)

    tokens2 = login_user(client)
    header_logout = {"Authorization": "Bearer " + tokens.json().get("access_token"), "Refresh-token": tokens.json().get("refresh_token")}
    header = {"Authorization": "Bearer " + tokens.json().get("access_token")}
    header2 = {"Authorization": "Bearer " + tokens2.json().get("access_token")}
    
    client.post("logout-all", headers=header_logout)
    response = client.put("users/", json={"name": UserData.name.value + "test", "bio": "testbio", "user_name": UserData.user_name.value + "test", "email": "test" + UserData.email.value}, headers=header)
    assert response.status_code == 403
    
    response = client.put("users/", json={"name": UserData.name.value + "test", "bio": "testbio", "user_name": UserData.user_name.value + "test", "email": "test" + UserData.email.value}, headers=header2)
    assert response.status_code == 403
    
    response = client.put("users/", json={"name": UserData.name.value + "test", "bio": "testbio", "user_name": UserData.user_name.value + "test", "email": "test" + UserData.email.value}, headers=header)
    assert response.status_code == 403
    
@pytest.mark.order(8)
def test_delete_user(client):
    create_user(client)
    tokens = login_user(client)
    header = {"Authorization": "Bearer " + tokens.json().get("access_token")}
    response = client.delete("users/", headers=header) 
    assert response.status_code == 200
    schemas.UserOut(**response.json())
    response = client.delete("users/", headers=header) 
    assert response.status_code == 403

@pytest.mark.order(9)
def test_patch_user(client):
    create_user(client)
    tokens = login_user(client)
    header = {"Authorization": "Bearer " + tokens.json().get("access_token")}
    response = client.patch("users/", json={"name": UserData.name.value + "test", "bio": "testbio", "user_name": UserData.user_name.value + "test", "email": "test" + UserData.email.value}, headers=header) 
    assert response.status_code == 200
    assert response.json().get("name") == UserData.name.value + "test"
    assert response.json().get("user_name") == UserData.user_name.value + "test"
    assert response.json().get("bio") == "testbio"
    
@pytest.mark.order(10)
def test_search_user(client):
    response = client.get("users/search/" + UserData.user_name.value)
    assert response.status_code == 200
    assert response.json() == []
    
    create_user(client)
    response = client.get("users/search/" + UserData.user_name.value[:-3])
    assert response.status_code == 200
    schemas.UserOut(**(response.json()[0]))
    assert response.json()[0].get("user_name") == UserData.user_name.value
    
@pytest.mark.order(11)
def test_follow_user(client):
    create_user(client)
    tokens = login_user(client)
    header = {"Authorization": "Bearer " + tokens.json().get("access_token")}
    response = client.post("users/follow/1", headers=header)
    assert response.status_code == 400
    response = client.post("users/follow/9999", headers=header)
    assert response.status_code == 404
    
    user = client.post("users/", json={"name": UserData.name.value, "user_name": UserData.user_name.value + "test", "email": "test" + UserData.email.value,"password": UserData.password.value})
    id = user.json().get("id")
    response = client.post(f"users/follow/{id}", headers=header)
    assert response.status_code == 200
    assert response.json().get("followers") == 1
    
@pytest.mark.order(12)
def test_unfollow_user(client):
    create_user(client)
    tokens = login_user(client)
    header = {"Authorization": "Bearer " + tokens.json().get("access_token")}
    response = client.post("users/unfollow/1", headers=header)
    assert response.status_code == 400
    response = client.post("users/unfollow/9999", headers=header)
    assert response.status_code == 404
    
    user = client.post("users/", json={"name": UserData.name.value, "user_name": UserData.user_name.value + "test", "email": "test" + UserData.email.value,"password": UserData.password.value})
    id = user.json().get("id")
    response = client.post(f"users/follow/{id}", headers=header)
    assert response.json().get("followers") == 1
    response = client.post(f"users/unfollow/{id}", headers=header)
    assert response.status_code == 200
    assert response.json().get("followers") == 0
    
@pytest.mark.order(13)
def test_following_list(client):
    response = client.get("users/following-list/1")
    assert response.status_code == 200
    assert response.json() == []
    
    create_user(client)
    tokens = login_user(client)
    header = {"Authorization": "Bearer " + tokens.json().get("access_token")}
    user = client.post("users/", json={"name": UserData.name.value, "user_name": UserData.user_name.value + "test", "email": "test" + UserData.email.value,"password": UserData.password.value})
    id = user.json().get("id")
    response = client.post(f"users/follow/{id}", headers=header)
    
    response = client.get("users/following-list/1")
    assert response.status_code == 200
    schemas.FollowList(**(response.json()[0]))
    
@pytest.mark.order(14)
def test_follower_list(client):
    response = client.get("users/follower-list/2")
    assert response.status_code == 200
    assert response.json() == []
    
    create_user(client)
    tokens = login_user(client)
    header = {"Authorization": "Bearer " + tokens.json().get("access_token")}
    user = client.post("users/", json={"name": UserData.name.value, "user_name": UserData.user_name.value + "test", "email": "test" + UserData.email.value,"password": UserData.password.value})
    id = user.json().get("id")
    response = client.post(f"users/follow/{id}", headers=header)
    
    response = client.get("users/follower-list/2")
    assert response.status_code == 200
    schemas.FollowList(**(response.json()[0]))
    
@pytest.mark.order(15)
def test_change_password(client):
    create_user(client)
    tokens = login_user(client)
    header = {"Authorization": "Bearer " + tokens.json().get("access_token")}
    response = client.patch("users/change-password/", json={"email": UserData.email.value, "password": UserData.password.value, "new_password": UserData.password.value + "1"}, headers=header)
    
    assert response.status_code == 200
    schemas.UserOut(**response.json())
    
    assert client.post("/login", data={"username": UserData.email.value, "password": UserData.password.value + "1"}).status_code == 200

@pytest.mark.order(16)
def test_image_upload(client):
    create_user(client)
    tokens = login_user(client)
    header = {"Authorization": "Bearer " + tokens.json().get("access_token")}
    with open("test_image.png", 'rb') as f:
        img_data = f.read()
        files = {"file": ("test_image.png", img_data)}
        response = client.post("users/upload-profile-picture/", files=files, headers=header)
        assert response.status_code == 200
        url = response.json().get("profile_pic").split("/users/")[-1]
        returned_img = client.get("users/" + url)
        
        hash1 = hash_image("test_image.png")
        hash2 = hash_image(BytesIO(returned_img.content))
        
        assert hash1 == hash2