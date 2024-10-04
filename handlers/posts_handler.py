from fastapi import APIRouter, Depends, Form, UploadFile, Request
from models.posts_model import PostsModel
from models import schemas
from typing import List
from models.Oauth2 import verify_token
import utilities.utils as utils
from typing import Annotated

router = APIRouter(prefix="/posts", tags=["posts"])

posts_model = PostsModel()

@router.get("/", response_model=List[schemas.PostOut])
def all_posts(db : utils.db_dependency, request: Request):
    return posts_model.get_all_posts(db, request)

@router.post("/", response_model=schemas.PostOut, status_code=201)
async def create_post(db: utils.db_dependency, request: Request, title: Annotated[str, Form()], content: Annotated[str, Form()], image: Annotated[UploadFile, Form()] = None, token_data: dict = Depends(verify_token)):
    return await posts_model.create_post(db, title, content, image, token_data, request)

@router.get("/{id}", response_model=schemas.PostOut)
def get_post(db : utils.db_dependency, id: int, request: Request):
    return posts_model.get_post(db, id, request)

@router.delete("/{id}", response_model=schemas.PostOut)
def delete_post(db : utils.db_dependency, id: int, request: Request, token_data: dict = Depends(verify_token)):
    return posts_model.delete_post(db, id, token_data, request)

@router.post("/like/{id}", response_model=schemas.PostOut)
def like_post_by_post_id(db : utils.db_dependency, id: int, request: Request, token_data: dict = Depends(verify_token)):
    return posts_model.like_post(db, id, token_data, request)

@router.post("/dislike/{id}", response_model=schemas.PostOut)
def dislike_post_by_post_id(db : utils.db_dependency, id: int, request: Request, token_data: dict = Depends(verify_token)):
    return posts_model.dislike_post(db, id, token_data, request)

@router.get("/likes-list/{post_id}", response_model=List[schemas.LikesList])
def likes_list(db: utils.db_dependency, rds: utils.rds_dependency, post_id: int):
    return posts_model.post_likes_list(db, post_id, rds)

@router.get("/post-image/{image_id}")
async def get_post_image(image_id: str):
    return await posts_model.get_post_image(image_id)