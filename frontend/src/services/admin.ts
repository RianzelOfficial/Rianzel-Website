import { api } from './api';
import { 
    AdminDashboardStats, 
    AdminActivityLogList,
    AdminNotificationList,
    AdminRoleAssignmentList,
    ModerationLogList,
    AdminRoleList,
    CategoryList,
    RoleAssignmentRequest,
    ModerationActionRequest,
    FilterOptions
} from '../types/admin';

export class AdminService {
    private static instance: AdminService;
    private constructor() {}

    public static getInstance(): AdminService {
        if (!AdminService.instance) {
            AdminService.instance = new AdminService();
        }
        return AdminService.instance;
    }

    // Dashboard
    async getDashboardStats(): Promise<AdminDashboardStats> {
        const response = await api.get('/admin/dashboard/stats');
        return response.data;
    }

    // Activity Logs
    async getActivityLogs(filters: FilterOptions): Promise<AdminActivityLogList> {
        const response = await api.get('/admin/logs/activity', { params: filters });
        return response.data;
    }

    // Notifications
    async getNotifications(filters: FilterOptions): Promise<AdminNotificationList> {
        const response = await api.get('/admin/notifications', { params: filters });
        return response.data;
    }

    async markNotificationAsRead(id: number): Promise<void> {
        await api.post(`/admin/notifications/${id}/read`);
    }

    async markAllNotificationsAsRead(): Promise<void> {
        await api.post('/admin/notifications/read-all');
    }

    // Role Management
    async getRoles(filters: FilterOptions): Promise<AdminRoleList> {
        const response = await api.get('/admin/roles', { params: filters });
        return response.data;
    }

    async assignRole(request: RoleAssignmentRequest): Promise<AdminRoleAssignmentList> {
        const response = await api.post('/admin/roles/assign', request);
        return response.data;
    }

    async updateRole(id: number, data: Partial<AdminRole>): Promise<AdminRole> {
        const response = await api.put(`/admin/roles/${id}`, data);
        return response.data;
    }

    async deleteRole(id: number): Promise<void> {
        await api.delete(`/admin/roles/${id}`);
    }

    // Content Moderation
    async getContentModerationLogs(filters: FilterOptions): Promise<ModerationLogList> {
        const response = await api.get('/admin/moderation/logs', { params: filters });
        return response.data;
    }

    async moderateContent(request: ModerationActionRequest): Promise<void> {
        await api.post('/admin/moderation/action', request);
    }

    async approveContent(id: number, content_type: string): Promise<void> {
        await api.post(`/admin/moderation/${content_type}/${id}/approve`);
    }

    async rejectContent(id: number, content_type: string, reason: string): Promise<void> {
        await api.post(`/admin/moderation/${content_type}/${id}/reject`, { reason });
    }

    async deleteContent(id: number, content_type: string): Promise<void> {
        await api.delete(`/admin/moderation/${content_type}/${id}`);
    }

    // Categories
    async getCategories(filters: FilterOptions): Promise<CategoryList> {
        const response = await api.get('/admin/categories', { params: filters });
        return response.data;
    }

    async createCategory(data: Partial<Category>): Promise<Category> {
        const response = await api.post('/admin/categories', data);
        return response.data;
    }

    async updateCategory(id: number, data: Partial<Category>): Promise<Category> {
        const response = await api.put(`/admin/categories/${id}`, data);
        return response.data;
    }

    async deleteCategory(id: number): Promise<void> {
        await api.delete(`/admin/categories/${id}`);
    }

    // User Management
    async getUserActivity(userId: number, filters: FilterOptions): Promise<AdminActivityLogList> {
        const response = await api.get(`/admin/users/${userId}/activity`, { params: filters });
        return response.data;
    }

    async getUserNotifications(userId: number, filters: FilterOptions): Promise<AdminNotificationList> {
        const response = await api.get(`/admin/users/${userId}/notifications`, { params: filters });
        return response.data;
    }

    async banUser(userId: number, reason: string, duration?: string): Promise<void> {
        await api.post(`/admin/users/${userId}/ban`, { reason, duration });
    }

    async unbanUser(userId: number): Promise<void> {
        await api.post(`/admin/users/${userId}/unban`);
    }
}

// Export singleton instance
export const adminService = AdminService.getInstance();
