from fastapi import APIRouter, Depends
from models.comments_model import CommentsModel
from models import schemas
from typing import List
from Oauth2 import verify_token
import utils

router = APIRouter(prefix="/comments", tags=["comments"])

comments_model = CommentsModel()

@router.post("/{id}", response_model=schemas.CommentOut, status_code=201)
def comment_on_posts(db : utils.db_dependency, id: int, comment: schemas.CreateComment, token_data: dict = Depends(verify_token)):
    return comments_model.comment_on_post(db, id, comment, token_data)

@router.get("/{id}", response_model=List[schemas.CommentOut])
def get_comment_by_post_id(db : utils.db_dependency, id: int, token_data: dict = Depends(verify_token)):
    return comments_model.get_comment_by_post_id(db, id, token_data)

@router.delete("/{id}", response_model=schemas.CommentOut)
def delete_comment_by_comment_id(db : utils.db_dependency, id: int, token_data: dict = Depends(verify_token)):
    return comments_model.delete_comment(db, id, token_data)