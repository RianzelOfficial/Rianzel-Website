from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException
from ..models import Post, Comment, Category, User, Like
from ..schemas import PostCreate, PostUpdate, CommentCreate, CommentUpdate

class ForumService:
    def get_posts(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        category: Optional[str] = None,
        sort_by: str = "created_at",
        order: str = "desc"
    ) -> List[Post]:
        query = db.query(Post)
        
        if category:
            query = query.join(Post.category).filter(Category.name == category)
            
        if sort_by == "created_at":
            if order == "desc":
                query = query.order_by(Post.created_at.desc())
            else:
                query = query.order_by(Post.created_at.asc())
        elif sort_by == "likes":
            query = query.outerjoin(Like).group_by(Post.id)
            if order == "desc":
                query = query.order_by(func.count(Like.id).desc())
            else:
                query = query.order_by(func.count(Like.id).asc())
        elif sort_by == "comments":
            query = query.outerjoin(Comment).group_by(Post.id)
            if order == "desc":
                query = query.order_by(func.count(Comment.id).desc())
            else:
                query = query.order_by(func.count(Comment.id).asc())
        
        return query.offset(skip).limit(limit).all()

    def get_post(self, db: Session, post_id: int) -> Post:
        post = db.query(Post).filter(Post.id == post_id).first()
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        return post

    def create_post(self, db: Session, post: PostCreate, author_id: int) -> Post:
        db_post = Post(
            title=post.title,
            content=post.content,
            category_id=post.category_id,
            author_id=author_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            views=0
        )
        db.add(db_post)
        db.commit()
        db.refresh(db_post)
        return db_post

    def update_post(self, db: Session, post_id: int, post: PostUpdate, author_id: int) -> Post:
        db_post = self.get_post(db, post_id)
        if db_post.author_id != author_id:
            raise HTTPException(status_code=403, detail="Not authorized to update this post")
        
        for key, value in post.dict(exclude_unset=True).items():
            setattr(db_post, key, value)
        
        db_post.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_post)
        return db_post

    def delete_post(self, db: Session, post_id: int, author_id: int) -> None:
        db_post = self.get_post(db, post_id)
        if db_post.author_id != author_id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this post")
        
        db.delete(db_post)
        db.commit()

    def create_comment(self, db: Session, comment: CommentCreate, author_id: int) -> Comment:
        db_comment = Comment(
            content=comment.content,
            post_id=comment.post_id,
            author_id=author_id,
            parent_id=comment.parent_id,
            created_at=datetime.utcnow()
        )
        db.add(db_comment)
        db.commit()
        db.refresh(db_comment)
        return db_comment

    def update_comment(self, db: Session, comment_id: int, comment: CommentUpdate, author_id: int) -> Comment:
        db_comment = db.query(Comment).filter(Comment.id == comment_id).first()
        if not db_comment:
            raise HTTPException(status_code=404, detail="Comment not found")
        if db_comment.author_id != author_id:
            raise HTTPException(status_code=403, detail="Not authorized to update this comment")
        
        db_comment.content = comment.content
        db.commit()
        db.refresh(db_comment)
        return db_comment

    def delete_comment(self, db: Session, comment_id: int, author_id: int) -> None:
        db_comment = db.query(Comment).filter(Comment.id == comment_id).first()
        if not db_comment:
            raise HTTPException(status_code=404, detail="Comment not found")
        if db_comment.author_id != author_id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this comment")
        
        db.delete(db_comment)
        db.commit()

    def create_like(self, db: Session, post_id: int, user_id: int) -> None:
        existing_like = db.query(Like).filter(
            Like.post_id == post_id,
            Like.user_id == user_id
        ).first()
        
        if existing_like:
            raise HTTPException(status_code=400, detail="Post already liked")
        
        db_like = Like(
            post_id=post_id,
            user_id=user_id,
            created_at=datetime.utcnow()
        )
        db.add(db_like)
        db.commit()

    def remove_like(self, db: Session, post_id: int, user_id: int) -> None:
        db_like = db.query(Like).filter(
            Like.post_id == post_id,
            Like.user_id == user_id
        ).first()
        
        if not db_like:
            raise HTTPException(status_code=404, detail="Like not found")
        
        db.delete(db_like)
        db.commit()

    def get_post_comments(self, db: Session, post_id: int, skip: int = 0, limit: int = 100) -> List[Comment]:
        return db.query(Comment).filter(Comment.post_id == post_id).offset(skip).limit(limit).all()

    def get_category_posts(self, db: Session, category_id: int, skip: int = 0, limit: int = 100) -> List[Post]:
        return db.query(Post).filter(Post.category_id == category_id).offset(skip).limit(limit).all()

    def increment_post_views(self, db: Session, post_id: int) -> None:
        db_post = self.get_post(db, post_id)
        db_post.views += 1
        db.commit()
        db.refresh(db_post)
