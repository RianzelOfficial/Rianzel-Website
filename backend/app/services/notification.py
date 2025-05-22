from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from ..models import Notification, User
from ..schemas import NotificationCreate

class NotificationService:
    def create_notification(self, db: Session, notification: NotificationCreate) -> Notification:
        db_notification = Notification(
            user_id=notification.user_id,
            message=notification.message,
            read=False,
            created_at=datetime.utcnow()
        )
        db.add(db_notification)
        db.commit()
        db.refresh(db_notification)
        return db_notification

    def get_notifications(
        self,
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 50,
        read: Optional[bool] = None
    ) -> List[Notification]:
        query = db.query(Notification).filter(Notification.user_id == user_id)
        
        if read is not None:
            query = query.filter(Notification.read == read)
            
        return query.order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()

    def mark_notification_as_read(self, db: Session, notification_id: int) -> Notification:
        notification = db.query(Notification).filter(Notification.id == notification_id).first()
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")
            
        notification.read = True
        db.commit()
        db.refresh(notification)
        return notification

    def mark_all_notifications_as_read(self, db: Session, user_id: int) -> None:
        notifications = db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.read == False
        ).all()
        
        for notification in notifications:
            notification.read = True
        
        db.commit()

    def delete_notification(self, db: Session, notification_id: int) -> None:
        notification = db.query(Notification).filter(Notification.id == notification_id).first()
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")
            
        db.delete(notification)
        db.commit()

    def get_unread_notification_count(self, db: Session, user_id: int) -> int:
        return db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.read == False
        ).count()

    def create_post_notification(self, db: Session, post_id: int, user_id: int) -> None:
        notification = Notification(
            user_id=user_id,
            message=f"New post created: {post_id}",
            read=False,
            created_at=datetime.utcnow()
        )
        db.add(notification)
        db.commit()

    def create_comment_notification(self, db: Session, comment_id: int, user_id: int) -> None:
        notification = Notification(
            user_id=user_id,
            message=f"New comment: {comment_id}",
            read=False,
            created_at=datetime.utcnow()
        )
        db.add(notification)
        db.commit()

    def create_like_notification(self, db: Session, post_id: int, user_id: int) -> None:
        notification = Notification(
            user_id=user_id,
            message=f"Your post {post_id} received a new like",
            read=False,
            created_at=datetime.utcnow()
        )
        db.add(notification)
        db.commit()
