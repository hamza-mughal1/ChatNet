import utils
from models.db_models import Posts as DbPostModel
from sqlalchemy.orm import Session
from fastapi import HTTPException

class PostsModel():
    def __init__(self):
        pass
    
    def get_all_posts(self, db : utils.db_dependency, token_data):
        return db.query(DbPostModel).all()
    
    def create_post(self, db, post_data, token_data):
        post = DbPostModel(user_id = token_data["user_id"], **post_data.model_dump())
        db.add(post)
        db.commit()

        return post
        
    def get_post(self, db: Session, id):
        post = db.query(DbPostModel).filter(DbPostModel.id == id).first()

        if not post:
            raise HTTPException(status_code=404, detail="No post found")
        
        return post