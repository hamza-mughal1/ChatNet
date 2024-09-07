from fastapi import APIRouter, HTTPException, Depends, Header
from fastapi.security import OAuth2PasswordRequestForm
from models import schemas
import utils
from models import db_models
import Oauth2
from typing import Annotated
from jose import jwt, JWTError

router = APIRouter(tags=["Authentication"])


@router.post("/login", response_model=schemas.Token)
def login(db : utils.db_dependency, user_credentials: OAuth2PasswordRequestForm = Depends()):

    user = db.query(db_models.Users).filter(db_models.Users.email == user_credentials.username).first()
    if not user:
        raise HTTPException(status_code=403, detail="Invalid Credentials")
    if not utils.verify_password(user_credentials.password, user.password):
        raise HTTPException(status_code=403, detail="Invalid Credentials")
    
    access_token = Oauth2.create_token({"user_id":user.id, "user_name":user.user_name, "type":"access-token"})
    refresh_token = Oauth2.create_token({"user_id":user.id, "user_name":user.user_name, "type":"refresh-token"}, refresh=True)

    ac_token = db_models.AccessTokens(user_id=user.id, token=access_token)
    db.add(ac_token)
    db.commit()

    re_token = db_models.RefreshTokens(access_token_id=ac_token.id, user_id=user.id, token=refresh_token)
    db.add(re_token)
    db.commit()

    return {"access_token":access_token, "refresh_token":refresh_token, "token_type":"Bearer"}

@router.post("/refresh", response_model=schemas.Token)
def refresh(db : utils.db_dependency, token : str = Depends(Oauth2.oauth2_baerer), refresh_token: Annotated[str | None, Header()] = None):
    if refresh_token is None:
        raise HTTPException(status_code=403, detail="unable to find 'Refresh-token' header")
    
    try:
        jwt.decode(token, Oauth2.SECRET_KEY, algorithms=Oauth2.ALGORITHM)
        raise HTTPException(status_code=403, detail="token is still valid", headers={"WWW-Authenticate":"Bearer"})
    except JWTError:
        pass
    
    try:
        refresh_payload = jwt.decode(refresh_token, Oauth2.SECRET_KEY, algorithms=Oauth2.ALGORITHM)
    except JWTError:
        raise HTTPException(status_code=403, detail="refresh token is invalid", headers={"WWW-Authenticate":"Bearer"})

    if refresh_payload.get("type") != "refresh-token":
        raise HTTPException(status_code=403, detail="refresh token is invalid", headers={"WWW-Authenticate":"Bearer"})

    if (refresh_db_model := db.query(db_models.RefreshTokens).filter(db_models.RefreshTokens.token == refresh_token).first()) is None:
        raise HTTPException(status_code=403, detail="refresh token is invalid", headers = {"WWW-Authenticate":"Bearer"})

    

    if (access_db_model := db.query(db_models.AccessTokens).filter(db_models.AccessTokens.id == refresh_db_model.access_token_id).first()).token != token:
        raise HTTPException(status_code=403, detail="token is invalid", headers={"WWW-Authenticate":"Bearer"})
    
    user = db.query(db_models.Users).filter(db_models.Users.id == refresh_db_model.user_id).first()

    db.delete(access_db_model)
    db.commit()

    access_token = Oauth2.create_token({"user_id":user.id, "user_name":user.user_name, "type":"access-token"})
    refresh_token = Oauth2.create_token({"user_id":user.id, "user_name":user.user_name, "type":"refresh-token"}, refresh=True)

    ac_token = db_models.AccessTokens(user_id=user.id, token=access_token)
    db.add(ac_token)
    db.commit()

    re_token = db_models.RefreshTokens(access_token_id=ac_token.id, user_id=user.id, token=refresh_token)
    db.add(re_token)
    db.commit()

    return {"access_token":access_token, "refresh_token":refresh_token, "token_type":"Bearer"}
    
    