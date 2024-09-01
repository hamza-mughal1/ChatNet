from pydantic import BaseModel, EmailStr
from datetime import datetime

class PostOut(BaseModel):
    id: int
    user_id: int
    title: str
    content: str
    likes: int
    created_at: datetime

    class Config:
        orm_mode = True

class UserOut(BaseModel):
    id: int
    name: str
    user_name: str
    created_at: datetime

    class Config:
        orm_mode = True

class CreateUser(BaseModel):
    name: str
    user_name: str
    email: EmailStr
    password: str