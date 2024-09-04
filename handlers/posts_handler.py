from fastapi import APIRouter, Depends
from models.posts_model import PostsModel
from models import schemas
from typing import List
from Oauth2 import verify_token
import utils

router = APIRouter(prefix="/posts", tags=["posts"])

posts_model = PostsModel()

@router.get("/", response_model=List[schemas.PostOut])
def all_posts(db : utils.db_dependency):
    return posts_model.get_all_posts(db)

@router.post("/", response_model=schemas.PostOut, status_code=201)
def create_post(db: utils.db_dependency, post_data: schemas.CreatePost, token_data: dict = Depends(verify_token)):
    return posts_model.create_post(db, post_data, token_data)

@router.get("/{id}", response_model=schemas.PostOut)
def get_post(db : utils.db_dependency, id: int):
    return posts_model.get_post(db, id)

@router.delete("/{id}", response_model=schemas.PostOut)
def delete_post(db : utils.db_dependency, id: int, token_data: dict = Depends(verify_token)):
    return posts_model.delete_post(db, id, token_data)

@router.post("/like/{id}", response_model=schemas.PostOut)
def like_post_by_post_id(db : utils.db_dependency, id: int, token_data: dict = Depends(verify_token)):
    return posts_model.like_post(db, id, token_data)

@router.post("/dislike/{id}", response_model=schemas.PostOut)
def dislike_post_by_post_id(db : utils.db_dependency, id: int, token_data: dict = Depends(verify_token)):
    return posts_model.dislike_post(db, id, token_data)

