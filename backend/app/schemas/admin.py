from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from .user import UserResponse
from .post import PostResponse
from .comment import CommentResponse

class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None
    permissions: List[str]

class RoleCreate(RoleBase):
    pass

class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    permissions: Optional[List[str]] = None

class Role(RoleBase):
    id: int

    class Config:
        orm_mode = True

class ModerationLogBase(BaseModel):
    content_id: int
    content_type: str
    status: str
    moderator_id: int
    reason: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        orm_mode = True

class ModerationLogCreate(ModerationLogBase):
    pass

class ModerationLog(ModerationLogBase):
    id: int

    class Config:
        orm_mode = True

class CategoryBase(BaseModel):
    name: str
    description: str
    content_type: str
    status: str = "active"
    parent_id: Optional[int] = None
    post_count: int = 0
    comment_count: int = 0

    class Config:
        orm_mode = True

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    content_type: Optional[str] = None
    status: Optional[str] = None
    parent_id: Optional[int] = None

class Category(CategoryBase):
    id: int

    class Config:
        orm_mode = True

class NotificationBase(BaseModel):
    type: str
    message: str
    read: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        orm_mode = True

class Notification(NotificationBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True

class NotificationCreate(NotificationBase):
    pass

class NotificationUpdate(BaseModel):
    read: bool

class ModerationStats(BaseModel):
    pending: int
    approved_today: int
    rejected_today: int
    by_category: Dict[str, int]

    class Config:
        orm_mode = True

class AdminDashboardStats(BaseModel):
    total_users: int
    active_users: int
    new_users: int
    total_posts: int
    total_comments: int
    total_categories: int
    moderation_queue: int
    pending_approvals: int
    pending_reports: int

class AdminActivityLog(BaseModel):
    id: int
    user_id: int
    action: str
    description: str
    ip_address: str
    created_at: datetime
    user: UserResponse

    class Config:
        orm_mode = True

class AdminActivityLogList(BaseModel):
    logs: List[AdminActivityLog]
    total: int

    class Config:
        orm_mode = True

class AdminNotification(BaseModel):
    id: int
    title: str
    message: str
    type: str
    recipient_id: Optional[int]
    created_at: datetime
    read: bool
    system: bool

    class Config:
        orm_mode = True

class AdminNotificationList(BaseModel):
    notifications: List[AdminNotification]
    total: int

    class Config:
        orm_mode = True

class AdminRole(BaseModel):
    id: int
    name: str
    description: str
    permissions: List[str]
    created_at: datetime

    class Config:
        orm_mode = True

class AdminRoleCreate(BaseModel):
    name: str
    description: str
    permissions: List[str]

class AdminRoleUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    permissions: Optional[List[str]]

class AdminModerationLog(BaseModel):
    id: int
    content_id: int
    content_type: str
    moderator_id: int
    action: str
    reason: str
    created_at: datetime
    content: Content
    moderator: UserResponse

    class Config:
        orm_mode = True

class AdminModerationLogList(BaseModel):
    logs: List[AdminModerationLog]
    total: int

    class Config:
        orm_mode = True

class AdminModerationStats(BaseModel):
    total_reports: int
    pending_reports: int
    resolved_reports: int
    ignored_reports: int
    total_moderations: int
    pending_moderations: int

    class Config:
        orm_mode = True

class AdminCategory(BaseModel):
    id: int
    name: str
    description: str
    created_at: datetime

    class Config:
        orm_mode = True

class AdminCategoryCreate(BaseModel):
    name: str
    description: str

class AdminCategoryUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]

class AdminReport(BaseModel):
    id: int
    reporter_id: int
    reported_id: int
    content_id: int
    content_type: str
    reason: str
    status: str
    created_at: datetime
    resolved_at: Optional[datetime]
    resolution_notes: Optional[str]
    reporter: UserResponse
    reported: UserResponse
    content: Content
    category: Category

    class Config:
        orm_mode = True

class AdminReportCreate(BaseModel):
    reporter_id: int
    reported_id: int
    content_id: int
    content_type: str
    reason: str
    category_id: int

class AdminReportUpdate(BaseModel):
    status: Optional[str]
    resolution_notes: Optional[str]

class AdminReportList(BaseModel):
    reports: List[AdminReport]
    total: int

    class Config:
        orm_mode = True

class AdminAnalyticsStats(BaseModel):
    total_users: int
    new_users: int
    active_users: int
    total_posts: int
    total_comments: int
    avg_engagement: float
    top_category: str
    total_interactions: int
    avg_comments: float
    avg_likes: float
    user_growth: List[dict]
    content_performance: List[dict]
    engagement_metrics: List[dict]
    category_distribution: List[dict]
    user_activity: List[dict]

    class Config:
        orm_mode = True

class AdminContent(BaseModel):
    id: int
    title: str
    type: str
    content: str
    category_id: int
    author_id: int
    thumbnail: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime
    author: UserResponse
    category: Category

    class Config:
        orm_mode = True

class AdminContentCreate(BaseModel):
    title: str
    type: str
    content: str
    category_id: int
    author_id: int
    thumbnail: Optional[str]
    status: str

class AdminContentUpdate(BaseModel):
    title: Optional[str]
    type: Optional[str]
    content: Optional[str]
    category_id: Optional[int]
    thumbnail: Optional[str]
    status: Optional[str]

class AdminContentList(BaseModel):
    contents: List[AdminContent]
    total: int

    class Config:
        orm_mode = True

class AdminSettings(BaseModel):
    site: dict
    security: dict
    email: dict

    class Config:
        orm_mode = True

class AdminBackupStatus(BaseModel):
    last_database_backup: Optional[datetime]
    database_size: Optional[int]
    last_file_backup: Optional[datetime]
    file_size: Optional[int]

    class Config:
        orm_mode = True

class AdminBackup(BaseModel):
    id: int
    type: str
    created_at: datetime
    size: int
    status: str

    class Config:
        orm_mode = True

class AdminRoleAssignment(BaseModel):
    user_id: int
    role_id: int

    class Config:
        orm_mode = True

class AdminRoleAssignmentList(BaseModel):
    total: int
    page: int
    page_size: int
    assignments: List[AdminRoleAssignment]

    class Config:
        orm_mode = True

class ModerationQueue(BaseModel):
    id: int
    content_id: int
    content_type: str
    title: str
    content: str
    author: str
    category: str
    status: str
    created_at: datetime

    class Config:
        orm_mode = True

class ModerationQueueList(BaseModel):
    total: int
    page: int
    page_size: int
    queue: List[ModerationQueue]

    class Config:
        orm_mode = True

class CategoryList(BaseModel):
    total: int
    page: int
    page_size: int
    categories: List[Category]

    class Config:
        orm_mode = True

class AdminNotification(BaseModel):
    id: int
    type: str
    message: str
    read: bool
    created_at: datetime
    user_id: int

    class Config:
        orm_mode = True

class AdminNotificationList(BaseModel):
    total: int
    page: int
    page_size: int
    notifications: List[AdminNotification]

    class Config:
        orm_mode = True

class AdminStats(BaseModel):
    total_users: int
    active_users: int
    new_users_today: int
    active_users_7d: int
    total_posts: int
    active_posts: int
    new_posts_today: int
    total_comments: int
    new_comments_today: int
    avg_comments_per_post: float
    pending_moderation: int
    reported_content: int
    storage_usage: int
    bandwidth_usage: int
    active_categories: int
    moderation_stats: ModerationStats

    class Config:
        orm_mode = True

class RoleListResponse(BaseModel):
    roles: List[Role]
    total: int
    page: int
    pages: int

class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    parent_id: Optional[int] = None
    status: str = "active"
    order: int = 0
    is_featured: bool = False
    icon: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[int] = None
    status: Optional[str] = None
    order: Optional[int] = None
    is_featured: Optional[bool] = None
    icon: Optional[str] = None

class CategoryResponse(CategoryBase):
    id: int
    posts_count: int
    subcategories_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CategoryListResponse(BaseModel):
    categories: List[CategoryResponse]
    total: int
    page: int
    pages: int

class AdminDashboardStats(BaseModel):
    total_users: int
    active_users: int
    new_users_today: int
    total_posts: int
    active_posts: int
    new_posts_today: int
    total_comments: int
    new_comments_today: int
    pending_moderation: int
    reported_content: int
    storage_usage: float
    bandwidth_usage: float

class AdminActivityLog(BaseModel):
    id: int
    user_id: int
    action: str
    resource: str
    resource_id: int
    details: dict
    created_at: datetime

    class Config:
        from_attributes = True

class AdminActivityLogList(BaseModel):
    logs: List[AdminActivityLog]
    total: int
    page: int
    pages: int

class AdminNotification(BaseModel):
    id: int
    user_id: int
    message: str
    type: str
    read: bool
    created_at: datetime

    class Config:
        from_attributes = True

class AdminNotificationList(BaseModel):
    notifications: List[AdminNotification]
    total: int
    page: int
    pages: int

class AdminRoleAssignment(BaseModel):
    user_id: int
    role_id: int
    assigned_by: int
    assigned_at: datetime
    reason: Optional[str] = None

    class Config:
        from_attributes = True

class AdminRoleAssignmentList(BaseModel):
    assignments: List[AdminRoleAssignment]
    total: int
    page: int
    pages: int
