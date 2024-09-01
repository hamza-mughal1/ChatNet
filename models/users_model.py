from sqlalchemy.orm import Session
from models.db_models import Users as DbUserModel
from fastapi import HTTPException


class UsersModel():
    def __init__(self):
        pass

    def get_all_users(self, db : Session):
        return db.query(DbUserModel).all()
    
    def create_user(self, user_info, db: Session):
        if db.query(DbUserModel).filter(DbUserModel.user_name == user_info.user_name).first():
            raise HTTPException(status_code=409, detail="user_name already exists")
        
        if db.query(DbUserModel).filter(DbUserModel.email == user_info.email).first():
            raise HTTPException(status_code=409, detail="email already exists")
        
        user = DbUserModel(**user_info.dict())
        
        db.add(user)
        db.commit()
        return user