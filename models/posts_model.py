from sqlalchemy.orm import Session
from models.db_models import Posts as DbPostModel


class PostsModel():
    def __init__(self):
        pass
    
    def get_all_posts(self, db : Session):
        return db.query(DbPostModel).all()