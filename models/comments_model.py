import utils
from models.db_models import Posts as DbPostModel, Users, Comments
from fastapi import HTTPException

class CommentsModel():
    def __init__(self):
        pass

    def comment_on_post(self, db: utils.db_dependency, id, comment, token_data):
        if (db.query(DbPostModel).filter(DbPostModel.id == id).first()) is None:
            raise HTTPException(status_code=404, detail="Post not found")
        new_comment = Comments(user_id=token_data["user_id"], post_id=id, content=comment.content)
        db.add(new_comment)
        db.commit()

        return utils.orm_to_dict(new_comment)
    

    def get_comment_by_post_id(self, db: utils.db_dependency, id, token_data):
        return db.query(Comments).filter(Comments.post_id == id).all()
    
    def delete_comment(self, db: utils.db_dependency, id, token_data):
        if (comment := db.query(Comments).filter(Comments.id == id).first()) is None:
            raise HTTPException(status_code=404, detail="comment not found")
        
        if comment.user_id != token_data["user_id"]:
            raise HTTPException(status_code=403, detail="Access denied. (Don't have ownership)")

        db.delete(comment)
        db.commit()

        return comment