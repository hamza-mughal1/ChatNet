from handlers import users_handler
from models.db_models import Users as DbUserModel, Follows, Likes
from config import HOST, PORT #type:ignore
from fastapi import HTTPException, UploadFile, Request
from fastapi.responses import FileResponse
import utils
from models import schemas
from sqlalchemy.exc import IntegrityError
from io import BytesIO
from PIL import Image #type:ignore
from datetime import datetime
import os

class UsersModel():
    def __init__(self):
        self.PROFILE_PIC_DIR = os.getcwd() + "/profile_pics/"
        self.allowed_profile_image_type = ["png", "jpg", "jpeg"]
        self.max_image_size = 2

    @staticmethod
    def dict_with_follow(db, user):
        following = db.query(Follows).filter(Follows.follower_id == user.id).count()
        followers = db.query(Follows).filter(Follows.following_id == user.id).count()
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
        
        func_path = ""
        for i in users_handler.router.routes:
            if i.name == "get_profile_picture":
                func_path = i.path

        func_path = HOST + ":" + PORT + func_path.split("{")[0]
        
        if user.profile_pic != "None":
            if os.path.exists(temp := self.PROFILE_PIC_DIR + user.profile_pic.split(func_path)[1]):
                os.remove(temp)
        
        db.delete(user)
        db.commit()


        return UsersModel.dict_with_follow(db, user)
    

    def search_by_user_name(self, db: utils.db_dependency, user_name):
        if (user := db.query(DbUserModel).filter(DbUserModel.user_name == user_name).first()) is None:
            raise HTTPException(status_code=404, detail="user not found")
    
        return UsersModel.dict_with_follow(db, user)
    
    def follow_user(self, db: utils.db_dependency, user_id, token_data):
        if user_id == token_data["user_id"]:
            raise HTTPException(status_code=400, detail="Not allowed to follow yourself")
        if db.query(DbUserModel).filter(DbUserModel.id == user_id).first() is None:
            raise HTTPException(status_code=404, detail="user not found")
        
        if db.query(Follows).filter(Follows.follower_id == token_data["user_id"]).filter(Follows.following_id == user_id).first() is not None:
            return UsersModel.get_user(self, db, user_id)
        
        follow = Follows(follower_id=token_data["user_id"], following_id=user_id)
        db.add(follow)
        db.commit()

        return UsersModel.get_user(self, db, user_id)
    
    def unfollow_user(self, db: utils.db_dependency, user_id, token_data):
        if user_id == token_data["user_id"]:
            raise HTTPException(status_code=400, detail="Not allowed to unfollow yourself")
        
        if (follow := db.query(Follows).filter(Follows.follower_id == token_data["user_id"]).filter(Follows.following_id == user_id).first()) is None:
            return UsersModel.get_user(self, db, user_id)
        
        db.delete(follow)
        db.commit()

        return UsersModel.get_user(self, db, user_id)
    
    def following_list(self, db: utils.db_dependency, user_id):
        l = []
        for i in db.query(Follows).filter(Follows.follower_id == user_id).all():
            dic = utils.orm_to_dict(i)
            follower_user_name = db.query(DbUserModel).filter(DbUserModel.id == i.follower_id).first().user_name
            following_user_name = db.query(DbUserModel).filter(DbUserModel.id == i.following_id).first().user_name
            dic.update({"follower_user_name":follower_user_name, "following_user_name":following_user_name})
            l.append(dic)

        return l
    
    def follower_list(self, db: utils.db_dependency, user_id):
        l = []
        for i in db.query(Follows).filter(Follows.following_id == user_id).all():
            dic = utils.orm_to_dict(i)
            follower_user_name = db.query(DbUserModel).filter(DbUserModel.id == i.follower_id).first().user_name
            following_user_name = db.query(DbUserModel).filter(DbUserModel.id == i.following_id).first().user_name
            dic.update({"follower_user_name":follower_user_name, "following_user_name":following_user_name})
            l.append(dic)

        return l
    
    def change_password(self, db: utils.db_dependency, details: schemas.ChangePassword, token_data):
        result = db.query(DbUserModel).filter(DbUserModel.id == token_data["user_id"]).first()
        db_email = result.email
        db_pass = result.password

        if details.email != db_email:
            raise HTTPException(status_code=403, detail="Invalid Credentials")

        if not utils.verify_password(details.password, db_pass):
            raise HTTPException(status_code=403, detail="Invalid Credentials")
        
        result.password = utils.create_hashed_password(details.new_password)
        db.commit()

        return UsersModel.get_user(self, db, token_data["user_id"])
    

    def post_likes_list_by_user(self, db: utils.db_dependency, token_data):
        l = []
        for i in db.query(Likes).filter(Likes.user_id == token_data["user_id"]).all():
            dic = utils.orm_to_dict(i)
            dic.update({"user_name":token_data["user_name"]})
            l.append(dic)

        return l
    
    async def upload_profile_pic(self, db: utils.db_dependency, file: UploadFile, token_data):
        

        
        if file.content_type.split("/")[1] not in self.allowed_profile_image_type:
            raise HTTPException(status_code=400, detail=f"only {self.allowed_profile_image_type} types are allowed")
        
        
        os.makedirs(self.PROFILE_PIC_DIR, exist_ok=True)
        func_path = ""
        for i in users_handler.router.routes:
            if i.name == "get_profile_picture":
                func_path = i.path

        func_path = HOST + ":" + PORT + func_path.split("{")[0]

        img = await file.read()
        if len(img) > self.max_image_size * 1024 * 1024: 
            raise HTTPException(status_code=400, detail=f"Request body size exceeds {self.max_image_size}MB limit.")
        byte_stream = BytesIO(img)
        image = Image.open(byte_stream)
        unique_file_name = str(datetime.now().timestamp()).replace(".", "")
        final_unique_name = unique_file_name + file.filename
        url = final_unique_name
        final_unique_name = self.PROFILE_PIC_DIR + final_unique_name
        image.save(final_unique_name)
        user = db.query(DbUserModel).filter(DbUserModel.id == token_data["user_id"]).first()
        if user.profile_pic != "None":
            if os.path.exists(temp := self.PROFILE_PIC_DIR + user.profile_pic.split(func_path)[1]):
                os.remove(temp)
        
        

        user.profile_pic = func_path + url
        db.commit()
        return UsersModel.get_user(self, db, user.id)
    
    async def get_profile_pic(self, profile_pic_id: str):
        path = self.PROFILE_PIC_DIR + profile_pic_id
        if not os.path.exists(path):
            raise HTTPException(status_code=404, detail="no profile picture found")
        
        return FileResponse(path=path)
