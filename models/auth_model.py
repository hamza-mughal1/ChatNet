from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from models import schemas
import utils
from models import db_models
import Oauth2

router = APIRouter(tags=["Authentication"])


@router.post("/login", response_model=schemas.Token)
def login(db : utils.db_dependency, user_credentials: OAuth2PasswordRequestForm = Depends()):

    user = db.query(db_models.Users).filter(db_models.Users.email == user_credentials.username).first()
    if not user:
        raise HTTPException(status_code=403, detail="Invalid Credentials")
    if not utils.verify_password(user_credentials.password, user.password):
        raise HTTPException(status_code=403, detail="Invalid Credentials")
    
    token = Oauth2.create_access_token({"user_id":user.id, "user_name":user.user_name})

    return {"access_token":token, "token_type":"Bearer"}
