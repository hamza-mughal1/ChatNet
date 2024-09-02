from models.db_models import Users as DbUserModel
from fastapi import HTTPException
import utils

class UsersModel():
    def __init__(self):
        pass

    def get_all_users(self, db : utils.db_dependency):
        return db.query(DbUserModel).all()
    
    def create_user(self, user_info, db: utils.db_dependency):
        if db.query(DbUserModel).filter(DbUserModel.user_name == user_info.user_name).first():
            raise HTTPException(status_code=409, detail="user_name already exists")
        
        if db.query(DbUserModel).filter(DbUserModel.email == user_info.email).first():
            raise HTTPException(status_code=409, detail="email already exists")
        
        user_info.password = utils.create_hashed_password(user_info.password)
        user = DbUserModel(**user_info.model_dump())
        
        db.add(user)
        db.commit()
        return user
    