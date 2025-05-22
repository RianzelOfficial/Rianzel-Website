from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models import User, Post, Comment, Like, Notification
from ..schemas import ProfileUpdate

class ProfileService:
    def get_user_profile(self, db: Session, user_id: int) -> dict:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        # Get user statistics
        posts_count = db.query(Post).filter(Post.author_id == user_id).count()
        comments_count = db.query(Comment).filter(Comment.author_id == user_id).count()
        likes_count = db.query(Like).filter(Like.user_id == user_id).count()
        
        # Get user's posts
        posts = db.query(Post).filter(Post.author_id == user_id).order_by(Post.created_at.desc()).all()
        
        # Get user's comments
        comments = db.query(Comment).filter(Comment.author_id == user_id).order_by(Comment.created_at.desc()).all()
        
        # Get user's likes
        likes = db.query(Like).filter(Like.user_id == user_id).order_by(Like.created_at.desc()).all()
        
        # Get user's notifications
        notifications = db.query(Notification).filter(Notification.user_id == user_id).order_by(Notification.created_at.desc()).all()
        
        return {
            "user": user,
            "posts_count": posts_count,
            "comments_count": comments_count,
            "likes_count": likes_count,
            "posts": posts,
            "comments": comments,
            "likes": likes,
            "notifications": notifications
        }

    def update_profile(self, db: Session, user_id: int, profile: ProfileUpdate) -> User:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        for key, value in profile.dict(exclude_unset=True).items():
            setattr(user, key, value)
        
        db.commit()
        db.refresh(user)
        return user

    def get_user_stats(self, db: Session, user_id: int) -> dict:
        posts = db.query(Post).filter(Post.author_id == user_id).count()
        comments = db.query(Comment).filter(Comment.author_id == user_id).count()
        likes = db.query(Like).filter(Like.user_id == user_id).count()
        
        return {
            "posts": posts,
            "comments": comments,
            "likes": likes
        }

    def get_user_activity(self, db: Session, user_id: int, skip: int = 0, limit: int = 50) -> list:
        activity = []
        
        # Get posts
        posts = db.query(Post).filter(Post.author_id == user_id).order_by(Post.created_at.desc()).all()
        activity.extend([{
            "type": "post",
            "content": post.content[:100] + "...",
            "created_at": post.created_at
        } for post in posts])
        
        # Get comments
        comments = db.query(Comment).filter(Comment.author_id == user_id).order_by(Comment.created_at.desc()).all()
        activity.extend([{
            "type": "comment",
            "content": comment.content[:100] + "...",
            "created_at": comment.created_at
        } for comment in comments])
        
        # Get likes
        likes = db.query(Like).filter(Like.user_id == user_id).order_by(Like.created_at.desc()).all()
        activity.extend([{
            "type": "like",
            "post_id": like.post_id,
            "created_at": like.created_at
        } for like in likes])
        
        # Sort activity by date
        activity.sort(key=lambda x: x["created_at"], reverse=True)
        
        return activity[skip:skip+limit]

    def get_user_preferences(self, db: Session, user_id: int) -> dict:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        return {
            "theme": user.theme_preference,
            "notification_settings": user.notification_settings,
            "privacy_settings": user.privacy_settings
        }

    def update_user_preferences(self, db: Session, user_id: int, preferences: dict) -> User:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        if "theme" in preferences:
            user.theme_preference = preferences["theme"]
        if "notification_settings" in preferences:
            user.notification_settings = preferences["notification_settings"]
        if "privacy_settings" in preferences:
            user.privacy_settings = preferences["privacy_settings"]
        
        db.commit()
        db.refresh(user)
        return user

    def get_user_notifications(self, db: Session, user_id: int, skip: int = 0, limit: int = 50) -> list:
        return db.query(Notification).filter(
            Notification.user_id == user_id
        ).order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()

    def mark_notification_as_read(self, db: Session, notification_id: int) -> None:
        notification = db.query(Notification).filter(Notification.id == notification_id).first()
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")
            
        notification.read = True
        db.commit()

    def mark_all_notifications_as_read(self, db: Session, user_id: int) -> None:
        notifications = db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.read == False
        ).all()
        
        for notification in notifications:
            notification.read = True
        
        db.commit()
