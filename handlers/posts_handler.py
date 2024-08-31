from fastapi import APIRouter, Depends
from models.database_orm import get_db
from sqlalchemy.orm import Session
from models import db_models
router = APIRouter(prefix="/posts")


@router.get("/")
def all_posts(db : Session =  Depends(get_db)):
    s = db.query(db_models.Posts).all()
    return s
