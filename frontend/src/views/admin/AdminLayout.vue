<template>
  <div class="admin-layout">
    <!-- Sidebar -->
    <aside class="admin-sidebar">
      <div class="admin-sidebar-header">
        <h1>Rianzel Admin</h1>
      </div>
      <nav class="admin-sidebar-nav">
        <router-link to="/admin/dashboard" class="nav-item">
          <i class="fas fa-chart-line"></i>
          <span>Dashboard</span>
        </router-link>
        <router-link to="/admin/roles" class="nav-item">
          <i class="fas fa-user-shield"></i>
          <span>Roles & Permissions</span>
        </router-link>
        <router-link to="/admin/moderation" class="nav-item">
          <i class="fas fa-shield-alt"></i>
          <span>Content Moderation</span>
        </router-link>
        <router-link to="/admin/categories" class="nav-item">
          <i class="fas fa-tags"></i>
          <span>Categories</span>
        </router-link>
        <router-link to="/admin/users" class="nav-item">
          <i class="fas fa-users"></i>
          <span>User Management</span>
        </router-link>
        <router-link to="/admin/notifications" class="nav-item">
          <i class="fas fa-bell"></i>
          <span>Notifications</span>
        </router-link>
        <router-link to="/admin/activity" class="nav-item">
          <i class="fas fa-history"></i>
          <span>Activity Logs</span>
        </router-link>
      </nav>
    </aside>

    <!-- Main Content -->
    <main class="admin-main">
      <header class="admin-header">
        <h2>{{ currentPageTitle }}</h2>
        <div class="admin-header-actions">
          <button class="btn btn-primary" @click="openNotificationDrawer">
            <i class="fas fa-bell"></i>
            <span v-if="unreadNotifications">{{ unreadNotifications }}</span>
          </button>
          <button class="btn btn-secondary" @click="logout">
            <i class="fas fa-sign-out-alt"></i>
            <span>Logout</span>
          </button>
        </div>
      </header>
      
      <div class="admin-content">
        <router-view></router-view>
      </div>
    </main>

    <!-- Notification Drawer -->
    <div class="notification-drawer" v-if="showNotificationDrawer">
      <div class="notification-drawer-header">
        <h3>Notifications</h3>
        <button class="btn btn-link" @click="closeNotificationDrawer">
          <i class="fas fa-times"></i>
        </button>
      </div>
      <div class="notification-list">
        <div v-for="notification in notifications" :key="notification.id" class="notification-item">
          <div class="notification-content">
            <span class="notification-type" :class="notification.type">
              {{ notification.type }}
            </span>
            <span class="notification-message">
              {{ notification.message }}
            </span>
          </div>
          <div class="notification-actions">
            <button class="btn btn-link" @click="markAsRead(notification.id)" v-if="!notification.read">
              <i class="fas fa-check"></i>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useAdminStore } from '@/store/admin'
import { useRouter } from 'vue-router'

const router = useRouter()
const adminStore = useAdminStore()

const showNotificationDrawer = ref(false)
const currentPageTitle = computed(() => {
  const route = router.currentRoute.value
  const titleMap = {
    '/admin/dashboard': 'Dashboard',
    '/admin/roles': 'Roles & Permissions',
    '/admin/moderation': 'Content Moderation',
    '/admin/categories': 'Categories',
    '/admin/users': 'User Management',
    '/admin/notifications': 'Notifications',
    '/admin/activity': 'Activity Logs'
  }
  return titleMap[route.path]
})

const unreadNotifications = computed(() => {
  return adminStore.notifications.notifications.filter(n => !n.read).length
})

const notifications = computed(() => {
  return adminStore.notifications.notifications
})

const openNotificationDrawer = () => {
  showNotificationDrawer.value = true
}

const closeNotificationDrawer = () => {
  showNotificationDrawer.value = false
}

const markAsRead = async (notificationId: number) => {
  await adminStore.markNotificationAsRead(notificationId)
  closeNotificationDrawer()
}

const logout = () => {
  // Implement logout logic
  router.push('/login')
}
</script>

<style scoped>
.admin-layout {
  display: flex;
  min-height: 100vh;
}

.admin-sidebar {
  width: 250px;
  background: #2c3e50;
  color: white;
  padding: 20px;
}

.admin-sidebar-header {
  padding: 15px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.admin-sidebar-nav {
  margin-top: 20px;
}

.nav-item {
  display: flex;
  align-items: center;
  padding: 12px 15px;
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  border-radius: 5px;
  margin: 5px 0;
  transition: background-color 0.3s;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.1);
}

.nav-item.router-link-active {
  background: rgba(255, 255, 255, 0.2);
  color: white;
}

.nav-item i {
  margin-right: 10px;
}

.admin-main {
  flex: 1;
  padding: 20px;
  background: #f5f6fa;
}

.admin-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.admin-header-actions {
  display: flex;
  gap: 10px;
}

.admin-content {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.notification-drawer {
  position: fixed;
  top: 0;
  right: 0;
  width: 400px;
  height: 100vh;
  background: white;
  box-shadow: -2px 0 5px rgba(0, 0, 0, 0.1);
  z-index: 1000;
}

.notification-drawer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  border-bottom: 1px solid #eee;
}

.notification-list {
  padding: 15px;
  max-height: calc(100vh - 60px);
  overflow-y: auto;
}

.notification-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  border-bottom: 1px solid #eee;
}

.notification-content {
  flex: 1;
}

.notification-type {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  margin-right: 8px;
}

.notification-type.moderation {
  background: #f8d7da;
  color: #721c24;
}

.notification-type.role_assignment {
  background: #d4edda;
  color: #155724;
}

.notification-type.system {
  background: #fff3cd;
  color: #856404;
}

.notification-type.user_action {
  background: #cce5ff;
  color: #004085;
}

.notification-message {
  font-size: 14px;
}

.notification-actions {
  display: flex;
  align-items: center;
}
</style>
