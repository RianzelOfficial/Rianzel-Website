from fastapi import HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from ..models import (
    User, Post, Comment, Category, Like, Notification,
    Role, ActivityLog, ModerationLog, RoleAssignment
)
from ..schemas import admin as schemas
from ..security import get_password_hash
from ..utils import calculate_storage_usage, calculate_bandwidth_usage
from ..config import settings
from ..database import get_db
from ..auth import get_current_user
from ..services import websocket

# Constants for moderation
MODERATION_ACTIONS = {
    'approve': 'approved',
    'reject': 'rejected',
    'delete': 'deleted'
}

# Constants for role assignments
ROLE_ASSIGNMENT_STATUS = {
    'pending': 'Pending Review',
    'approved': 'Approved',
    'rejected': 'Rejected'
}

# Constants for notifications
NOTIFICATION_TYPES = {
    'MODERATION': 'moderation',
    'ROLE_ASSIGNMENT': 'role_assignment',
    'SYSTEM': 'system',
    'USER_ACTION': 'user_action'
}

# Constants for user status
USER_STATUS = {
    'ACTIVE': 'active',
    'BANNED': 'banned',
    'SUSPENDED': 'suspended'
}

# Constants for content status
CONTENT_STATUS = {
    'ACTIVE': 'active',
    'PENDING': 'pending',
    'REJECTED': 'rejected',
    'DELETED': 'deleted'
}

class AdminService:
    def __init__(self, db):
        self.db = db
        self.now = datetime.utcnow()
        
    # Content Management Methods
    def get_content(self, content_id: int, content_type: str) -> Dict[str, Any]:
        """Retrieve a single content item by ID and type."""
        if content_type == "post":
            content = self.db.query(Post).filter(Post.id == content_id).first()
        elif content_type == "comment":
            content = self.db.query(Comment).filter(Comment.id == content_id).first()
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid content type: {content_type}"
            )
            
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{content_type.capitalize()} with ID {content_id} not found"
            )
        return content

    def list_contents(
        self,
        content_type: str,
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = None,
        category_id: Optional[int] = None,
        author_id: Optional[int] = None,
        search: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> Dict[str, Any]:
        """List contents with filtering, sorting, and pagination."""
        if content_type == "post":
            query = self.db.query(Post)
        elif content_type == "comment":
            query = self.db.query(Comment)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid content type: {content_type}"
            )
        
        # Apply filters
        if status:
            query = query.filter(Post.status == status)
        if category_id and content_type == "post":
            query = query.filter(Post.category_id == category_id)
        if author_id:
            query = query.filter(Post.author_id == author_id)
        if search:
            search_filter = or_(
                Post.title.ilike(f"%{search}%"),
                Post.content.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        # Apply sorting
        sort_column = getattr(Post, sort_by, None)
        if sort_column is None:
            sort_column = Post.created_at
            
        if sort_order.lower() == "asc":
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())
        
        # Apply pagination
        total = query.count()
        items = query.offset((page - 1) * page_size).limit(page_size).all()
        
        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": (total + page_size - 1) // page_size
        }

    def update_content(
        self,
        content_id: int,
        content_type: str,
        update_data: Dict[str, Any],
        updated_by: int
    ) -> Dict[str, Any]:
        """Update content with moderation logging."""
        content = self.get_content(content_id, content_type)
        
        # Log the update
        log = ModerationLog(
            content_id=content_id,
            content_type=content_type,
            action="update",
            moderator_id=updated_by,
            details={"changes": update_data}
        )
        self.db.add(log)
        
        # Update fields
        for key, value in update_data.items():
            if hasattr(content, key):
                setattr(content, key, value)
        
        content.updated_at = self.now
        self.db.commit()
        self.db.refresh(content)
        return content

    # Settings Management Methods
    def get_site_settings(self) -> Dict[str, Any]:
        """Retrieve all site settings."""
        # This would typically come from a settings table in the database
        # For now, returning a placeholder
        return {
            "site_name": settings.SITE_NAME,
            "site_description": settings.SITE_DESCRIPTION,
            "contact_email": settings.CONTACT_EMAIL,
            "maintenance_mode": settings.MAINTENANCE_MODE,
            "registration_open": settings.REGISTRATION_OPEN,
            "max_upload_size": settings.MAX_UPLOAD_SIZE,
            "allowed_file_types": settings.ALLOWED_FILE_TYPES,
            "default_user_role": settings.DEFAULT_USER_ROLE
        }

    def update_site_settings(self, settings_data: Dict[str, Any], updated_by: int) -> Dict[str, Any]:
        """Update site settings."""
        # In a real implementation, this would update a settings table
        # For now, we'll just log the update and return the new settings
        log = ActivityLog(
            user_id=updated_by,
            action="update_site_settings",
            details={"changes": settings_data}
        )
        self.db.add(log)
        self.db.commit()
        
        # Return the new settings (in a real app, these would be saved to the database)
        return {**self.get_site_settings(), **settings_data}

    # Helper Methods
    def _get_content_query(self, content_type: str):
        """Get the appropriate query object for the content type."""
        if content_type == "post":
            return self.db.query(Post)
        elif content_type == "comment":
            return self.db.query(Comment)
        raise ValueError(f"Unsupported content type: {content_type}")

    # Role Management Methods
    def create_role(self, role_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new role with permissions."""
        # Validate role data
        required_fields = ['name', 'permissions']
        if not all(field in role_data for field in required_fields):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing required fields: name, permissions"
            )

        # Check if role name already exists
        existing_role = self.db.query(Role).filter_by(name=role_data['name']).first()
        if existing_role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Role '{role_data['name']}' already exists"
            )

        # Create role
        role = Role(
            name=role_data['name'],
            permissions=role_data['permissions'],
            created_at=self.now
        )
        self.db.add(role)
        self.db.commit()
        self.db.refresh(role)
        return role

    def update_role(self, role_id: int, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing role."""
        role = self.db.query(Role).filter_by(id=role_id).first()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role with ID {role_id} not found"
            )

        # Update fields
        for key, value in update_data.items():
            if hasattr(role, key):
                setattr(role, key, value)

        role.updated_at = self.now
        self.db.commit()
        self.db.refresh(role)
        return role

    def delete_role(self, role_id: int) -> None:
        """Delete a role."""
        role = self.db.query(Role).filter_by(id=role_id).first()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role with ID {role_id} not found"
            )

        # Check if role is assigned to any users
        if self.db.query(RoleAssignment).filter_by(role_id=role_id).count() > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete role {role.name} as it is assigned to users"
            )

        self.db.delete(role)
        self.db.commit()

    # User Management Methods
    def assign_role(self, user_id: int, role_id: int, assigned_by: int) -> Dict[str, Any]:
        """Assign a role to a user."""
        # Validate user
        user = self.db.query(User).filter_by(id=user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )

        # Validate role
        role = self.db.query(Role).filter_by(id=role_id).first()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role with ID {role_id} not found"
            )

        # Check if role is already assigned
        existing_assignment = self.db.query(RoleAssignment).filter_by(
            user_id=user_id,
            role_id=role_id
        ).first()
        if existing_assignment:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User already has role {role.name}"
            )

        # Create role assignment
        assignment = RoleAssignment(
            user_id=user_id,
            role_id=role_id,
            assigned_by=assigned_by,
            status="active",
            created_at=self.now
        )
        self.db.add(assignment)
        self.db.commit()
        self.db.refresh(assignment)

        # Log the action
        log = ActivityLog(
            user_id=assigned_by,
            action="assign_role",
            details={
                "user_id": user_id,
                "role_id": role_id,
                "role_name": role.name
            }
        )
        self.db.add(log)
        self.db.commit()

        return assignment

    def remove_role(self, user_id: int, role_id: int, removed_by: int) -> None:
        """Remove a role from a user."""
        assignment = self.db.query(RoleAssignment).filter_by(
            user_id=user_id,
            role_id=role_id
        ).first()
        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role assignment not found"
            )

        # Log the action
        log = ActivityLog(
            user_id=removed_by,
            action="remove_role",
            details={
                "user_id": user_id,
                "role_id": role_id,
                "role_name": assignment.role.name
            }
        )
        self.db.add(log)

        self.db.delete(assignment)
        self.db.commit()

    # Moderation Methods
    def moderate_content(self, content_id: int, content_type: str, action: str, moderator_id: int, reason: str) -> Dict[str, Any]:
        """Moderate content (approve, reject, delete)."""
        content = self.get_content(content_id, content_type)
        
        # Validate action
        valid_actions = ['approve', 'reject', 'delete']
        if action not in valid_actions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid action: {action}"
            )

        # Create moderation log
        log = ModerationLog(
            content_id=content_id,
            content_type=content_type,
            action=action,
            moderator_id=moderator_id,
            reason=reason,
            created_at=self.now
        )
        self.db.add(log)

        # Apply moderation action
        if action == 'approve':
            content.status = 'active'
        elif action == 'reject':
            content.status = 'rejected'
        elif action == 'delete':
            content.status = 'deleted'

        content.updated_at = self.now
        self.db.commit()
        self.db.refresh(content)

        return content

    def ban_user(self, user_id: int, moderator_id: int, ban_type: str, duration: int, reason: str) -> Dict[str, Any]:
        """Ban or suspend a user."""
        user = self.db.query(User).filter_by(id=user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )

        # Validate ban type
        valid_ban_types = ['temporary', 'permanent']
        if ban_type not in valid_ban_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid ban type: {ban_type}"
            )

        # Create ban log
        ban_log = ModerationLog(
            content_id=None,
            content_type='user',
            action=f"ban_{ban_type}",
            moderator_id=moderator_id,
            reason=reason,
            details={
                "duration_days": duration,
                "ban_type": ban_type
            },
            created_at=self.now
        )
        self.db.add(ban_log)

        # Apply ban
        user.is_active = False
        user.ban_reason = reason
        if ban_type == 'temporary':
            user.ban_expires_at = self.now + timedelta(days=duration)
        else:
            user.ban_expires_at = None

        user.updated_at = self.now
        self.db.commit()
        self.db.refresh(user)

        return user

    def unban_user(self, user_id: int, moderator_id: int) -> Dict[str, Any]:
        """Unban a user."""
        user = self.db.query(User).filter_by(id=user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )

        # Create unban log
        unban_log = ModerationLog(
            content_id=None,
            content_type='user',
            action="unban",
            moderator_id=moderator_id,
            reason="Manual unban by moderator",
            created_at=self.now
        )
        self.db.add(unban_log)

        # Remove ban
        user.is_active = True
        user.ban_reason = None
        user.ban_expires_at = None
        user.updated_at = self.now

        self.db.commit()
        self.db.refresh(user)

        return user

    # Category Management Methods
    def create_category(self, category_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new forum category."""
        required_fields = ['name', 'description', 'parent_id', 'permissions']
        if not all(field in category_data for field in required_fields):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required fields: {required_fields}"
            )

        # Validate parent category if provided
        if category_data['parent_id']:
            parent = self.db.query(Category).filter_by(id=category_data['parent_id']).first()
            if not parent:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Parent category with ID {category_data['parent_id']} not found"
                )

        # Create category
        category = Category(
            name=category_data['name'],
            description=category_data['description'],
            parent_id=category_data['parent_id'],
            permissions=category_data['permissions'],
            created_at=self.now
        )
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)

        return category

    def update_category(self, category_id: int, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing category."""
        category = self.db.query(Category).filter_by(id=category_id).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with ID {category_id} not found"
            )

        # Update fields
        for key, value in update_data.items():
            if hasattr(category, key):
                setattr(category, key, value)

        category.updated_at = self.now
        self.db.commit()
        self.db.refresh(category)

        return category

    def delete_category(self, category_id: int) -> None:
        """Delete a category."""
        category = self.db.query(Category).filter_by(id=category_id).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with ID {category_id} not found"
            )

        # Check if category has posts
        if self.db.query(Post).filter_by(category_id=category_id).count() > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete category as it contains posts"
            )

        self.db.delete(category)
        self.db.commit()

    async def get_dashboard_stats(self) -> schemas.AdminDashboardStats:
        # Get basic stats
        stats = {
            "total_users": self.db.query(User).count(),
            "active_users": self.db.query(User).filter(User.is_active == True).count(),
            "new_users_today": self.db.query(User).filter(
                User.created_at >= datetime.utcnow() - timedelta(days=1)
            ).count(),
            "active_users_7d": self.db.query(User).filter(
                User.last_login >= datetime.utcnow() - timedelta(days=7)
            ).count(),
            "total_posts": self.db.query(Post).count(),
            "active_posts": self.db.query(Post).filter(Post.status == "active").count(),
            "new_posts_today": self.db.query(Post).filter(
                Post.created_at >= datetime.utcnow() - timedelta(days=1)
            ).count(),
            "total_comments": self.db.query(Comment).count(),
            "new_comments_today": self.db.query(Comment).filter(
                Comment.created_at >= datetime.utcnow() - timedelta(days=1)
            ).count(),
            "avg_comments_per_post": self.db.query(Comment).count() / self.db.query(Post).count() if self.db.query(Post).count() > 0 else 0,
            "avg_likes_per_post": self.db.query(Like).count() / self.db.query(Post).count() if self.db.query(Post).count() > 0 else 0,
            "pending_moderation": self.db.query(Post).filter(Post.status == "pending").count(),
            "reported_content": self.db.query(Post).filter(Post.is_reported == True).count() + self.db.query(Comment).filter(Comment.is_reported == True).count(),
            "storage_usage": await calculate_storage_usage(self.db),
            "bandwidth_usage": await calculate_bandwidth_usage(self.db),
            "active_categories": self.db.query(Category).filter(Category.status == "active").count()
        }

        # Get moderation stats
        moderation_stats = {
            "pending": self.db.query(Post).filter(Post.status == "pending").count(),
            "approved_today": self.db.query(Post).filter(
                Post.status == "active",
                Post.updated_at >= datetime.utcnow() - timedelta(days=1)
            ).count(),
            "rejected_today": self.db.query(Post).filter(
                Post.status == "rejected",
                Post.updated_at >= datetime.utcnow() - timedelta(days=1)
            ).count(),
            "by_category": {
                cat.name: self.db.query(Post).filter(
                    Post.category_id == cat.id,
                    Post.status == "active"
                ).count()
                for cat in self.db.query(Category).all()
            }
        }

        stats["moderation_stats"] = schemas.ModerationStats(**moderation_stats)
        return schemas.AdminDashboardStats(**stats)

    async def get_roles(self, filters: dict = None) -> schemas.RoleListResponse:
        query = self.db.query(Role)
        
        if filters:
            if filters.get("name"):
                query = query.filter(Role.name.ilike(f"%{filters['name']}%"))
            if filters.get("status"):
                query = query.filter(Role.status == filters["status"])

        total = query.count()
        roles = query.all()
        
        return schemas.RoleListResponse(
            roles=roles,
            total=total,
            page=1,
            pages=1
        )

    async def create_role(self, role_data: schemas.RoleCreate) -> schemas.Role:
        role = Role(**role_data.dict())
        self.db.add(role)
        self.db.commit()
        self.db.refresh(role)
        return schemas.Role.from_orm(role)

    async def update_role(self, role_id: int, role_data: schemas.RoleUpdate) -> schemas.Role:
        role = self.db.query(Role).filter(Role.id == role_id).first()
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")

        for key, value in role_data.dict(exclude_unset=True).items():
            setattr(role, key, value)
        
        self.db.commit()
        self.db.refresh(role)
        return schemas.Role.from_orm(role)

    async def delete_role(self, role_id: int) -> None:
        role = self.db.query(Role).filter(Role.id == role_id).first()
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        
        self.db.delete(role)
        self.db.commit()

    async def get_moderation_queue(self, filters: dict = None) -> schemas.ModerationQueueList:
        query = self.db.query(Post).filter(Post.status == "pending")
        
        if filters:
            if filters.get("content_type"):
                query = query.filter(Post.type == filters["content_type"])
            if filters.get("category"):
                query = query.filter(Post.category_id == filters["category"])

        total = query.count()
        queue = query.all()
        
        return schemas.ModerationQueueList(
            queue=[{
                "id": post.id,
                "content_id": post.id,
                "content_type": post.type,
                "title": post.title,
                "content": post.content,
                "author": post.author.username,
                "category": post.category.name if post.category else "",
                "status": post.status,
                "created_at": post.created_at
            } for post in queue],
            total=total,
            page=1,
            pages=1
        )

    async def approve_content(self, content_id: int, content_type: str) -> None:
        if content_type == "post":
            content = self.db.query(Post).filter(Post.id == content_id).first()
        else:
            content = self.db.query(Comment).filter(Comment.id == content_id).first()

        if not content:
            raise HTTPException(status_code=404, detail="Content not found")

        content.status = "active"
        self.db.commit()

    async def reject_content(self, content_id: int, content_type: str, reason: str) -> None:
        if content_type == "post":
            content = self.db.query(Post).filter(Post.id == content_id).first()
        else:
            content = self.db.query(Comment).filter(Comment.id == content_id).first()

        if not content:
            raise HTTPException(status_code=404, detail="Content not found")

        content.status = "rejected"
        content.rejection_reason = reason
        self.db.commit()

    async def get_categories(self, filters: dict = None) -> schemas.CategoryList:
        query = self.db.query(Category)
        
        if filters:
            if filters.get("name"):
                query = query.filter(Category.name.ilike(f"%{filters['name']}%"))
            if filters.get("status"):
                query = query.filter(Category.status == filters["status"])
            if filters.get("content_type"):
                query = query.filter(Category.content_type == filters["content_type"])

        total = query.count()
        categories = query.all()
        
        return schemas.CategoryList(
            categories=categories,
            total=total,
            page=1,
            pages=1
        )

    async def create_category(self, category_data: schemas.CategoryCreate) -> schemas.Category:
        category = Category(**category_data.dict())
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return schemas.Category.from_orm(category)

    async def update_category(self, category_id: int, category_data: schemas.CategoryUpdate) -> schemas.Category:
        category = self.db.query(Category).filter(Category.id == category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

        for key, value in category_data.dict(exclude_unset=True).items():
            setattr(category, key, value)
        
        self.db.commit()
        self.db.refresh(category)
        return schemas.Category.from_orm(category)

    async def delete_category(self, category_id: int) -> None:
        category = self.db.query(Category).filter(Category.id == category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        
        self.db.delete(category)
        self.db.commit()

    def get_dashboard_stats(self) -> schemas.AdminDashboardStats:
        stats = {
            "total_users": self.db.query(models.User).count(),
            "active_users": self.db.query(models.User).filter(models.User.is_active == True).count(),
            "new_users": self.db.query(models.User).filter(
                models.User.created_at >= datetime.now() - timedelta(days=7)
            ).count(),
            "total_posts": self.db.query(models.Post).count(),
            "total_comments": self.db.query(models.Comment).count(),
            "total_categories": self.db.query(models.Category).count(),
            "moderation_queue": self.db.query(models.Content).filter(
                models.Content.status == "pending"
            ).count(),
            "pending_approvals": self.db.query(models.Content).filter(
                models.Content.status == "pending"
            ).count(),
            "pending_reports": self.db.query(models.Report).filter(
                models.Report.status == "pending"
            ).count()
        }
        return schemas.AdminDashboardStats(**stats)

    def get_activity_logs(
        self,
        skip: int = 0,
        limit: int = 100,
        username: Optional[str] = None,
        action: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> schemas.AdminActivityLogList:
        query = self.db.query(models.ActivityLog)
        
        if username:
            query = query.join(models.User).filter(models.User.username.ilike(f"%{username}%"))
        if action:
            query = query.filter(models.ActivityLog.action == action)
        if start_date:
            query = query.filter(models.ActivityLog.created_at >= start_date)
        if end_date:
            query = query.filter(models.ActivityLog.created_at <= end_date)

        total = query.count()
        logs = query.offset(skip).limit(limit).all()
        
        return schemas.AdminActivityLogList(
            logs=[schemas.AdminActivityLog(
                id=log.id,
                user_id=log.user_id,
                action=log.action,
                description=log.description,
                ip_address=log.ip_address,
                created_at=log.created_at,
                user=log.user
            ) for log in logs],
            total=total
        )

    def create_notification(
        self,
        notification: schemas.AdminNotificationCreate
    ) -> schemas.AdminNotification:
        db_notification = models.Notification(
            title=notification.title,
            message=notification.message,
            type=notification.type,
            recipient_id=notification.recipient_id,
            system=notification.system
        )
        self.db.add(db_notification)
        self.db.commit()
        self.db.refresh(db_notification)
        return schemas.AdminNotification.from_orm(db_notification)

    def get_notifications(
        self,
        skip: int = 0,
        limit: int = 100,
        type: Optional[str] = None,
        status: Optional[bool] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> schemas.AdminNotificationList:
        query = self.db.query(models.Notification)
        
        if type:
            query = query.filter(models.Notification.type == type)
        if status is not None:
            query = query.filter(models.Notification.read == status)
        if start_date:
            query = query.filter(models.Notification.created_at >= start_date)
        if end_date:
            query = query.filter(models.Notification.created_at <= end_date)

        total = query.count()
        notifications = query.offset(skip).limit(limit).all()
        
        return schemas.AdminNotificationList(
            notifications=[schemas.AdminNotification.from_orm(n) for n in notifications],
            total=total
        )

    def mark_notification_as_read(self, notification_id: int) -> schemas.AdminNotification:
        notification = self.db.query(models.Notification).filter(
            models.Notification.id == notification_id
        ).first()
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")
        
        notification.read = True
        self.db.commit()
        self.db.refresh(notification)
        return schemas.AdminNotification.from_orm(notification)

    def mark_notification_as_unread(self, notification_id: int) -> schemas.AdminNotification:
        notification = self.db.query(models.Notification).filter(
            models.Notification.id == notification_id
        ).first()
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")
        
        notification.read = False
        self.db.commit()
        self.db.refresh(notification)
        return schemas.AdminNotification.from_orm(notification)

    def create_role(self, role: schemas.AdminRoleCreate) -> schemas.AdminRole:
        db_role = models.Role(
            name=role.name,
            description=role.description,
            permissions=role.permissions
        )
        self.db.add(db_role)
        self.db.commit()
        self.db.refresh(db_role)
        return schemas.AdminRole.from_orm(db_role)

    def get_roles(self, skip: int = 0, limit: int = 100) -> List[schemas.AdminRole]:
        return self.db.query(models.Role).offset(skip).limit(limit).all()

    def get_role(self, role_id: int) -> schemas.AdminRole:
        role = self.db.query(models.Role).filter(models.Role.id == role_id).first()
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        return schemas.AdminRole.from_orm(role)

    def update_role(
        self,
        role_id: int,
        role: schemas.AdminRoleUpdate
    ) -> schemas.AdminRole:
        db_role = self.db.query(models.Role).filter(models.Role.id == role_id).first()
        if not db_role:
            raise HTTPException(status_code=404, detail="Role not found")
        
        if role.name:
            db_role.name = role.name
        if role.description:
            db_role.description = role.description
        if role.permissions is not None:
            db_role.permissions = role.permissions
        
        self.db.commit()
        self.db.refresh(db_role)
        return schemas.AdminRole.from_orm(db_role)

    def delete_role(self, role_id: int) -> None:
        role = self.db.query(models.Role).filter(models.Role.id == role_id).first()
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        
        self.db.delete(role)
        self.db.commit()

    def get_moderation_queue(
        self,
        skip: int = 0,
        limit: int = 100,
        content_type: Optional[str] = None,
        status: Optional[str] = None
    ) -> schemas.AdminModerationLogList:
        query = self.db.query(models.ModerationLog)
        
        if content_type:
            query = query.filter(models.ModerationLog.content_type == content_type)
        if status:
            query = query.filter(models.ModerationLog.status == status)

        total = query.count()
        logs = query.offset(skip).limit(limit).all()
        
        return schemas.AdminModerationLogList(
            logs=[schemas.AdminModerationLog(
                id=log.id,
                content_id=log.content_id,
                content_type=log.content_type,
                moderator_id=log.moderator_id,
                action=log.action,
                reason=log.reason,
                created_at=log.created_at,
                content=log.content,
                moderator=log.moderator
            ) for log in logs],
            total=total
        )

    def get_moderation_stats(self) -> schemas.AdminModerationStats:
        stats = {
            "total_reports": self.db.query(models.Report).count(),
            "pending_reports": self.db.query(models.Report).filter(
                models.Report.status == "pending"
            ).count(),
            "resolved_reports": self.db.query(models.Report).filter(
                models.Report.status == "resolved"
            ).count(),
            "ignored_reports": self.db.query(models.Report).filter(
                models.Report.status == "ignored"
            ).count(),
            "total_moderations": self.db.query(models.ModerationLog).count(),
            "pending_moderations": self.db.query(models.ModerationLog).filter(
                models.ModerationLog.status == "pending"
            ).count()
        }
        return schemas.AdminModerationStats(**stats)

    def create_category(self, category: schemas.AdminCategoryCreate) -> schemas.AdminCategory:
        db_category = models.Category(
            name=category.name,
            description=category.description
        )
        self.db.add(db_category)
        self.db.commit()
        self.db.refresh(db_category)
        return schemas.AdminCategory.from_orm(db_category)

    def get_categories(self, skip: int = 0, limit: int = 100) -> List[schemas.AdminCategory]:
        return self.db.query(models.Category).offset(skip).limit(limit).all()

    def get_category(self, category_id: int) -> schemas.AdminCategory:
        category = self.db.query(models.Category).filter(
            models.Category.id == category_id
        ).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        return schemas.AdminCategory.from_orm(category)

    def update_category(
        self,
        category_id: int,
        category: schemas.AdminCategoryUpdate
    ) -> schemas.AdminCategory:
        db_category = self.db.query(models.Category).filter(
            models.Category.id == category_id
        ).first()
        if not db_category:
            raise HTTPException(status_code=404, detail="Category not found")
        
        if category.name:
            db_category.name = category.name
        if category.description:
            db_category.description = category.description
        
        self.db.commit()
        self.db.refresh(db_category)
        return schemas.AdminCategory.from_orm(db_category)

    def delete_category(self, category_id: int) -> None:
        category = self.db.query(models.Category).filter(
            models.Category.id == category_id
        ).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        
        self.db.delete(category)
        self.db.commit()

    def get_reports(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        type: Optional[str] = None,
        category_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> schemas.AdminReportList:
        query = self.db.query(models.Report)
        
        if status:
            query = query.filter(models.Report.status == status)
        if type:
            query = query.filter(models.Report.content_type == type)
        if category_id:
            query = query.filter(models.Report.category_id == category_id)
        if start_date:
            query = query.filter(models.Report.created_at >= start_date)
        if end_date:
            query = query.filter(models.Report.created_at <= end_date)

        total = query.count()
        reports = query.offset(skip).limit(limit).all()
        
        return schemas.AdminReportList(
            reports=[schemas.AdminReport(
                id=report.id,
                reporter_id=report.reporter_id,
                reported_id=report.reported_id,
                content_id=report.content_id,
                content_type=report.content_type,
                reason=report.reason,
                status=report.status,
                created_at=report.created_at,
                resolved_at=report.resolved_at,
                resolution_notes=report.resolution_notes,
                reporter=report.reporter,
                reported=report.reported,
                content=report.content,
                category=report.category
            ) for report in reports],
            total=total
        )

    def resolve_report(self, report_id: int, resolution_notes: Optional[str] = None) -> schemas.AdminReport:
        report = self.db.query(models.Report).filter(
            models.Report.id == report_id
        ).first()
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        if report.status != "pending":
            raise HTTPException(status_code=400, detail="Report is already resolved")
        
        report.status = "resolved"
        report.resolved_at = datetime.now()
        report.resolution_notes = resolution_notes
        
        self.db.commit()
        self.db.refresh(report)
        return schemas.AdminReport.from_orm(report)

    def ignore_report(self, report_id: int) -> schemas.AdminReport:
        report = self.db.query(models.Report).filter(
            models.Report.id == report_id
        ).first()
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        if report.status != "pending":
            raise HTTPException(status_code=400, detail="Report is already resolved")
        
        report.status = "ignored"
        report.resolved_at = datetime.now()
        
        self.db.commit()
        self.db.refresh(report)
        return schemas.AdminReport.from_orm(report)

    def get_analytics(
        self,
        range: str = "week",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> schemas.AdminAnalyticsStats:
        if range == "week":
            start_date = datetime.now() - timedelta(days=7)
        elif range == "month":
            start_date = datetime.now() - timedelta(days=30)
        elif range == "year":
            start_date = datetime.now() - timedelta(days=365)
        
        if not end_date:
            end_date = datetime.now()

        # User Growth
        user_growth = self.db.query(
            models.User.created_at,
            func.count(models.User.id).label("count")
        ).filter(
            models.User.created_at >= start_date,
            models.User.created_at <= end_date
        ).group_by(
            func.date_trunc('day', models.User.created_at)
        ).all()

        # Content Performance
        content_performance = self.db.query(
            models.Post.category_id,
            func.count(models.Post.id).label("post_count"),
            func.avg(models.Post.likes).label("avg_likes"),
            func.avg(models.Post.comments).label("avg_comments")
        ).filter(
            models.Post.created_at >= start_date,
            models.Post.created_at <= end_date
        ).group_by(models.Post.category_id).all()

        # Engagement Metrics
        engagement_metrics = self.db.query(
            models.Post.id,
            models.Post.likes,
            models.Post.comments,
            models.Post.shares
        ).filter(
            models.Post.created_at >= start_date,
            models.Post.created_at <= end_date
        ).all()

        # Category Distribution
        category_distribution = self.db.query(
            models.Category.id,
            models.Category.name,
            func.count(models.Post.id).label("post_count")
        ).join(models.Post).filter(
            models.Post.created_at >= start_date,
            models.Post.created_at <= end_date
        ).group_by(models.Category.id, models.Category.name).all()

        # User Activity
        user_activity = self.db.query(
            func.date_trunc('hour', models.ActivityLog.created_at).label("hour"),
            func.count(models.ActivityLog.id).label("activity_count")
        ).filter(
            models.ActivityLog.created_at >= start_date,
            models.ActivityLog.created_at <= end_date
        ).group_by("hour").all()

        # Calculate statistics
        stats = {
            "total_users": self.db.query(models.User).count(),
            "new_users": self.db.query(models.User).filter(
                models.User.created_at >= start_date
            ).count(),
            "active_users": self.db.query(models.User).filter(
                models.User.last_active >= start_date
            ).count(),
            "total_posts": self.db.query(models.Post).count(),
            "total_comments": self.db.query(models.Comment).count(),
            "avg_engagement": sum(p.likes + p.comments + p.shares for p in engagement_metrics) / len(engagement_metrics) if engagement_metrics else 0,
            "top_category": content_performance[0][0] if content_performance else None,
            "total_interactions": sum(p.likes + p.comments + p.shares for p in engagement_metrics) if engagement_metrics else 0,
            "avg_comments": sum(p.comments for p in engagement_metrics) / len(engagement_metrics) if engagement_metrics else 0,
            "avg_likes": sum(p.likes for p in engagement_metrics) / len(engagement_metrics) if engagement_metrics else 0,
            "user_growth": [{"date": str(d[0]), "count": d[1]} for d in user_growth],
            "content_performance": [{"category": c[0], "post_count": c[1], "avg_likes": c[2], "avg_comments": c[3]} for c in content_performance],
            "engagement_metrics": [{"likes": e.likes, "comments": e.comments, "shares": e.shares} for e in engagement_metrics],
            "category_distribution": [{"category": c[1], "post_count": c[2]} for c in category_distribution],
            "user_activity": [{"hour": str(u[0]), "activity_count": u[1]} for u in user_activity]
        }
        
        return schemas.AdminAnalyticsStats(**stats)

async def get_dashboard_stats(db: Session):
    # User metrics
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    new_users_today = db.query(User).filter(
        User.created_at >= datetime.utcnow() - timedelta(days=1)
    ).count()
    
    # Content metrics
    total_posts = db.query(Post).count()
    active_posts = db.query(Post).filter(Post.status == "active").count()
    new_posts_today = db.query(Post).filter(
        Post.created_at >= datetime.utcnow() - timedelta(days=1)
    ).count()
    
    total_comments = db.query(Comment).count()
    new_comments_today = db.query(Comment).filter(
        Comment.created_at >= datetime.utcnow() - timedelta(days=1)
    ).count()
    
    # Moderation metrics
    pending_moderation = db.query(Post).filter(
        Post.status == "pending"
    ).count()
    
    reported_content = db.query(Post).filter(
        Post.is_reported == True
    ).count() + db.query(Comment).filter(
        Comment.is_reported == True
    ).count()
    
    # Usage metrics
    storage_usage = await calculate_storage_usage(db)
    bandwidth_usage = await calculate_bandwidth_usage(db)
    
    # Engagement metrics
    avg_comments_per_post = total_comments / total_posts if total_posts > 0 else 0
    avg_likes_per_post = db.query(Like).count() / total_posts if total_posts > 0 else 0
    
    # User activity metrics
    active_users_7d = db.query(User).filter(
        User.last_login >= datetime.utcnow() - timedelta(days=7)
    ).count()
    
    # Category metrics
    active_categories = db.query(Category).filter(
        Category.status == "active"
    ).count()
    
    stats = {
        "total_users": total_users,
        "active_users": active_users,
        "new_users_today": new_users_today,
        "active_users_7d": active_users_7d,
        "total_posts": total_posts,
        "active_posts": active_posts,
        "new_posts_today": new_posts_today,
        "total_comments": total_comments,
        "new_comments_today": new_comments_today,
        "avg_comments_per_post": avg_comments_per_post,
        "avg_likes_per_post": avg_likes_per_post,
        "pending_moderation": pending_moderation,
        "reported_content": reported_content,
        "storage_usage": storage_usage,
        "bandwidth_usage": bandwidth_usage,
        "active_categories": active_categories
    }
    
    return schemas.AdminDashboardStats(**stats)

async def get_activity_logs(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    resource: Optional[str] = None,
    resource_id: Optional[int] = None,
    status: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc"
):
    query = db.query(ActivityLog)
    
    # Apply filters
    if user_id:
        query = query.filter(ActivityLog.user_id == user_id)
    if action:
        query = query.filter(ActivityLog.action == action)
    if resource:
        query = query.filter(ActivityLog.resource == resource)
    if resource_id:
        query = query.filter(ActivityLog.resource_id == resource_id)
    if status:
        query = query.filter(ActivityLog.status == status)
    if start_date:
        query = query.filter(ActivityLog.created_at >= start_date)
    if end_date:
        query = query.filter(ActivityLog.created_at <= end_date)
    
    # Get total count before applying pagination
    total = query.count()
    
    # Apply sorting
    sort_direction = getattr(ActivityLog, sort_by)
    if sort_order == "desc":
        sort_direction = sort_direction.desc()
    else:
        sort_direction = sort_direction.asc()
    
    # Apply pagination and fetch results
    logs = query.order_by(sort_direction)\
        .offset((page - 1) * page_size)\
        .limit(page_size)\
        .all()
    
    # Calculate metrics
    metrics = {
        "total_logs": total,
        "unique_users": db.query(ActivityLog.user_id).distinct().count(),
        "unique_resources": db.query(ActivityLog.resource).distinct().count(),
        "most_active_user": db.query(ActivityLog.user_id, func.count(ActivityLog.user_id))
            .group_by(ActivityLog.user_id)
            .order_by(func.count(ActivityLog.user_id).desc())
            .first()
    }
    
    return schemas.AdminActivityLogList(
        logs=logs,
        total=total,
        page=page,
        pages=(total + page_size - 1) // page_size,
        metrics=metrics
    )

async def get_notifications(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    user_id: Optional[int] = None,
    read: Optional[bool] = None,
    type: Optional[str] = None
):
    query = db.query(Notification)
    
    if user_id:
        query = query.filter(Notification.user_id == user_id)
    if read is not None:
        query = query.filter(Notification.read == read)
    if type:
        query = query.filter(Notification.type == type)
    
    total = query.count()
    notifications = query.order_by(Notification.created_at.desc())\
        .offset((page - 1) * page_size)\
        .limit(page_size)\
        .all()
    
    return schemas.AdminNotificationList(
        notifications=notifications,
        total=total,
        page=page,
        pages=(total + page_size - 1) // page_size
    )

async def assign_role(
    db: Session,
    user_id: int,
    role_id: int,
    assigned_by: int,
    reason: Optional[str] = None
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.role_id = role_id
    user.updated_at = datetime.utcnow()
    
    # Create role assignment log
    assignment = RoleAssignment(
        user_id=user_id,
        role_id=role_id,
        assigned_by=assigned_by,
        assigned_at=datetime.utcnow(),
        reason=reason
    )
    db.add(assignment)
    
    db.commit()
    db.refresh(user)
    
    return schemas.AdminRoleAssignment(
        user_id=user_id,
        role_id=role_id,
        assigned_by=assigned_by,
        assigned_at=datetime.utcnow(),
        reason=reason
    )

async def get_role_assignments(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    user_id: Optional[int] = None,
    role_id: Optional[int] = None
):
    query = db.query(RoleAssignment)
    
    if user_id:
        query = query.filter(RoleAssignment.user_id == user_id)
    if role_id:
        query = query.filter(RoleAssignment.role_id == role_id)
    
    total = query.count()
    assignments = query.order_by(RoleAssignment.assigned_at.desc())\
        .offset((page - 1) * page_size)\
        .limit(page_size)\
        .all()
    
    return schemas.AdminRoleAssignmentList(
        assignments=assignments,
        total=total,
        page=page,
        pages=(total + page_size - 1) // page_size
    )

async def moderate_content(
    db: Session,
    content_id: int,
    content_type: str,
    action: str,
    moderator_id: int,
    reason: Optional[str] = None
):
    if content_type == "post":
        content = db.query(Post).filter(Post.id == content_id).first()
    elif content_type == "comment":
        content = db.query(Comment).filter(Comment.id == content_id).first()
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid content type"
        )
    
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    if action == "approve":
        content.status = "active"
    elif action == "reject":
        content.status = "rejected"
    elif action == "delete":
        content.status = "deleted"
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid moderation action"
        )
    
    content.updated_at = datetime.utcnow()
    
    # Create moderation log
    log = ModerationLog(
        content_id=content_id,
        content_type=content_type,
        moderator_id=moderator_id,
        action=action,
        reason=reason,
        created_at=datetime.utcnow()
    )
    db.add(log)
    
    db.commit()
    db.refresh(content)
    
    return content

async def get_moderation_logs(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    moderator_id: Optional[int] = None,
    content_type: Optional[str] = None,
    action: Optional[str] = None
):
    query = db.query(ModerationLog)
    
    if moderator_id:
        query = query.filter(ModerationLog.moderator_id == moderator_id)
    if content_type:
        query = query.filter(ModerationLog.content_type == content_type)
    if action:
        query = query.filter(ModerationLog.action == action)
    
    total = query.count()
    logs = query.order_by(ModerationLog.created_at.desc())\
        .offset((page - 1) * page_size)\
        .limit(page_size)\
        .all()
    
    return {
        "logs": logs,
        "total": total,
        "page": page,
        "pages": (total + page_size - 1) // page_size
    }
