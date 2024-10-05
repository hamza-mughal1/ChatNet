import utilities.utils as utils
from models.db_models import Posts as DbPostModel, Users, Comments, Likes
from fastapi import HTTPException
from fastapi.responses import FileResponse
from datetime import datetime
from PIL import Image #type:ignore
from io import BytesIO
import os
from handlers import posts_handler
import json
import pickle

class PostsModel():
    get_post_func_name = "get_post_image"
    image_folder_name = "post_pics"
    POST_PIC_DIR = os.getcwd() + f"/{image_folder_name}/"
    def __init__(self):
        
        self.allowed_post_image_type = ["png", "jpg", "jpeg"]
        self.image_size = 2

    @staticmethod
    def get_post_image_url(post, request):
        path = PostsModel.POST_PIC_DIR + post["image"]
        if not os.path.exists(path):
            return "None"
        
        func_path = ""
        for i in posts_handler.router.routes:
            if i.name == PostsModel.get_post_func_name:
                func_path = i.path
        return utils.generate_image_path(post["image"], func_path, request)

    @staticmethod
    def create_dict(obj, request):
        from models.users_model import UsersModel # import inside a function due to circlular import error
        
        user = obj[1]
        profile_pic = UsersModel.get_user_profile_url(user, request)
        user = utils.orm_to_dict(user)
        user["profile_pic"] = profile_pic
        post = utils.orm_to_dict(obj[0])
        post["image"] = PostsModel.get_post_image_url(post, request)
        dic = {**user}
        dic.update(post)

        return dic

    
    def get_all_posts(self, db : utils.db_dependency, request):
        posts = db.query(DbPostModel, Users).join(Users, DbPostModel.user_id == Users.id).all()
        l = []
        for i in posts:
            l.append(PostsModel.create_dict(i, request))

        return l
    
    async def create_post(self, db, title, content, file, token_data, request):
        if file:
            if file.content_type.split("/")[1] not in self.allowed_post_image_type:
                raise HTTPException(status_code=400, detail=f"only {self.allowed_post_image_type} types are allowed")
            
            os.makedirs(self.POST_PIC_DIR, exist_ok=True)

            img = await file.read()
            if len(img) > self.image_size * 1024 * 1024: 
                raise HTTPException(status_code=400, detail=f"Request body size exceeds {self.image_size}MB limit.")
            byte_stream = BytesIO(img)
            image = Image.open(byte_stream)
            unique_file_name = str(datetime.now().timestamp()).replace(".", "")
            final_unique_name = unique_file_name + file.filename
            image.save(self.POST_PIC_DIR + final_unique_name)
            url = final_unique_name
        else:
            url = "None"

        post = DbPostModel(user_id = token_data["user_id"], title=title, content=content, image=url)

        db.add(post)
        db.commit()

        final_post = db.query(DbPostModel, Users).join(Users, DbPostModel.user_id == Users.id).filter(DbPostModel.id == post.id).first()
        return PostsModel.create_dict(final_post, request)
    
        
    def get_post(self, db: utils.db_dependency, id, request, rds, update_cache=False):
        rds_parameter = f"get_post_by_id_{id}"
        cache = rds.get(rds_parameter)
        if cache and update_cache is False:
            return pickle.loads(cache)
        
        
        post = db.query(DbPostModel, Users).join(Users, DbPostModel.user_id == Users.id).filter(DbPostModel.id == id).first()
        if not post:
            raise HTTPException(status_code=404, detail="No post found")
        
        dic = PostsModel.create_dict(post, request)
        
        # cache is set for 3 minutes (3 seconds * by 60 = 3 minutes)
        rds.setex(rds_parameter, 3 * 60, pickle.dumps(dic))
        return dic
    
    def delete_post(self, db: utils.db_dependency, id, token_data, request):
        post = db.query(DbPostModel).filter(DbPostModel.id == id).first()

        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        if not post.user_id == token_data["user_id"]:
            raise HTTPException(status_code=403, detail="Access denied. (Don't have ownership)")

        returning_post = db.query(DbPostModel, Users).join(Users, DbPostModel.user_id == Users.id).filter(DbPostModel.id == id).first()
        returning_post = PostsModel.create_dict(returning_post, request)

        if post.image != "None":
            if os.path.exists(temp := self.POST_PIC_DIR + post.image):
                os.remove(temp)

        db.delete(post)
        db.commit()
        
        return returning_post
    
    def like_post(self, db: utils.db_dependency, post_id, token_data, request, rds):
        if (post := db.query(DbPostModel).filter(DbPostModel.id == post_id).first()) is None:
            raise HTTPException(status_code=404, detail="post not found")
        
        if db.query(Likes).filter(Likes.user_id == token_data["user_id"]).filter(Likes.post_id == post_id).first() is not None:
            return PostsModel.get_post(self, db, post_id, request, rds, update_cache=True)
        
        like = Likes(user_id=token_data["user_id"], post_id=post_id)
        
        post.likes += 1
        db.add(like)
        db.commit()

        return PostsModel.get_post(self, db, post_id, request, rds, update_cache=True)
    
    def dislike_post(self, db: utils.db_dependency, post_id, token_data, request, rds):
        if (post := db.query(DbPostModel).filter(DbPostModel.id == post_id).first()) is None:
            raise HTTPException(status_code=404, detail="post not found")
        
        if (like := db.query(Likes).filter(Likes.user_id == token_data["user_id"]).filter(Likes.post_id == post_id).first()) is None:
            return PostsModel.get_post(self, db, post_id, rds, update_cache=True)

        post.likes -= 1
        db.delete(like)
        db.commit()

        return PostsModel.get_post(self, db, post_id, request, rds, update_cache=True)
    
    def post_likes_list(self, db: utils.db_dependency, post_id, rds):
        rds_parameter = f"post_likes_list_of_id_{post_id}"
        cache = rds.get(rds_parameter)
        if cache:
            return pickle.loads(cache)
        
        l = []
        for i in db.query(Likes).filter(Likes.post_id == post_id).all():
            dic = utils.orm_to_dict(i)
            user_name = db.query(Users).filter(Users.id == i.user_id).first().user_name
            dic.update({"user_name":user_name})
            l.append(dic)
            
        # cache is set for 5 sec for more frequent update
        rds.setex(rds_parameter, 5, pickle.dumps(l))
        return l


    async def get_post_image(self, image_id):
        path = self.POST_PIC_DIR + image_id
        if not os.path.exists(path):
            raise HTTPException(status_code=404, detail="no image found")
        
        return FileResponse(path=path)
    