import utils
from models.db_models import Posts as DbPostModel, Users, Comments
from fastapi import HTTPException

class PostsModel():
    def __init__(self):
        pass

    @staticmethod
    def create_dict(db, obj):
        user = utils.orm_to_dict(obj[1])
        post = utils.orm_to_dict(obj[0])
        comments = db.query(Comments).filter(Comments.post_id == post["id"]).count()
        dic = {**user}
        dic.update(post)
        dic.update({"comments":comments})

        return dic

    
    def get_all_posts(self, db : utils.db_dependency, token_data):
        posts = db.query(DbPostModel, Users).join(Users, DbPostModel.user_id == Users.id).all()
        l = []
        for i in posts:
            l.append(PostsModel.create_dict(db, i))

        return l
    
    def create_post(self, db, post_data, token_data):
        post = DbPostModel(user_id = token_data["user_id"], **post_data.model_dump())
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

        db.delete(post)
        db.commit()
        
        return returning_post