import { defineStore } from 'pinia';
import { AdminState } from '@/types/admin';
import { adminService } from '@/services/admin';

export const useAdminStore = defineStore('admin', {
    state: (): AdminState => ({
        dashboardStats: null,
        activityLogs: {
            logs: [],
            total: 0,
            page: 1,
            pages: 1,
            metrics: {
                total_logs: 0,
                unique_users: 0,
                unique_resources: 0
            }
        },
        notifications: {
            notifications: [],
            total: 0,
            page: 1,
            pages: 1,
            unread_count: 0
        },
        roleAssignments: {
            assignments: [],
            total: 0,
            page: 1,
            pages: 1,
            pending_count: 0
        },
        moderationLogs: {
            logs: [],
            total: 0,
            page: 1,
            pages: 1,
            pending_count: 0,
            by_category: {}
        },
        roles: {
            roles: [],
            total: 0,
            page: 1,
            pages: 1,
            hierarchy: []
        },
        categories: {
            categories: [],
            total: 0,
            page: 1,
            pages: 1,
            hierarchy: []
        },
        loading: false,
        error: null,
        selectedRole: null,
        selectedCategory: null,
        filters: {
            page: 1,
            page_size: 20,
            user_id: undefined,
            role_id: undefined,
            action: undefined,
            resource: undefined,
            type: undefined,
            status: undefined,
            start_date: undefined,
            end_date: undefined,
            sort_by: undefined,
            sort_order: undefined,
            search: undefined
        }
    }),

    actions: {
        async fetchDashboardStats() {
            try {
                this.loading = true;
                this.error = null;
                this.dashboardStats = await adminService.getDashboardStats();
            } catch (error) {
                this.error = error.message;
            } finally {
                this.loading = false;
            }
        },

        async fetchActivityLogs(filters: any = {}) {
            try {
                this.loading = true;
                this.error = null;
                this.activityLogs = await adminService.getActivityLogs({
                    ...this.filters,
                    ...filters
                });
            } catch (error) {
                this.error = error.message;
            } finally {
                this.loading = false;
            }
        },

        async fetchNotifications(filters: any = {}) {
            try {
                this.loading = true;
                this.error = null;
                this.notifications = await adminService.getNotifications({
                    ...this.filters,
                    ...filters
                });
            } catch (error) {
                this.error = error.message;
            } finally {
                this.loading = false;
            }
        },

        async markNotificationAsRead(id: number) {
            try {
                await adminService.markNotificationAsRead(id);
                await this.fetchNotifications();
            } catch (error) {
                this.error = error.message;
            }
        },

        async markAllNotificationsAsRead() {
            try {
                await adminService.markAllNotificationsAsRead();
                await this.fetchNotifications();
            } catch (error) {
                this.error = error.message;
            }
        },

        async fetchRoles(filters: any = {}) {
            try {
                this.loading = true;
                this.error = null;
                this.roles = await adminService.getRoles({
                    ...this.filters,
                    ...filters
                });
            } catch (error) {
                this.error = error.message;
            } finally {
                this.loading = false;
            }
        },

        async assignRole(request: any) {
            try {
                await adminService.assignRole(request);
                await this.fetchRoleAssignments();
            } catch (error) {
                this.error = error.message;
            }
        },

        async fetchRoleAssignments() {
            try {
                this.loading = true;
                this.error = null;
                this.roleAssignments = await adminService.getRoleAssignments();
            } catch (error) {
                this.error = error.message;
            } finally {
                this.loading = false;
            }
        },

        async fetchModerationLogs(filters: any = {}) {
            try {
                this.loading = true;
                this.error = null;
                this.moderationLogs = await adminService.getContentModerationLogs({
                    ...this.filters,
                    ...filters
                });
            } catch (error) {
                this.error = error.message;
            } finally {
                this.loading = false;
            }
        },

        async moderateContent(request: any) {
            try {
                await adminService.moderateContent(request);
                await this.fetchModerationLogs();
            } catch (error) {
                this.error = error.message;
            }
        },

        async fetchCategories(filters: any = {}) {
            try {
                this.loading = true;
                this.error = null;
                this.categories = await adminService.getCategories({
                    ...this.filters,
                    ...filters
                });
            } catch (error) {
                this.error = error.message;
            } finally {
                this.loading = false;
            }
        },

        async createCategory(data: any) {
            try {
                const category = await adminService.createCategory(data);
                await this.fetchCategories();
                return category;
            } catch (error) {
                this.error = error.message;
                throw error;
            }
        },

        async updateCategory(id: number, data: any) {
            try {
                const category = await adminService.updateCategory(id, data);
                await this.fetchCategories();
                return category;
            } catch (error) {
                this.error = error.message;
                throw error;
            }
        },

        async deleteCategory(id: number) {
            try {
                await adminService.deleteCategory(id);
                await this.fetchCategories();
            } catch (error) {
                this.error = error.message;
                throw error;
            }
        },

        async getUserActivity(userId: number, filters: any = {}) {
            try {
                this.loading = true;
                this.error = null;
                const logs = await adminService.getUserActivity(userId, {
                    ...this.filters,
                    ...filters
                });
                return logs;
            } catch (error) {
                this.error = error.message;
                throw error;
            } finally {
                this.loading = false;
            }
        },

        async banUser(userId: number, reason: string, duration?: string) {
            try {
                await adminService.banUser(userId, reason, duration);
            } catch (error) {
                this.error = error.message;
                throw error;
            }
        },

        async unbanUser(userId: number) {
            try {
                await adminService.unbanUser(userId);
            } catch (error) {
                this.error = error.message;
                throw error;
            }
        }
    }
});
