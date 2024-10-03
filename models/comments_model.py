import utilities.utils as utils
from models.db_models import Posts as DbPostModel, Users, Comments
from fastapi import HTTPException

class CommentsModel():
    def __init__(self):
        pass

    def comment_on_post(self, db: utils.db_dependency, id, comment, token_data):
        if (post := db.query(DbPostModel).filter(DbPostModel.id == id).first()) is None:
            raise HTTPException(status_code=404, detail="Post not found")
        new_comment = Comments(user_id=token_data["user_id"], post_id=id, content=comment.content)
        db.add(new_comment)
        post.comments += 1
        db.commit()
        dic = utils.orm_to_dict(new_comment)
        dic.update({"user_name":token_data["user_name"]})
        return dic
    

    def get_comment_by_post_id(self, db: utils.db_dependency, id):
        if db.query(DbPostModel).filter(DbPostModel.id == id).first() is None:
            raise HTTPException(status_code=404, detail="post not found")
        
        
        user_name = None
        l = []
        for i in db.query(Comments).filter(Comments.post_id == id).all():
            dic = utils.orm_to_dict(i)
            if user_name is None:
                user_name = db.query(Users).filter(Users.id == i.user_id).first().user_name
            dic.update({"user_name":user_name})
            l.append(dic)
        return l
    
    def delete_comment(self, db: utils.db_dependency, id, token_data):
        if (comment := db.query(Comments).filter(Comments.id == id).first()) is None:
            raise HTTPException(status_code=404, detail="comment not found")
        
        if comment.user_id != token_data["user_id"]:
            raise HTTPException(status_code=403, detail="Access denied. (Don't have ownership)")
        
        post = db.query(DbPostModel).filter(DbPostModel.id == comment.post_id).first()

        db.delete(comment)
        post.comments -= 1
        db.commit()
        comment = utils.orm_to_dict(comment)
        comment.update({"user_name":token_data["user_name"]})
        return comment
    
    def get_comment_by_user_id(self, db: utils.db_dependency, token_data):
        l = []
        for i in db.query(Comments).filter(Comments.user_id == token_data["user_id"]).all():
            dic = utils.orm_to_dict(i)
            dic.update({"user_name":token_data["user_name"]})
            l.append(dic)
        return l
    
    def get_by_comment_id(self, db: utils.db_dependency, id):
        if (comment := db.query(Comments).filter(Comments.id == id).first()) is None:
            raise HTTPException(status_code=404, detail="comment not found")

        
        user_name = db.query(Users).filter(Users.id == comment.user_id).first().user_name
        comment = utils.orm_to_dict(comment)
        comment.update({"user_name": user_name})
        return comment