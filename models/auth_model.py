from fastapi import APIRouter, HTTPException, Depends, Header
from fastapi.security import OAuth2PasswordRequestForm
from models import schemas
import utilities.utils as utils
from models import db_models
import models.Oauth2 as Oauth2
from typing import Annotated
from jose import jwt, JWTError
from utilities.settings import setting
from utilities.api_limiter import ApiLimitDependency
from utilities.utils import ApiLimitMode

router = APIRouter(tags=["Authentication"])

login_api_limit = ApiLimitDependency(req_count=ApiLimitMode.SLOTH.value)
@router.post("/login", response_model=schemas.Token)
def login(db : utils.db_dependency, rds: utils.rds_dependency, limit : Annotated[ApiLimitDependency, Depends(login_api_limit)], user_credentials: OAuth2PasswordRequestForm = Depends()):
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
    
    # (time * 60) because redis only accepts time in seconds
    rds.setex(access_token,setting.access_token_expire_minutes*60, access_token)

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
    
    
@router.post("/logout")
def logout_user(db : utils.db_dependency, rds: utils.rds_dependency, token : str = Depends(Oauth2.oauth2_baerer), refresh_token: Annotated[str | None, Header()] = None):
    if refresh_token is None:
        raise HTTPException(status_code=403, detail="unable to find 'Refresh-token' header")
    
    try:
        access_payload = jwt.decode(token, Oauth2.SECRET_KEY, algorithms=Oauth2.ALGORITHM)
        pass
    except JWTError:
        raise HTTPException(status_code=403, detail="token is invalid", headers={"WWW-Authenticate":"Bearer"})
    
    try:
        refresh_payload = jwt.decode(refresh_token, Oauth2.SECRET_KEY, algorithms=Oauth2.ALGORITHM)
    except JWTError:
        raise HTTPException(status_code=403, detail="refresh token is invalid", headers={"WWW-Authenticate":"Bearer"})
    
    if access_payload.get("type") != "access-token":
        raise HTTPException(status_code=403, detail="token is invalid", headers={"WWW-Authenticate":"Bearer"})

    if refresh_payload.get("type") != "refresh-token":
        raise HTTPException(status_code=403, detail="refresh token is invalid", headers={"WWW-Authenticate":"Bearer"})

    if (refresh_db_model := db.query(db_models.RefreshTokens).filter(db_models.RefreshTokens.token == refresh_token).first()) is None:
        raise HTTPException(status_code=403, detail="refresh token is invalid", headers = {"WWW-Authenticate":"Bearer"})

    

    if (access_db_model := db.query(db_models.AccessTokens).filter(db_models.AccessTokens.id == refresh_db_model.access_token_id).first()).token != token:
        raise HTTPException(status_code=403, detail="token is invalid", headers={"WWW-Authenticate":"Bearer"})
    
    db.delete(access_db_model)
    db.commit()
    rds.delete(token)

    return {"messsage": "You have been logged out"}


   
@router.post("/logout-all")
def logout_user(db : utils.db_dependency, rds: utils.rds_dependency, token : str = Depends(Oauth2.oauth2_baerer), refresh_token: Annotated[str | None, Header()] = None):
    if refresh_token is None:
        raise HTTPException(status_code=403, detail="unable to find 'Refresh-token' header")
    
    try:
        access_payload = jwt.decode(token, Oauth2.SECRET_KEY, algorithms=Oauth2.ALGORITHM)
        pass
    except JWTError:
        raise HTTPException(status_code=403, detail="token is invalid", headers={"WWW-Authenticate":"Bearer"})
    
    try:
        refresh_payload = jwt.decode(refresh_token, Oauth2.SECRET_KEY, algorithms=Oauth2.ALGORITHM)
    except JWTError:
        raise HTTPException(status_code=403, detail="refresh token is invalid", headers={"WWW-Authenticate":"Bearer"})
    
    if access_payload.get("type") != "access-token":
        raise HTTPException(status_code=403, detail="token is invalid", headers={"WWW-Authenticate":"Bearer"})

    if refresh_payload.get("type") != "refresh-token":
        raise HTTPException(status_code=403, detail="refresh token is invalid", headers={"WWW-Authenticate":"Bearer"})

    if (refresh_db_model := db.query(db_models.RefreshTokens).filter(db_models.RefreshTokens.token == refresh_token).first()) is None:
        raise HTTPException(status_code=403, detail="refresh token is invalid", headers = {"WWW-Authenticate":"Bearer"})

    

    if (db.query(db_models.AccessTokens).filter(db_models.AccessTokens.id == refresh_db_model.access_token_id).first()).token != token:
        raise HTTPException(status_code=403, detail="token is invalid", headers={"WWW-Authenticate":"Bearer"})
    
    acc_tokens = db.query(db_models.AccessTokens).filter(db_models.AccessTokens.user_id == refresh_db_model.user_id).all()
    for i in acc_tokens:
        db.delete(i)
        rds.delete(i.token)
    db.commit()

    return {"messsage": "You have been logged out from all logins"}