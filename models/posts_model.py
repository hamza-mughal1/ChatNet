import utils
from models.db_models import Posts as DbPostModel


class PostsModel():
    def __init__(self):
        pass
    
    def get_all_posts(self, db : utils.db_dependency, token_data):
        return db.query(DbPostModel).all()