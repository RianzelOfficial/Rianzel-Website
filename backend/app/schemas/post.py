from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from .user import UserResponse

class PostBase(BaseModel):
    title: str
    content: str
    category_id: int
    views: int = 0

class PostCreate(PostBase):
    pass

class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category_id: Optional[int] = None
    status: Optional[str] = None

class PostInDB(PostBase):
    id: int
    author_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PostResponse(PostInDB):
    author: UserResponse
    likes_count: int
    comments_count: int
    is_liked: bool
    last_activity: datetime
    status: str
    featured_image: Optional[str] = None
    tags: List[str] = []

class PostListResponse(BaseModel):
    posts: List[PostResponse]
    total: int
    page: int
    pages: int

class PostStats(BaseModel):
    total_posts: int
    daily_posts: int
    weekly_posts: int
    monthly_posts: int
    active_categories: int
    active_users: int

class PostSearchResponse(BaseModel):
    posts: List[PostResponse]
    total: int
    page: int
    pages: int
    filters: dict
    sort_options: List[str]
    time_ranges: List[str]
