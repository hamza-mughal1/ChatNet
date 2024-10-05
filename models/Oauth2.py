from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from utilities.utils import db_dependency, rds_dependency
from models.db_models import Users, AccessTokens
from utilities.settings import setting
import uuid

SECRET_KEY = setting.secret_key
ALGORITHM = setting.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = setting.access_token_expire_minutes
REFRESH_TOKEN_EXPIRE_MINUTES = setting.refresh_token_expire_minutes

oauth2_baerer = OAuth2PasswordBearer(tokenUrl="/login")

def create_token(data: dict, refresh=False):
    to_encode = data.copy()
    if refresh:
        expiration = datetime.now() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    else:
        expiration = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp":round(expiration.timestamp())})
    to_encode.update({"uuid": str(uuid.uuid4())})

    ecoded_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return ecoded_token

def verify_token(db :  db_dependency, rds: rds_dependency, token : str = Depends(oauth2_baerer)):
    cache = rds.get(token)
    if cache:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
            user_id = payload.get("user_id")
            user_name  = payload.get("user_name")

            if (user_id is None) or (user_name is None):
                raise HTTPException(status_code=403, detail="token is invalid", headers = {"WWW-Authenticate":"Bearer"})
        
        except JWTError:
            raise HTTPException(status_code=403, detail="token is invalid", headers={"WWW-Authenticate":"Bearer"})
        
        payload.update({"token": token})
        
        return payload
    elif db.query(AccessTokens).filter(AccessTokens.token == token).first() is None:
        raise HTTPException(status_code=403, detail="token is invalid", headers = {"WWW-Authenticate":"Bearer"})
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        user_id = payload.get("user_id")
        user_name  = payload.get("user_name")

        if (user_id is None) or (user_name is None):
            raise HTTPException(status_code=403, detail="token is invalid", headers = {"WWW-Authenticate":"Bearer"})
        
        if (user := db.query(Users).filter(Users.id == user_id).first()) is None:
            raise HTTPException(status_code=403, detail="Invalid token. (User not found)", headers = {"WWW-Authenticate":"Bearer"})
        
        payload.update({"user_name": user.user_name, "token": token})
    
    except JWTError:
        raise HTTPException(status_code=403, detail="token is invalid", headers={"WWW-Authenticate":"Bearer"})
    
    return payload
    
    