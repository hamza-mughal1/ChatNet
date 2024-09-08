from pydantic import BaseModel, EmailStr, field_validator, FieldValidationInfo
from datetime import datetime
import re
from typing import Optional

class PostOut(BaseModel):
    id: int
    user_id: int
    user_name: str
    profile_pic: str
    title: str
    content: str
    image: str
    likes: int
    comments: int
    created_at: datetime

    class Config:
        from_attributes = True

class UserOut(BaseModel):
    id: int
    name: str
    user_name: str
    followers: int
    following: int
    bio: str
    profile_pic: str
    created_at: datetime

    class Config:
        from_attributes = True

class CreateUser(BaseModel):
    name: str
    user_name: str
    email: EmailStr
    password: str

    @field_validator('password')
    def validate_password(cls, value: str, info: FieldValidationInfo):
        # Check for length between 8 and 10 characters
        if not 8 <= len(value) <= 10:
            raise ValueError('Password must be between 8 and 10 characters.')

        # Check for at least one uppercase letter
        if not re.search(r'[A-Z]', value):
            raise ValueError('Password must contain at least one uppercase letter.')

        # Check for at least one digit
        if not re.search(r'\d', value):
            raise ValueError('Password must contain at least one digit.')

        # Check for at least one special character
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise ValueError('Password must contain at least one special character.')

        return value
    
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class CreatePost(BaseModel):
    title: str
    content: str


class UpdateUser(BaseModel):
    name: str
    user_name: str
    bio: str
    email: EmailStr

class UpdateUserPatch(BaseModel):
    name: Optional[str] = None
    user_name: Optional[str] = None
    email: Optional[EmailStr] = None
    bio: Optional[str] = None

class CreateComment(BaseModel):
    content: str

class CommentOut(BaseModel):
    id: int
    user_id: int
    post_id: int
    user_name: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True

class FollowList(BaseModel):
    id: int
    follower_id: int
    following_id: int
    follower_user_name: str
    following_user_name: str 
    created_at: datetime

class ChangePassword(BaseModel):
    email: EmailStr
    password: str
    new_password: str

    @field_validator('password', 'new_password')
    def validate_password(cls, value: str, info: FieldValidationInfo):
        # Check for length between 8 and 10 characters
        if not 8 <= len(value) <= 10:
            raise ValueError('Password must be between 8 and 10 characters.')

        # Check for at least one uppercase letter
        if not re.search(r'[A-Z]', value):
            raise ValueError('Password must contain at least one uppercase letter.')

        # Check for at least one digit
        if not re.search(r'\d', value):
            raise ValueError('Password must contain at least one digit.')

        # Check for at least one special character
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise ValueError('Password must contain at least one special character.')

        return value
    
class LikesList(BaseModel):
    id: int
    post_id: int
    user_id: int
    user_name: str
    created_at: datetime