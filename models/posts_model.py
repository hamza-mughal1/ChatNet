import utilities.utils as utils
from models.db_models import Posts as DbPostModel, Users, Comments, Likes
from fastapi import HTTPException
from fastapi.responses import FileResponse
from datetime import datetime
from PIL import Image #type:ignore
from io import BytesIO
import os
from utilities.settings import setting
from handlers import posts_handler
HOST = setting.host
PORT = setting.port

class PostsModel():
    def __init__(self):
        self.POST_PIC_DIR = os.getcwd() + "/post_pics/"
        self.allowed_post_image_type = ["png", "jpg", "jpeg"]
        self.image_size = 2

    @staticmethod
    def create_dict(db, obj):
        user = utils.orm_to_dict(obj[1])
        post = utils.orm_to_dict(obj[0])
        comments = db.query(Comments).filter(Comments.post_id == post["id"]).count()
        likes = db.query(Likes).filter(Likes.post_id == post["id"]).count()
        dic = {**user}
        dic.update(post)
        dic.update({"comments":comments, "likes": likes})

        return dic

    
    def get_all_posts(self, db : utils.db_dependency):
        posts = db.query(DbPostModel, Users).join(Users, DbPostModel.user_id == Users.id).all()
        l = []
        for i in posts:
            l.append(PostsModel.create_dict(db, i))

        return l
    
    async def create_post(self, db, title, content, file, token_data):
        if file:
            if file.content_type.split("/")[1] not in self.allowed_post_image_type:
                raise HTTPException(status_code=400, detail=f"only {self.allowed_post_image_type} types are allowed")
            
            os.makedirs(self.POST_PIC_DIR, exist_ok=True)
            func_path = ""
            for i in posts_handler.router.routes:
                if i.name == "get_post_image":
                    func_path = i.path

            func_path = HOST + ":" + PORT + func_path.split("{")[0]

            img = await file.read()
            if len(img) > self.image_size * 1024 * 1024: 
                raise HTTPException(status_code=400, detail=f"Request body size exceeds {self.image_size}MB limit.")
            byte_stream = BytesIO(img)
            image = Image.open(byte_stream)
            unique_file_name = str(datetime.now().timestamp()).replace(".", "")
            final_unique_name = unique_file_name + file.filename
            url = final_unique_name
            final_unique_name = self.POST_PIC_DIR + final_unique_name
            image.save(final_unique_name)
            url = func_path + url
        else:
            url = "None"

        post = DbPostModel(user_id = token_data["user_id"], title=title, content=content, image=url)

        db.add(post)
        db.commit()

        final_post = db.query(DbPostModel, Users).join(Users, DbPostModel.user_id == Users.id).filter(DbPostModel.id == post.id).first()
        return PostsModel.create_dict(db, final_post)
    
        
    def get_post(self, db: utils.db_dependency, id):
        post = db.query(DbPostModel, Users).join(Users, DbPostModel.user_id == Users.id).filter(DbPostModel.id == id).first()
        if not post:
            raise HTTPException(status_code=404, detail="No post found")
        
        return PostsModel.create_dict(db, post)
    
    def delete_post(self, db: utils.db_dependency, id, token_data):
        post = db.query(DbPostModel).filter(DbPostModel.id == id).first()

        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        if not post.user_id == token_data["user_id"]:
            raise HTTPException(status_code=403, detail="Access denied. (Don't have ownership)")

        returning_post = db.query(DbPostModel, Users).join(Users, DbPostModel.user_id == Users.id).filter(DbPostModel.id == id).first()
        returning_post = PostsModel.create_dict(db, returning_post)

        func_path = ""
        for i in posts_handler.router.routes:
            if i.name == "get_post_image":
                func_path = i.path

        func_path = HOST + ":" + PORT + func_path.split("{")[0]
        
        if post.image != "None":
            if os.path.exists(temp := self.POST_PIC_DIR + post.image.split(func_path)[1]):
                os.remove(temp)

        db.delete(post)
        db.commit()
        
        return returning_post
    
    def like_post(self, db: utils.db_dependency, post_id, token_data):
        if db.query(DbPostModel).filter(DbPostModel.id == post_id).first() is None:
            raise HTTPException(status_code=404, detail="post not found")
        
        if db.query(Likes).filter(Likes.user_id == token_data["user_id"]).filter(Likes.post_id == post_id).first() is not None:
            return PostsModel.get_post(self, db, post_id)
        
        like = Likes(user_id=token_data["user_id"], post_id=post_id)
        db.add(like)
        db.commit()

        return PostsModel.get_post(self, db, post_id)
    
    def dislike_post(self, db: utils.db_dependency, post_id, token_data):
        if db.query(DbPostModel).filter(DbPostModel.id == post_id).first() is None:
            raise HTTPException(status_code=404, detail="post not found")
        
        if (like := db.query(Likes).filter(Likes.user_id == token_data["user_id"]).filter(Likes.post_id == post_id).first()) is None:
            return PostsModel.get_post(self, db, post_id)

        db.delete(like)
        db.commit()

        return PostsModel.get_post(self, db, post_id)
    
    def post_likes_list(self, db: utils.db_dependency, post_id):
        l = []
        for i in db.query(Likes).filter(Likes.post_id == post_id).all():
            dic = utils.orm_to_dict(i)
            user_name = db.query(Users).filter(Users.id == i.user_id).first().user_name
            dic.update({"user_name":user_name})
            l.append(dic)

        return l


    async def get_post_image(self, image_id):
        path = self.POST_PIC_DIR + image_id
        if not os.path.exists(path):
            raise HTTPException(status_code=404, detail="no image found")
        
        return FileResponse(path=path)
    