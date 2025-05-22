from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from ..services import admin as admin_service
from ..schemas import admin as schemas
from ..database import get_db
from ..auth import get_current_user
from ..models import User

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(get_current_user)],
)

# Dashboard
@router.get("/dashboard/stats", response_model=schemas.AdminDashboardStats)
async def get_dashboard_stats(db: Session = Depends(get_db)):
    return await admin_service.get_dashboard_stats(db)

# Activity Logs
@router.get("/logs/activity", response_model=schemas.AdminActivityLogList)
async def get_activity_logs(
    page: int = 1,
    page_size: int = 20,
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    resource: Optional[str] = None,
    resource_id: Optional[int] = None,
    status: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    db: Session = Depends(get_db)
):
    return await admin_service.get_activity_logs(
        db,
        page,
        page_size,
        user_id,
        action,
        resource,
        resource_id,
        status,
        start_date,
        end_date,
        sort_by,
        sort_order
    )

# Notifications
@router.get("/notifications", response_model=schemas.AdminNotificationList)
async def get_notifications(
    page: int = 1,
    page_size: int = 20,
    user_id: Optional[int] = None,
    type: Optional[str] = None,
    status: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    db: Session = Depends(get_db)
):
    return await admin_service.get_notifications(
        db,
        page,
        page_size,
        user_id,
        type,
        status,
        start_date,
        end_date,
        sort_by,
        sort_order
    )

@router.post("/notifications/{notification_id}/read")
async def mark_notification_as_read(
    notification_id: int,
    db: Session = Depends(get_db)
):
    return await admin_service.mark_notification_as_read(db, notification_id)

@router.post("/notifications/read-all")
async def mark_all_notifications_as_read(db: Session = Depends(get_db)):
    return await admin_service.mark_all_notifications_as_read(db)

# Role Management
@router.get("/roles", response_model=schemas.AdminRoleList)
async def get_roles(
    page: int = 1,
    page_size: int = 20,
    name: Optional[str] = None,
    status: Optional[str] = None,
    sort_by: str = "name",
    sort_order: str = "asc",
    db: Session = Depends(get_db)
):
    return await admin_service.get_roles(
        db,
        page,
        page_size,
        name,
        status,
        sort_by,
        sort_order
    )

@router.post("/roles", response_model=schemas.AdminRole)
async def create_role(
    role: schemas.AdminRoleCreate,
    db: Session = Depends(get_db)
):
    return await admin_service.create_role(db, role)

@router.put("/roles/{role_id}", response_model=schemas.AdminRole)
async def update_role(
    role_id: int,
    role: schemas.AdminRoleUpdate,
    db: Session = Depends(get_db)
):
    return await admin_service.update_role(db, role_id, role)

@router.delete("/roles/{role_id}")
async def delete_role(
    role_id: int,
    db: Session = Depends(get_db)
):
    return await admin_service.delete_role(db, role_id)

# Role Assignments
@router.get("/roles/assignments", response_model=schemas.AdminRoleAssignmentList)
async def get_role_assignments(
    page: int = 1,
    page_size: int = 20,
    user_id: Optional[int] = None,
    role_id: Optional[int] = None,
    status: Optional[str] = None,
    sort_by: str = "assigned_at",
    sort_order: str = "desc",
    db: Session = Depends(get_db)
):
    return await admin_service.get_role_assignments(
        db,
        page,
        page_size,
        user_id,
        role_id,
        status,
        sort_by,
        sort_order
    )

@router.post("/roles/assign", response_model=schemas.AdminRoleAssignment)
async def assign_role(
    assignment: schemas.AdminRoleAssignmentCreate,
    db: Session = Depends(get_db)
):
    return await admin_service.assign_role(db, assignment)

# Content Moderation
@router.get("/moderation/logs", response_model=schemas.ModerationLogList)
async def get_moderation_logs(
    page: int = 1,
    page_size: int = 20,
    moderator_id: Optional[int] = None,
    content_type: Optional[str] = None,
    action: Optional[str] = None,
    status: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    db: Session = Depends(get_db)
):
    return await admin_service.get_moderation_logs(
        db,
        page,
        page_size,
        moderator_id,
        content_type,
        action,
        status,
        start_date,
        end_date,
        sort_by,
        sort_order
    )

@router.post("/moderation/action")
async def moderate_content(
    action: schemas.ModerationAction,
    db: Session = Depends(get_db)
):
    return await admin_service.moderate_content(db, action)

@router.post("/moderation/{content_type}/{content_id}/approve")
async def approve_content(
    content_type: str,
    content_id: int,
    db: Session = Depends(get_db)
):
    return await admin_service.approve_content(db, content_type, content_id)

@router.post("/moderation/{content_type}/{content_id}/reject")
async def reject_content(
    content_type: str,
    content_id: int,
    reason: str,
    db: Session = Depends(get_db)
):
    return await admin_service.reject_content(db, content_type, content_id, reason)

@router.delete("/moderation/{content_type}/{content_id}")
async def delete_content(
    content_type: str,
    content_id: int,
    db: Session = Depends(get_db)
):
    return await admin_service.delete_content(db, content_type, content_id)

# Categories
@router.get("/categories", response_model=schemas.CategoryList)
async def get_categories(
    page: int = 1,
    page_size: int = 20,
    name: Optional[str] = None,
    status: Optional[str] = None,
    sort_by: str = "name",
    sort_order: str = "asc",
    db: Session = Depends(get_db)
):
    return await admin_service.get_categories(
        db,
        page,
        page_size,
        name,
        status,
        sort_by,
        sort_order
    )

@router.post("/categories", response_model=schemas.Category)
async def create_category(
    category: schemas.CategoryCreate,
    db: Session = Depends(get_db)
):
    return await admin_service.create_category(db, category)

@router.put("/categories/{category_id}", response_model=schemas.Category)
async def update_category(
    category_id: int,
    category: schemas.CategoryUpdate,
    db: Session = Depends(get_db)
):
    return await admin_service.update_category(db, category_id, category)

@router.delete("/categories/{category_id}")
async def delete_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    return await admin_service.delete_category(db, category_id)

# User Management
@router.get("/users/{user_id}/activity", response_model=schemas.AdminActivityLogList)
async def get_user_activity(
    user_id: int,
    page: int = 1,
    page_size: int = 20,
    action: Optional[str] = None,
    resource: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    db: Session = Depends(get_db)
):
    return await admin_service.get_user_activity(
        db,
        user_id,
        page,
        page_size,
        action,
        resource,
        start_date,
        end_date,
        sort_by,
        sort_order
    )

@router.get("/users/{user_id}/notifications", response_model=schemas.AdminNotificationList)
async def get_user_notifications(
    user_id: int,
    page: int = 1,
    page_size: int = 20,
    type: Optional[str] = None,
    status: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    db: Session = Depends(get_db)
):
    return await admin_service.get_user_notifications(
        db,
        user_id,
        page,
        page_size,
        type,
        status,
        start_date,
        end_date,
        sort_by,
        sort_order
    )

@router.post("/users/{user_id}/ban")
async def ban_user(
    user_id: int,
    reason: str,
    duration: Optional[str] = None,
    db: Session = Depends(get_db)
):
    return await admin_service.ban_user(db, user_id, reason, duration)

@router.post("/users/{user_id}/unban")
async def unban_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    return await admin_service.unban_user(db, user_id)
