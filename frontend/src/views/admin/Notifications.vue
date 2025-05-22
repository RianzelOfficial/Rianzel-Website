<template>
  <div class="notifications-page">
    <!-- Notifications Header -->
    <div class="notifications-header">
      <h2>Notifications Management</h2>
      <div class="header-actions">
        <button class="btn btn-primary" @click="openNotificationModal('create')">
          <i class="fas fa-bell-plus"></i>
          <span>Create Notification</span>
        </button>
      </div>
    </div>

    <!-- Filters -->
    <div class="notifications-filters">
      <div class="filter-group">
        <label for="type">Type:</label>
        <select id="type" v-model="filters.type" @change="fetchNotifications">
          <option value="">All</option>
          <option value="moderation">Moderation</option>
          <option value="role_assignment">Role Assignment</option>
          <option value="system">System</option>
          <option value="user_action">User Action</option>
        </select>
      </div>
      <div class="filter-group">
        <label for="status">Status:</label>
        <select id="status" v-model="filters.status" @change="fetchNotifications">
          <option value="">All</option>
          <option value="read">Read</option>
          <option value="unread">Unread</option>
        </select>
      </div>
      <div class="filter-group">
        <label for="date">Date Range:</label>
        <input type="date" id="date" v-model="filters.date" @change="fetchNotifications">
      </div>
    </div>

    <!-- Notifications List -->
    <div class="notifications-list">
      <div class="notification-item" v-for="notification in notifications" :key="notification.id">
        <div class="notification-content">
          <span class="notification-type" :class="notification.type">
            {{ notification.type }}
          </span>
          <div class="notification-details">
            <h4>{{ notification.title }}</h4>
            <p>{{ notification.message }}</p>
            <small>{{ formatDate(notification.created_at) }}</small>
          </div>
        </div>
        <div class="notification-actions">
          <button class="btn btn-link" @click="markAsRead(notification.id)" v-if="!notification.read">
            <i class="fas fa-check"></i>
          </button>
          <button class="btn btn-link" @click="markAsUnread(notification.id)" v-else>
            <i class="fas fa-times"></i>
          </button>
          <button class="btn btn-link" @click="deleteNotification(notification.id)" v-if="!notification.system">
            <i class="fas fa-trash"></i>
          </button>
        </div>
      </div>
    </div>

    <!-- Notification Modal -->
    <div class="modal" v-if="showNotificationModal">
      <div class="modal-content">
        <h3>{{ modalMode === 'create' ? 'Create Notification' : 'Edit Notification' }}</h3>
        <form @submit.prevent="saveNotification">
          <div class="form-group">
            <label>Title</label>
            <input type="text" v-model="currentNotification.title" required>
          </div>
          <div class="form-group">
            <label>Message</label>
            <textarea v-model="currentNotification.message" required></textarea>
          </div>
          <div class="form-group">
            <label>Type</label>
            <select v-model="currentNotification.type">
              <option value="moderation">Moderation</option>
              <option value="role_assignment">Role Assignment</option>
              <option value="system">System</option>
              <option value="user_action">User Action</option>
            </select>
          </div>
          <div class="form-group">
            <label>Recipient</label>
            <select v-model="currentNotification.recipient_id">
              <option value="">All Users</option>
              <option v-for="user in users" :key="user.id" :value="user.id">
                {{ user.username }} ({{ user.email }})
              </option>
            </select>
          </div>
          <div class="form-actions">
            <button type="button" class="btn btn-secondary" @click="closeNotificationModal">
              Cancel
            </button>
            <button type="submit" class="btn btn-primary">
              {{ modalMode === 'create' ? 'Send' : 'Update' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useAdminStore } from '@/store/admin'
import { NotificationType, NotificationStatus } from '@/types/admin'

const adminStore = useAdminStore()

const notifications = computed(() => adminStore.notifications.notifications)
const users = computed(() => adminStore.users.users)
const loading = ref(false)
const error = ref(null)

// Notification Modal
const showNotificationModal = ref(false)
const modalMode = ref<'create' | 'edit'>('create')
const currentNotification = ref({
  title: '',
  message: '',
  type: NotificationType.SYSTEM,
  recipient_id: null,
  system: false
})

const openNotificationModal = (mode: 'create' | 'edit', notification?: any) => {
  modalMode.value = mode
  if (notification) {
    currentNotification.value = { ...notification }
  } else {
    currentNotification.value = {
      title: '',
      message: '',
      type: NotificationType.SYSTEM,
      recipient_id: null,
      system: false
    }
  }
  showNotificationModal.value = true
}

const closeNotificationModal = () => {
  showNotificationModal.value = false
}

const saveNotification = async () => {
  try {
    loading.value = true
    if (modalMode.value === 'create') {
      await adminStore.createNotification(currentNotification.value)
    } else {
      await adminStore.updateNotification(currentNotification.value.id, currentNotification.value)
    }
    closeNotificationModal()
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

// Filters
const filters = ref({
  type: '' as NotificationType | '',
  status: '' as NotificationStatus | '',
  date: ''
})

const fetchNotifications = async () => {
  try {
    loading.value = true
    await adminStore.getNotifications({
      type: filters.value.type,
      status: filters.value.status,
      date: filters.value.date
    })
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

// Actions
const markAsRead = async (notificationId: number) => {
  try {
    loading.value = true
    await adminStore.markNotificationAsRead(notificationId)
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

const markAsUnread = async (notificationId: number) => {
  try {
    loading.value = true
    await adminStore.markNotificationAsUnread(notificationId)
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

const deleteNotification = async (notificationId: number) => {
  if (!confirm('Are you sure you want to delete this notification?')) return
  try {
    loading.value = true
    await adminStore.deleteNotification(notificationId)
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchNotifications()
  adminStore.getUsers()
})

const formatDate = (dateString: string): string => {
  return new Date(dateString).toLocaleString()
}
</script>

<style scoped>
.notifications-page {
  padding: 20px;
}

.notifications-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.notifications-filters {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 10px;
}

.notifications-list {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.notification-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 15px;
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

.notification-details h4 {
  margin: 0 0 5px 0;
  color: #333;
}

.notification-details p {
  margin: 0 0 5px 0;
  color: #6c757d;
}

.notification-details small {
  color: #6c757d;
}

.notification-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
}

.modal-content {
  background: white;
  padding: 20px;
  border-radius: 8px;
  width: 90%;
  max-width: 600px;
}

.form-group {
  margin-bottom: 15px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}
</style>
