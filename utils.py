from passlib.context import CryptContext
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import Depends
from models.database_orm import get_db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_hashed_password(passowrd):
    return pwd_context.hash(passowrd)

def verify_password(password, hashed_password):
    return pwd_context.verify(password, hashed_password)

db_dependency = Annotated[Session, Depends(get_db)]