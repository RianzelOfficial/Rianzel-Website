from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from ..services import forum
from ..schemas import forum as schemas
from ..database import get_db
from ..security import get_current_user

router = APIRouter()

@router.post("/posts", response_model=schemas.Post)
async def create_post(
    post: schemas.PostCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return forum.create_post(db, post, current_user.id)

@router.get("/posts", response_model=List[schemas.Post])
async def get_posts(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    sort_by: str = "created_at",
    order: str = "desc",
    db: Session = Depends(get_db)
):
    return forum.get_posts(db, skip, limit, category, sort_by, order)

@router.get("/posts/{post_id}", response_model=schemas.PostWithComments)
async def get_post(
    post_id: int,
    db: Session = Depends(get_db)
):
    post = forum.get_post(db, post_id)
    comments = forum.get_post_comments(db, post_id)
    return schemas.PostWithComments(post=post, comments=comments)

@router.put("/posts/{post_id}", response_model=schemas.Post)
async def update_post(
    post_id: int,
    post: schemas.PostUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return forum.update_post(db, post_id, post, current_user.id)

@router.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    forum.delete_post(db, post_id, current_user.id)

@router.post("/comments", response_model=schemas.Comment)
async def create_comment(
    comment: schemas.CommentCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return forum.create_comment(db, comment, current_user.id)

@router.put("/comments/{comment_id}", response_model=schemas.Comment)
async def update_comment(
    comment_id: int,
    comment: schemas.CommentUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return forum.update_comment(db, comment_id, comment, current_user.id)

@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    forum.delete_comment(db, comment_id, current_user.id)

@router.post("/likes", response_model=schemas.Like)
async def create_like(
    like: schemas.LikeCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return forum.create_like(db, like.post_id, current_user.id)

@router.delete("/likes/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_like(
    post_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    forum.remove_like(db, post_id, current_user.id)

@router.get("/categories", response_model=List[schemas.Category])
async def get_categories(
    db: Session = Depends(get_db)
):
    return db.query(schemas.Category).all()

@router.post("/categories", response_model=schemas.Category)
async def create_category(
    category: schemas.CategoryCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create categories"
        )
    return forum.create_category(db, category)

@router.get("/posts/{post_id}/views", response_model=schemas.Post)
async def increment_post_views(
    post_id: int,
    db: Session = Depends(get_db)
):
    post = forum.increment_post_views(db, post_id)
    return post
