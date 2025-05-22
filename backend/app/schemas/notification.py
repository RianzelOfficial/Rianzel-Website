from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

class NotificationBase(BaseModel):
    message: str
    read: bool = False

class NotificationCreate(NotificationBase):
    user_id: int

class Notification(NotificationBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class NotificationUpdate(BaseModel):
    read: Optional[bool] = None

class NotificationWithUser(Notification):
    user_id: int

    class Config:
        from_attributes = True

class NotificationList(BaseModel):
    notifications: List[Notification]
    total_count: int
    unread_count: int
