from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int
    parent_id: Optional[int] = None

    class Config:
        from_attributes = True

class PostBase(BaseModel):
    title: str
    content: str
    category_id: int

class PostCreate(PostBase):
    pass

class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category_id: Optional[int] = None

class Post(PostBase):
    id: int
    author_id: int
    created_at: datetime
    updated_at: datetime
    views: int
    likes_count: int = 0
    comments_count: int = 0

    class Config:
        from_attributes = True

class CommentBase(BaseModel):
    content: str
    post_id: int
    parent_id: Optional[int] = None

class CommentCreate(CommentBase):
    pass

class CommentUpdate(BaseModel):
    content: str

class Comment(CommentBase):
    id: int
    author_id: int
    created_at: datetime
    likes_count: int = 0

    class Config:
        from_attributes = True

class LikeBase(BaseModel):
    post_id: int

class LikeCreate(LikeBase):
    pass

class Like(LikeBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class PostWithComments(BaseModel):
    post: Post
    comments: List[Comment]

class CategoryWithPosts(BaseModel):
    category: Category
    posts: List[Post]
