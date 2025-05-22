from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from .user import UserResponse
from .post import PostResponse

class CommentBase(BaseModel):
    content: str
    post_id: int
    parent_id: Optional[int] = None

class CommentCreate(CommentBase):
    pass

class CommentUpdate(BaseModel):
    content: Optional[str] = None
    status: Optional[str] = None

class CommentInDB(CommentBase):
    id: int
    author_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    likes_count: int = 0
    replies_count: int = 0

    class Config:
        from_attributes = True

class CommentResponse(CommentInDB):
    author: UserResponse
    post: PostResponse
    parent: Optional['CommentResponse'] = None
    replies: List['CommentResponse'] = []
    is_liked: bool
    last_activity: datetime

class CommentListResponse(BaseModel):
    comments: List[CommentResponse]
    total: int
    page: int
    pages: int

class CommentStats(BaseModel):
    total_comments: int
    daily_comments: int
    weekly_comments: int
    monthly_comments: int
    active_users: int
    average_replies: float

class CommentSearchResponse(BaseModel):
    comments: List[CommentResponse]
    total: int
    page: int
    pages: int
    filters: dict
    sort_options: List[str]
    time_ranges: List[str]
