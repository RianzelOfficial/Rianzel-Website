from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from ..services import profile
from ..schemas import profile as schemas
from ..database import get_db
from ..security import get_current_user

router = APIRouter()

@router.get("/profile", response_model=schemas.ProfileResponse)
async def get_profile(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    profile_data = profile.get_user_profile(db, current_user.id)
    return schemas.ProfileResponse(
        profile=profile_data["user"],
        stats=schemas.ProfileStats(
            posts=profile_data["posts_count"],
            comments=profile_data["comments_count"],
            likes=profile_data["likes_count"]
        ),
        activity=profile_data["activity"],
        preferences=profile_data["preferences"],
        notifications=profile_data["notifications"]
    )

@router.put("/profile", response_model=schemas.Profile)
async def update_profile(
    profile: schemas.ProfileUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return profile.update_profile(db, current_user.id, profile)

@router.get("/profile/stats", response_model=schemas.ProfileStats)
async def get_profile_stats(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    stats = profile.get_user_stats(db, current_user.id)
    return schemas.ProfileStats(**stats)

@router.get("/profile/activity", response_model=List[schemas.ProfileActivityItem])
async def get_profile_activity(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return profile.get_user_activity(db, current_user.id, skip, limit)

@router.get("/profile/preferences", response_model=schemas.ProfilePreferences)
async def get_profile_preferences(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return profile.get_user_preferences(db, current_user.id)

@router.put("/profile/preferences", response_model=schemas.Profile)
async def update_profile_preferences(
    preferences: schemas.ProfilePreferences,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return profile.update_user_preferences(db, current_user.id, preferences)

@router.get("/profile/notifications", response_model=List[schemas.ProfileNotification])
async def get_profile_notifications(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return profile.get_user_notifications(db, current_user.id, skip, limit)

@router.put("/profile/notifications/{notification_id}/read", response_model=schemas.ProfileNotification)
async def mark_notification_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return profile.mark_notification_as_read(db, notification_id)

@router.put("/profile/notifications/read-all", response_model=List[schemas.ProfileNotification])
async def mark_all_notifications_as_read(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    notifications = profile.get_user_notifications(db, current_user.id, 0, 50)
    profile.mark_all_notifications_as_read(db, current_user.id)
    return notifications

@router.get("/profile/notifications/unread-count", response_model=int)
async def get_unread_notification_count(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return profile.get_unread_notification_count(db, current_user.id)
