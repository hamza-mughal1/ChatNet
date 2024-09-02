from fastapi import APIRouter, Depends
from models.database_orm import get_db
from sqlalchemy.orm import Session
from models.posts_model import PostsModel
from models import schemas
from typing import List
from Oauth2 import verify_token
router = APIRouter(prefix="/posts", tags=["posts"])

posts_model = PostsModel()

@router.get("/", response_model=List[schemas.PostOut])
def all_posts(db : Session =  Depends(get_db), token_data: dict = Depends(verify_token)):
    return posts_model.get_all_posts(db, token_data)
