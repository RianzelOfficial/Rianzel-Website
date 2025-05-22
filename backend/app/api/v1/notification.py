from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from ..services import notification
from ..schemas import notification as schemas
from ..database import get_db
from ..security import get_current_user

router = APIRouter()

@router.post("/notifications", response_model=schemas.Notification)
async def create_notification(
    notification: schemas.NotificationCreate,
    db: Session = Depends(get_db)
):
    return notification.create_notification(db, notification)

@router.get("/notifications", response_model=schemas.NotificationList)
async def get_notifications(
    skip: int = 0,
    limit: int = 50,
    read: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    notifications = notification.get_notifications(
        db, current_user.id, skip, limit, read
    )
    total_count = notification.get_unread_notification_count(db, current_user.id)
    unread_count = notification.get_unread_notification_count(db, current_user.id)
    
    return schemas.NotificationList(
        notifications=notifications,
        total_count=total_count,
        unread_count=unread_count
    )

@router.put("/notifications/{notification_id}/read", response_model=schemas.Notification)
async def mark_notification_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return notification.mark_notification_as_read(db, notification_id)

@router.put("/notifications/read-all", response_model=schemas.NotificationList)
async def mark_all_notifications_as_read(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    notification.mark_all_notifications_as_read(db, current_user.id)
    notifications = notification.get_notifications(
        db, current_user.id, 0, 50
    )
    total_count = notification.get_unread_notification_count(db, current_user.id)
    unread_count = notification.get_unread_notification_count(db, current_user.id)
    
    return schemas.NotificationList(
        notifications=notifications,
        total_count=total_count,
        unread_count=unread_count
    )

@router.delete("/notifications/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    notification.delete_notification(db, notification_id)

@router.get("/notifications/unread-count", response_model=int)
async def get_unread_notification_count(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return notification.get_unread_notification_count(db, current_user.id)

@router.post("/notifications/post", response_model=schemas.Notification)
async def create_post_notification(
    post_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return notification.create_post_notification(db, post_id, current_user.id)

@router.post("/notifications/comment", response_model=schemas.Notification)
async def create_comment_notification(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return notification.create_comment_notification(db, comment_id, current_user.id)

@router.post("/notifications/like", response_model=schemas.Notification)
async def create_like_notification(
    post_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return notification.create_like_notification(db, post_id, current_user.id)
