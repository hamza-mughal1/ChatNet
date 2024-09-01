from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_hashed_password(passowrd):
    return pwd_context.hash(passowrd)