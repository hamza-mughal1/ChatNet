from fastapi import APIRouter, Depends
from models.comments_model import CommentsModel
from models import schemas
from typing import Annotated, List
from models.Oauth2 import verify_token
from utilities.api_limiter import ApiLimitDependency
import utilities.utils as utils

router = APIRouter(prefix="/comments", tags=["comments"])
api_limit_for_comments_resource = ApiLimitDependency(
    req_count=utils.ApiLimitMode.PANDA.value
)

comments_model = CommentsModel()


@router.post("/{id}", response_model=schemas.CommentOut, status_code=201)
def comment_on_posts(
    db: utils.db_dependency,
    id: int,
    comment: schemas.CreateComment,
    limit: Annotated[ApiLimitDependency, Depends(api_limit_for_comments_resource)],
    token_data: dict = Depends(verify_token),
):
    return comments_model.comment_on_post(db, id, comment, token_data)


@router.get("/{id}", response_model=List[schemas.CommentOut])
def get_comment_by_post_id(
    db: utils.db_dependency,
    id: int,
    rds: utils.rds_dependency,
    limit: Annotated[ApiLimitDependency, Depends(api_limit_for_comments_resource)],
    page: int = 1,
):
    if page < 1:
        page = 1
    return comments_model.get_comment_by_post_id(db, id, page=page, rds=rds)


@router.delete("/{id}", response_model=schemas.CommentOut)
def delete_comment_by_comment_id(
    db: utils.db_dependency,
    id: int,
    limit: Annotated[ApiLimitDependency, Depends(api_limit_for_comments_resource)],
    token_data: dict = Depends(verify_token),
):
    return comments_model.delete_comment(db, id, token_data)


@router.get("/by-user/", response_model=List[schemas.CommentOut])
def get_comment_by_user_id(
    db: utils.db_dependency,
    limit: Annotated[ApiLimitDependency, Depends(api_limit_for_comments_resource)],
    page: int = 1,
    token_data: dict = Depends(verify_token),
):
    if page < 1:
        page = 1
    return comments_model.get_comment_by_user_id(db, token_data, page=page)


@router.get("/by-comment-id/{id}", response_model=schemas.CommentOut)
def comment_by_comment_id(
    db: utils.db_dependency,
    id: int,
    limit: Annotated[ApiLimitDependency, Depends(api_limit_for_comments_resource)],
):
    return comments_model.get_by_comment_id(db, id)
