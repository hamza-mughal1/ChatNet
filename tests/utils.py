from enum import Enum
import hashlib
from PIL import Image

TITLE = "THIS IS SOME TITLE"
CONTENT = "THIS IS SOME CONTENT"

class UserData(Enum):
    name = "hamza"
    user_name = "hamzatest"
    email = "hamzatestuser@gmail.com"
    password = "Hamza@100"

def hash_image(image_path):
    img = Image.open(image_path)
    img = img.convert("RGB")  # Convert to RGB if not already
    img = img.resize((8, 8))  # Resize to 8x8 for hashing
    img_data = img.getdata()
    hash_str = ''.join(['1' if r > 128 else '0' for r, g, b in img_data])
    return hashlib.md5(hash_str.encode()).hexdigest()

def create_user(model):
    return model.post("users/", json={"name": UserData.name.value, "user_name": UserData.user_name.value, "email": UserData.email.value,"password": UserData.password.value})

def login_user(model):
    return model.post("/login", data={"username": UserData.email.value, "password": UserData.password.value})

def create_post(model, tokens=None):
    if tokens is None:
        create_user(model)
        tokens = login_user(model)
    header = {"Authorization": "Bearer " + tokens.json().get("access_token")}
    with open("test_image.png", 'rb') as f:
        file = {"image": ("test_image.png", f, "image/png")}
        payload = {"title": TITLE, "content": CONTENT}
        return model.post("posts/", data=payload, files=file, headers=header)