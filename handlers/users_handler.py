from fastapi import APIRouter, Depends
from models.users_model import UsersModel
from models import schemas
from typing import List
from Oauth2 import verify_token
from utils import db_dependency
router = APIRouter(prefix="/users", tags=["users"])

users_model = UsersModel()

@router.get("/", response_model=List[schemas.UserOut])
def all_users(db : db_dependency, token_data: dict = Depends(verify_token)):
    return users_model.get_all_users(db)

@router.post("/", response_model=schemas.UserOut, status_code=201)
def create_user(user: schemas.CreateUser, db:  db_dependency):
    return users_model.create_user(user, db)

@router.get("/{id}", response_model=schemas.UserOut)
def get_user(db :  db_dependency, id: int):
    return users_model.get_user(db, id)

@router.put("/", response_model=schemas.UserOut)
def update_user(db :  db_dependency, user_data: schemas.UpdateUser, token_data: dict = Depends(verify_token)):
    return users_model.update_user(db, user_data, token_data)

@router.delete("/", response_model=schemas.UserOut)
def delete_user(db :  db_dependency, token_data: dict = Depends(verify_token)):
    return users_model.delete_user(db, token_data)

@router.patch("/", response_model=schemas.UserOut)
def patch_user(db:  db_dependency, user_data: schemas.UpdateUserPatch, token_data: dict = Depends(verify_token)):
    return users_model.patch_user(db, user_data, token_data)
