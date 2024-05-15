from typing import Union
from pydantic import BaseModel, EmailStr
from datetime import datetime

class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    user_id: Union[int, None] = None
    rating: Union[int, None] = None

class PostUpdate(BaseModel):
    title: Union[str, None] = None
    content: Union[str, None]= None
    published: Union[bool, None]= None
    user_id: Union[int, None] = None
    rating: Union[int, None] = None

class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    published: bool
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class User(BaseModel):
    full_name: str
    email: EmailStr
    phone: Union[str, None] = None
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    phone: Union[str, None] = None
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: int
