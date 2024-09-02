from fastapi import APIRouter, Depends
from models import db_models
from models.posts_model import PostsModel
from models import schemas
from typing import List
from Oauth2 import verify_token
import utils

router = APIRouter(prefix="/posts", tags=["posts"])

posts_model = PostsModel()

@router.get("/", response_model=List[schemas.PostOut])
def all_posts(db : utils.db_dependency, token_data: dict = Depends(verify_token)):
    return posts_model.get_all_posts(db, token_data)

@router.post("/", response_model=schemas.PostOut)
def create_post(db: utils.db_dependency, post_data: schemas.CreatePost, token_data: dict = Depends(verify_token)):
    return posts_model.create_post(db, post_data, token_data)

@router.get("/{id}", response_model=schemas.PostOut)
def get_post(db : utils.db_dependency, id: int, token_data: dict = Depends(verify_token)):
    return posts_model.get_post(db, id)