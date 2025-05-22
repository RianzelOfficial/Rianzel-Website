from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class ProfileBase(BaseModel):
    username: str
    email: str
    role: str = "member"
    is_active: bool = True
    is_verified: bool = False

class ProfileCreate(ProfileBase):
    password: str

class ProfileUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    theme_preference: Optional[str] = None
    notification_settings: Optional[dict] = None
    privacy_settings: Optional[dict] = None

class Profile(ProfileBase):
    id: int
    created_at: datetime
    last_login: Optional[datetime] = None
    posts_count: int = 0
    comments_count: int = 0
    likes_count: int = 0

    class Config:
        from_attributes = True

class ProfileStats(BaseModel):
    posts: int
    comments: int
    likes: int

class ProfileActivityItem(BaseModel):
    type: str
    content: str
    created_at: datetime
    post_id: Optional[int] = None
    comment_id: Optional[int] = None
    like_id: Optional[int] = None

class ProfilePreferences(BaseModel):
    theme: Optional[str] = None
    notification_settings: Optional[dict] = None
    privacy_settings: Optional[dict] = None

class ProfileNotification(BaseModel):
    id: int
    message: str
    read: bool
    created_at: datetime

class ProfileResponse(BaseModel):
    profile: Profile
    stats: ProfileStats
    activity: List[ProfileActivityItem]
    preferences: ProfilePreferences
    notifications: List[ProfileNotification]
