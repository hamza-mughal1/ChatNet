from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from utils import db_dependency
from utilities.utils import db_dependency
from models.db_models import Users, AccessTokens

SECRET_KEY = "77cfbtdl757pu7n526qng21g4ib3?2yy8n9dvj3arn4x52j183jyjunlrxcds6r6"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_MINUTES = 60*24*30*1

oauth2_baerer = OAuth2PasswordBearer(tokenUrl="/login")

def create_token(data: dict, refresh=False):
    to_encode = data.copy()
    if refresh:
        expiration = datetime.now() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    else:
        expiration = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp":round(expiration.timestamp())})

    ecoded_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return ecoded_token

def verify_token(db :  db_dependency, token : str = Depends(oauth2_baerer)):
    if db.query(AccessTokens).filter(AccessTokens.token == token).first() is None:
        raise HTTPException(status_code=403, detail="token is invalid", headers = {"WWW-Authenticate":"Bearer"})
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        user_id = payload.get("user_id")
        user_name  = payload.get("user_name")

        if (user_id is None) or (user_name is None):
            raise HTTPException(status_code=403, detail="token is invalid", headers = {"WWW-Authenticate":"Bearer"})
        
        if (user := db.query(Users).filter(Users.id == user_id).first()) is None:
            raise HTTPException(status_code=403, detail="Invalid token. (User not found)", headers = {"WWW-Authenticate":"Bearer"})
        
        payload.update({"user_name": user.user_name})
    
    except JWTError:
        raise HTTPException(status_code=403, detail="token is invalid", headers={"WWW-Authenticate":"Bearer"})
    
    return payload
    
    