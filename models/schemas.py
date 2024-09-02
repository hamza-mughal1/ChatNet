from pydantic import BaseModel, EmailStr, field_validator, FieldValidationInfo
from datetime import datetime
import re

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