from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing_extensions import Annotated


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(extra="ignore", from_attributes=True)
    id: int
    email: EmailStr
    created_at: datetime


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True


class PostCreate(PostBase):
    pass


class Post(PostBase):
    model_config = ConfigDict(extra="ignore", from_attributes=True)
    id: int
    created_at: datetime
    owner_id: int
    owner: UserOut


class PostOut(BaseModel):
    model_config = ConfigDict(extra="ignore", from_attributes=True)
    Post: Post
    votes: int


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: int | None


class Vote(BaseModel):
    post_id: int
    dir: Annotated[int, Field(strict=True, ge=0, le=1)]
