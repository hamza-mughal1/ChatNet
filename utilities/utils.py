from passlib.context import CryptContext
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import Depends
from models.database_orm import get_db
from sqlalchemy.inspection import inspect
from models.redis_setup import get_rds
from redis import Redis
from enum import Enum

class ApiLimitMode(Enum):
    SLOTH=2
    TURTLE=5
    PANDA=10
    HORSE=20
    CHEETAH=30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_hashed_password(passowrd):
    return pwd_context.hash(passowrd)

def verify_password(password, hashed_password):
    return pwd_context.verify(password, hashed_password)

db_dependency = Annotated[Session, Depends(get_db)]
rds_dependency = Annotated[Redis, Depends(get_rds)]

def orm_to_dict(obj):
    return {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}

def generate_image_path(filename, func_path, request):
    if func_path == "":
        return "unable to generate the link"
    if filename == "None":
        return "None"

    func_path = str(request.base_url)[:-1] + func_path.split("{")[0]
    final_path = func_path + filename
    return final_path