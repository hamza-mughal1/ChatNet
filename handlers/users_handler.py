from fastapi import APIRouter, Depends, UploadFile, Request
from models.users_model import UsersModel
from models import schemas
from typing import Annotated, List
from models.Oauth2 import verify_token
from utilities.utils import (
    db_dependency,
    rds_dependency,
    ApiLimitMode,
    OTP_verification,
)
from utilities.api_limiter import ApiLimitDependency

router = APIRouter(prefix="/users", tags=["users"])

users_model = UsersModel()
api_limit_for_users_resource = ApiLimitDependency(req_count=ApiLimitMode.PANDA.value)


get_users_api_limit = ApiLimitDependency(req_count=ApiLimitMode.TURTLE.value)


@router.get("/", response_model=List[schemas.UserOut])
def all_users(
    db: db_dependency,
    request: Request,
    rds: rds_dependency,
    limit: Annotated[ApiLimitDependency, Depends(get_users_api_limit)],
    page: int = 1,
):
    if page < 1:
        page = 1
    return users_model.get_all_users(db, request, rds=rds, page=page)


if OTP_verification["var"]:
    create_user_api_limit = ApiLimitDependency(req_count=ApiLimitMode.TURTLE.value)

    @router.post("/", status_code=201)
    def create_user(
        user: schemas.CreateUser,
        db: db_dependency,
        rds: rds_dependency,
        limit: Annotated[ApiLimitDependency, Depends(create_user_api_limit)],
    ):
        return users_model.create_user(user, db, rds=rds)

else:
    create_user_api_limit = ApiLimitDependency(req_count=ApiLimitMode.TURTLE.value)

    @router.post("/", response_model=schemas.UserOut, status_code=201)
    def create_user(
        user: schemas.CreateUser,
        db: db_dependency,
        request: Request,
        limit: Annotated[ApiLimitDependency, Depends(create_user_api_limit)],
    ):
        return users_model.create_user_without_otp(user, db, request)


@router.get("/{id}", response_model=schemas.UserOut)
def get_user(
    db: db_dependency,
    id: int,
    request: Request,
    rds: rds_dependency,
    limit: Annotated[ApiLimitDependency, Depends(api_limit_for_users_resource)],
):
    return users_model.get_user(db, id, request, rds)


@router.put("/", response_model=schemas.UserOut)
def update_user(
    db: db_dependency,
    user_data: schemas.UpdateUser,
    request: Request,
    rds: rds_dependency,
    limit: Annotated[ApiLimitDependency, Depends(api_limit_for_users_resource)],
    token_data: dict = Depends(verify_token),
):
    return users_model.update_user(db, user_data, token_data, request, rds)


@router.delete("/", response_model=schemas.UserOut)
def delete_user(
    db: db_dependency,
    request: Request,
    rds: rds_dependency,
    limit: Annotated[ApiLimitDependency, Depends(api_limit_for_users_resource)],
    token_data: dict = Depends(verify_token),
):
    return users_model.delete_user(db, token_data, request, rds)


@router.patch("/", response_model=schemas.UserOut)
def patch_user(
    db: db_dependency,
    user_data: schemas.UpdateUserPatch,
    request: Request,
    rds: rds_dependency,
    limit: Annotated[ApiLimitDependency, Depends(api_limit_for_users_resource)],
    token_data: dict = Depends(verify_token),
):
    return users_model.patch_user(db, user_data, token_data, request, rds)


@router.get("/search/{user_name}", response_model=List[schemas.SearchUsers])
def search_user_by_user_name(db: db_dependency, user_name: str, request: Request):
    return users_model.search_by_user_name(db, user_name, request)


@router.post("/follow/{user_id}", response_model=schemas.UserOut)
def follow_user(
    db: db_dependency,
    user_id: int,
    request: Request,
    rds: rds_dependency,
    limit: Annotated[ApiLimitDependency, Depends(api_limit_for_users_resource)],
    token_data: dict = Depends(verify_token),
):
    return users_model.follow_user(db, user_id, token_data, request, rds)


@router.post("/unfollow/{user_id}", response_model=schemas.UserOut)
def unfollow_user(
    db: db_dependency,
    user_id: int,
    request: Request,
    rds: rds_dependency,
    limit: Annotated[ApiLimitDependency, Depends(api_limit_for_users_resource)],
    token_data: dict = Depends(verify_token),
):
    return users_model.unfollow_user(db, user_id, token_data, request, rds)


@router.get("/following-list/{user_id}", response_model=List[schemas.FollowList])
def following_list(
    db: db_dependency,
    user_id: int,
    limit: Annotated[ApiLimitDependency, Depends(api_limit_for_users_resource)],
    page: int = 1,
):
    if page < 1:
        page = 1
    return users_model.following_list(db, user_id, page=page)


@router.get("/follower-list/{user_id}", response_model=List[schemas.FollowList])
def follower_list(
    db: db_dependency,
    user_id: int,
    limit: Annotated[ApiLimitDependency, Depends(api_limit_for_users_resource)],
    page: int = 1,
):
    if page < 1:
        page = 1
    return users_model.follower_list(db, user_id, page=page)


@router.patch("/change-password/", response_model=schemas.UserOut)
def change_password(
    db: db_dependency,
    details: schemas.ChangePassword,
    request: Request,
    rds: rds_dependency,
    limit: Annotated[ApiLimitDependency, Depends(api_limit_for_users_resource)],
    token_data: dict = Depends(verify_token),
):
    return users_model.change_password(db, details, token_data, request, rds)


@router.get("/likes-list/", response_model=List[schemas.LikesList])
def post_likes_list_by_user(
    db: db_dependency,
    limit: Annotated[ApiLimitDependency, Depends(api_limit_for_users_resource)],
    page: int = 1,
    token_data: dict = Depends(verify_token),
):
    if page < 1:
        page = 1
    return users_model.post_likes_list_by_user(db, token_data, page=page)


@router.post("/upload-profile-picture/", response_model=schemas.UserOut)
async def upload_profile_picture(
    db: db_dependency,
    file: UploadFile,
    request: Request,
    rds: rds_dependency,
    limit: Annotated[ApiLimitDependency, Depends(api_limit_for_users_resource)],
    token_data: dict = Depends(verify_token),
):
    return await users_model.upload_profile_pic(db, file, token_data, request, rds)


@router.get("/profile-picture/{profile_pic_id}")
async def get_profile_picture(
    profile_pic_id: str,
    limit: Annotated[ApiLimitDependency, Depends(api_limit_for_users_resource)],
):
    return await users_model.get_profile_pic(profile_pic_id)
