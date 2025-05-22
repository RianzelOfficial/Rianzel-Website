from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List

class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: str = "member"
    is_active: bool = True
    is_verified: bool = False

class UserCreate(UserBase):
    password: str
    password_confirm: str
    date_of_birth: datetime
    country: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    profile_picture: Optional[str] = None
    newsletter_subscription: Optional[bool] = None

class UserInDB(UserBase):
    id: int
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True

class UserResponse(UserInDB):
    posts_count: int
    comments_count: int
    likes_count: int
    notifications_count: int
    unread_notifications_count: int

class UserListResponse(BaseModel):
    users: List[UserResponse]
    total: int
    page: int
    pages: int

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    remember_me: bool = False
    country: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: Optional[str] = None
    scopes: List[str] = []

class PasswordReset(BaseModel):
    email: EmailStr
    
class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str
    password_confirm: str
