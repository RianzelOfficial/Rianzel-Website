export interface AdminDashboardStats {
    total_users: number
    active_users: number
    new_users_today: number
    total_posts: number
    active_posts: number
    new_posts_today: number
    total_comments: number
    new_comments_today: number
    pending_moderation: number
    reported_content: number
    storage_usage: number
    bandwidth_usage: number
}

export interface AdminActivityLog {
    id: number
    user_id: number
    action: string
    resource: string
    resource_id: number
    details: Record<string, any>
    created_at: string
}

export interface AdminActivityLogList {
    logs: AdminActivityLog[]
    total: number
    page: number
    pages: number
}

export interface AdminNotification {
    id: number
    user_id: number
    message: string
    type: string
    read: boolean
    created_at: string
}

export interface AdminNotificationList {
    notifications: AdminNotification[]
    total: number
    page: number
    pages: number
}

export interface AdminRoleAssignment {
    user_id: number
    role_id: number
    assigned_by: number
    assigned_at: string
    reason?: string
}

export interface AdminRoleAssignmentList {
    assignments: AdminRoleAssignment[]
    total: number
    page: number
    pages: number
}

export interface ModerationLog {
    id: number
    content_id: number
    content_type: string
    moderator_id: number
    action: string
    reason?: string
    created_at: string
}

export interface ModerationLogList {
    logs: ModerationLog[]
    total: number
    page: number
    pages: number
}

export interface Role {
    id: number
    name: string
    description?: string
    permissions: string[]
    users_count: number
    created_at: string
    updated_at: string
}

export interface RoleList {
    roles: Role[]
    total: number
    page: number
    pages: number
}

export interface Category {
    id: number
    name: string
    description?: string
    parent_id?: number
    posts_count: number
    subcategories_count: number
    status: string
    order: number
    is_featured: boolean
    icon?: string
    created_at: string
    updated_at: string
}

export interface CategoryList {
    categories: Category[]
    total: number
    page: number
    pages: number
}

export interface RoleAssignmentRequest {
    user_id: number
    role_id: number
    reason?: string
}

export interface ModerationActionRequest {
    content_id: number
    content_type: string
    action: string
    reason?: string
}

export interface FilterOptions {
    page: number
    page_size: number
    user_id?: number
    role_id?: number
    action?: string
    resource?: string
    type?: string
    status?: string
    start_date?: string
    end_date?: string
}

export interface AdminState {
    dashboardStats: AdminDashboardStats | null
    activityLogs: AdminActivityLogList
    notifications: AdminNotificationList
    roleAssignments: AdminRoleAssignmentList
    moderationLogs: ModerationLogList
    roles: RoleList
    categories: CategoryList
    loading: boolean
    error: string | null
}
