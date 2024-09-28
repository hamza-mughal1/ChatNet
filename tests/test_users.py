from models import schemas
from tests.testing_database_setup import client
from enum import Enum
from jose import jwt
from models import Oauth2
import time
import hashlib
from PIL import Image
from io import BytesIO

def hash_image(image_path):
    img = Image.open(image_path)
    img = img.convert("RGB")  # Convert to RGB if not already
    img = img.resize((8, 8))  # Resize to 8x8 for hashing
    img_data = img.getdata()
    hash_str = ''.join(['1' if r > 128 else '0' for r, g, b in img_data])
    return hashlib.md5(hash_str.encode()).hexdigest()

class UserData(Enum):
    name = "hamza"
    user_name = "hamzatest"
    email = "hamzatestuser@gmail.com"
    password = "Hamza@100"
    
def create_user(model):
    return model.post("users/", json={"name": UserData.name.value, "user_name": UserData.user_name.value, "email": UserData.email.value,"password": UserData.password.value})

def login_user(model):
    return model.post("/login", data={"username": UserData.email.value, "password": UserData.password.value})

def test_create_user(client):
    response = create_user(client)
    assert response.status_code == 201
    schemas.UserOut(**response.json())
    assert response.json().get("user_name") == UserData.user_name.value
    assert create_user(client).status_code == 409

def test_all_users(client):
    response = client.get("/users/")
    assert response.status_code == 200
    assert response.json() == []
        
    create_user(client)
    response = client.get("/users/")
    assert response.status_code == 200
    schemas.UserOut(**response.json()[0])

    
def test_get_user(client):
    response = client.get("users/1")
    assert response.status_code == 404
    assert response.json().get('detail') == "user not found"
    
    
    create_user(client)
    response = client.get("users/1")
    assert response.status_code == 200
    schemas.UserOut(**response.json())
    
def test_login_user(client):
    response = login_user(client)
    assert response.status_code == 403
    
    create_user(client)
    response = login_user(client)
    assert response.status_code == 200
    data = jwt.decode(response.json().get("access_token"), Oauth2.SECRET_KEY, algorithms=Oauth2.ALGORITHM)
    assert data.get("user_name") == UserData.user_name.value
    
def test_update_user(client):
    create_user(client)
    tokens = login_user(client)
    header = {"Authorization": "Bearer " + tokens.json().get("access_token")}
    response = client.put("users/", json={"name": UserData.name.value + "test", "bio": "testbio", "user_name": UserData.user_name.value + "test", "email": "test" + UserData.email.value}, headers=header) 
    assert response.status_code == 200
    assert response.json().get("name") == UserData.name.value + "test"
    assert response.json().get("user_name") == UserData.user_name.value + "test"
    assert response.json().get("bio") == "testbio"
    
def test_delete_user(client):
    create_user(client)
    tokens = login_user(client)
    header = {"Authorization": "Bearer " + tokens.json().get("access_token")}
    response = client.delete("users/", headers=header) 
    assert response.status_code == 200
    schemas.UserOut(**response.json())
    response = client.delete("users/", headers=header) 
    assert response.status_code == 403

def test_patch_user(client):
    create_user(client)
    tokens = login_user(client)
    header = {"Authorization": "Bearer " + tokens.json().get("access_token")}
    response = client.patch("users/", json={"name": UserData.name.value + "test", "bio": "testbio", "user_name": UserData.user_name.value + "test", "email": "test" + UserData.email.value}, headers=header) 
    assert response.status_code == 200
    assert response.json().get("name") == UserData.name.value + "test"
    assert response.json().get("user_name") == UserData.user_name.value + "test"
    assert response.json().get("bio") == "testbio"
    
def test_search_user(client):
    response = client.get("users/search/" + UserData.user_name.value)
    assert response.status_code == 404
    
    create_user(client)
    response = client.get("users/search/" + UserData.user_name.value)
    assert response.status_code == 200
    schemas.UserOut(**response.json())
    
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
    assert response.json().get("following") == 1
    
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
    assert response.json().get("following") == 1
    response = client.post(f"users/unfollow/{id}", headers=header)
    assert response.status_code == 200
    assert response.json().get("following") == 0
    
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
    
def test_change_password(client):
    create_user(client)
    tokens = login_user(client)
    header = {"Authorization": "Bearer " + tokens.json().get("access_token")}
    response = client.patch("users/change-password/", json={"email": UserData.email.value, "password": UserData.password.value, "new_password": UserData.password.value + "1"}, headers=header)
    
    assert response.status_code == 200
    schemas.UserOut(**response.json())
    
    time.sleep(1) # to avoid generating same JWT (if the same information passed in two JWT then they both will be same) that's why it will change the exp time
    # by waiting for 1 sec
    
    assert client.post("/login", data={"username": UserData.email.value, "password": UserData.password.value + "1"}).status_code == 200
    
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