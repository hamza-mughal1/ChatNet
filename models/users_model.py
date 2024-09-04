from models.db_models import Users as DbUserModel, Follows
from fastapi import HTTPException
import utils
from models import schemas
from sqlalchemy.exc import IntegrityError

class UsersModel():
    def __init__(self):
        pass

    @staticmethod
    def dict_with_follow(db, user):
        followers = db.query(Follows).filter(Follows.follower_id == user.id).count()
        following = db.query(Follows).filter(Follows.following_id == user.id).count()
        return {"followers":followers, "following":following,**utils.orm_to_dict(user)}

    def get_all_users(self, db : utils.db_dependency):    
        return [UsersModel.dict_with_follow(db, i) for i in (db.query(DbUserModel).all())] 
    
    def create_user(self, user_info, db: utils.db_dependency):
        if db.query(DbUserModel).filter(DbUserModel.user_name == user_info.user_name).first():
            raise HTTPException(status_code=409, detail="user_name already exists")
        
        if db.query(DbUserModel).filter(DbUserModel.email == user_info.email).first():
            raise HTTPException(status_code=409, detail="email already exists")
        
        user_info.password = utils.create_hashed_password(user_info.password)
        user = DbUserModel(**user_info.model_dump())
        
        db.add(user)
        db.commit()
        return UsersModel.dict_with_follow(db, user)
    
    def get_user(self, db: utils.db_dependency, id):
        if (user := db.query(DbUserModel).filter(DbUserModel.id == id).first()) is None:
            raise HTTPException(status_code=404, detail="user not found")
    
        return UsersModel.dict_with_follow(db, user)
    

    def update_user(self, db: utils.db_dependency, user_data: schemas.UpdateUser, token_data):
        user = db.query(DbUserModel).filter(DbUserModel.id == token_data["user_id"]).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        try:
            user.name = user_data.name
            user.user_name = user_data.user_name 
            user.bio = user_data.bio
            user.email = user_data.email
            db.commit()
        except IntegrityError as e:
            if "psycopg2.errors.UniqueViolation" in e.args[0]:
                error_field = e.args[0].split("DETAIL:  Key (")[1].split(")=")[0]
            else:
                error_field = "{some-field}"
            raise HTTPException(status_code=409, detail=f"{error_field} already exists")
    
        return UsersModel.dict_with_follow(db, user)
    
    def patch_user(self, db: utils.db_dependency, user_data: schemas.UpdateUserPatch, token_data):
        user = db.query(DbUserModel).filter(DbUserModel.id == token_data["user_id"]).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if  not all([i == None for i in user_data.model_dump().values()]):
            try:
                if user_data.name is not None:
                    user.name = user_data.name
                if user_data.user_name is not None:
                    user.user_name = user_data.user_name
                if user_data.bio is not None:
                    user.bio = user_data.bio
                if user_data.email is not None:
                    user.email = user_data.email
                db.commit()
            except IntegrityError as e:
                if "psycopg2.errors.UniqueViolation" in e.args[0]:
                    error_field = e.args[0].split("DETAIL:  Key (")[1].split(")=")[0]
                else:
                    error_field = "{some-field}"
                raise HTTPException(status_code=409, detail=f"{error_field} already exists")
        
        return UsersModel.dict_with_follow(db, user)
    
    def delete_user(self, db: utils.db_dependency, token_data):
        user = db.query(DbUserModel).filter(DbUserModel.id == token_data["user_id"]).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        db.delete(user)
        db.commit()

        return UsersModel.dict_with_follow(db, user)
        return UsersModel.dict_with_follow(db, user)