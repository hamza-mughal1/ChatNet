from fastapi import APIRouter, Depends
from models.database_orm import get_db
from sqlalchemy.orm import Session
from models.users_model import UsersModel
from models import schemas
from typing import List

router = APIRouter(prefix="/users", tags=["users"])

users_model = UsersModel()

@router.get("/", response_model=List[schemas.UserOut])
def all_users(db : Session =  Depends(get_db)):
    return users_model.get_all_users(db)

@router.post("/", response_model=schemas.UserOut, status_code=201)
def create_user(user: schemas.CreateUser, db : Session =  Depends(get_db)):
    return users_model.create_user(user, db)