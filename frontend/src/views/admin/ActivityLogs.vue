<template>
  <div class="activity-logs-page">
    <!-- Activity Header -->
    <div class="activity-header">
      <h2>Activity Logs</h2>
      <div class="header-actions">
        <button class="btn btn-primary" @click="exportLogs">
          <i class="fas fa-file-export"></i>
          <span>Export Logs</span>
        </button>
      </div>
    </div>

    <!-- Filters -->
    <div class="activity-filters">
      <div class="filter-group">
        <label for="user">User:</label>
        <input type="text" id="user" v-model="filters.username" @input="debouncedFetchLogs">
      </div>
      <div class="filter-group">
        <label for="action">Action:</label>
        <select id="action" v-model="filters.action" @change="fetchLogs">
          <option value="">All Actions</option>
          <option value="login">Login</option>
          <option value="logout">Logout</option>
          <option value="create">Create</option>
          <option value="update">Update</option>
          <option value="delete">Delete</option>
          <option value="moderate">Moderate</option>
        </select>
      </div>
      <div class="filter-group">
        <label for="date">Date Range:</label>
        <input type="date" id="date" v-model="filters.date" @change="fetchLogs">
      </div>
      <div class="filter-group">
        <label for="type">Log Type:</label>
        <select id="type" v-model="filters.type" @change="fetchLogs">
          <option value="">All Types</option>
          <option value="user">User Activity</option>
          <option value="content">Content</option>
          <option value="moderation">Moderation</option>
          <option value="system">System</option>
        </select>
      </div>
    </div>

    <!-- Activity Table -->
    <div class="activity-table">
      <table>
        <thead>
          <tr>
            <th>User</th>
            <th>Action</th>
            <th>Type</th>
            <th>Description</th>
            <th>IP Address</th>
            <th>Time</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="log in logs" :key="log.id">
            <td>
              <span class="user-badge">
                {{ log.user.username }}
                <span class="role-tag" :class="log.user.role">{{ log.user.role }}</span>
              </span>
            </td>
            <td>
              <span class="action-tag" :class="log.action">
                {{ log.action }}
              </span>
            </td>
            <td>
              <span class="type-tag" :class="log.type">
                {{ log.type }}
              </span>
            </td>
            <td>{{ log.description }}</td>
            <td>{{ log.ip_address }}</td>
            <td>{{ formatDate(log.created_at) }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Log Details Modal -->
    <div class="modal" v-if="showLogModal">
      <div class="modal-content">
        <h3>Log Details</h3>
        <div class="log-details">
          <div class="detail-item">
            <span class="label">User:</span>
            <span class="value">
              {{ selectedLog.user.username }}
              <span class="role-tag" :class="selectedLog.user.role">{{ selectedLog.user.role }}</span>
            </span>
          </div>
          <div class="detail-item">
            <span class="label">Action:</span>
            <span class="value">
              <span class="action-tag" :class="selectedLog.action">
                {{ selectedLog.action }}
              </span>
            </span>
          </div>
          <div class="detail-item">
            <span class="label">Type:</span>
            <span class="value">
              <span class="type-tag" :class="selectedLog.type">
                {{ selectedLog.type }}
              </span>
            </span>
          </div>
          <div class="detail-item">
            <span class="label">Description:</span>
            <span class="value">{{ selectedLog.description }}</span>
          </div>
          <div class="detail-item">
            <span class="label">IP Address:</span>
            <span class="value">{{ selectedLog.ip_address }}</span>
          </div>
          <div class="detail-item">
            <span class="label">Time:</span>
            <span class="value">{{ formatDate(selectedLog.created_at) }}</span>
          </div>
          <div class="detail-item" v-if="selectedLog.meta_data">
            <span class="label">Meta Data:</span>
            <pre class="value">{{ JSON.stringify(selectedLog.meta_data, null, 2) }}</pre>
          </div>
        </div>
        <div class="form-actions">
          <button type="button" class="btn btn-secondary" @click="closeLogModal">
            Close
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useAdminStore } from '@/store/admin'
import { ActivityLogType, ActivityLogAction } from '@/types/admin'

const adminStore = useAdminStore()

const logs = computed(() => adminStore.activityLogs.logs)
const loading = ref(false)
const error = ref(null)

// Log Details Modal
const showLogModal = ref(false)
const selectedLog = ref(null)

const openLogModal = (log) => {
  selectedLog.value = log
  showLogModal.value = true
}

const closeLogModal = () => {
  showLogModal.value = false
}

// Filters
const filters = ref({
  username: '',
  action: '' as ActivityLogAction | '',
  type: '' as ActivityLogType | '',
  date: ''
})

const debouncedFetchLogs = useDebounce(() => {
  fetchLogs()
}, 300)

const fetchLogs = async () => {
  try {
    loading.value = true
    await adminStore.getActivityLogs({
      username: filters.value.username,
      action: filters.value.action,
      type: filters.value.type,
      date: filters.value.date
    })
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

// Export Logs
const exportLogs = async () => {
  try {
    loading.value = true
    const blob = new Blob([
      JSON.stringify(logs.value, null, 2)
    ], { type: 'application/json' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `activity-logs-${new Date().toISOString()}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchLogs()
})

const formatDate = (dateString: string): string => {
  return new Date(dateString).toLocaleString()
}
</script>

<style scoped>
.activity-logs-page {
  padding: 20px;
}

.activity-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.activity-filters {
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

.activity-table {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

th {
  background: #f8f9fa;
  font-weight: 600;
}

.user-badge {
  display: flex;
  align-items: center;
  gap: 8px;
}

.role-tag {
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
  margin-left: 8px;
}

.role-tag.admin {
  background: #d4edda;
  color: #155724;
}

.role-tag.moderator {
  background: #fff3cd;
  color: #856404;
}

.role-tag.user {
  background: #cce5ff;
  color: #004085;
}

.action-tag {
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
}

.action-tag.login {
  background: #d4edda;
  color: #155724;
}

.action-tag.logout {
  background: #f8d7da;
  color: #721c24;
}

.action-tag.create {
  background: #d4edda;
  color: #155724;
}

.action-tag.update {
  background: #fff3cd;
  color: #856404;
}

.action-tag.delete {
  background: #f8d7da;
  color: #721c24;
}

.type-tag {
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
}

.type-tag.user {
  background: #d4edda;
  color: #155724;
}

.type-tag.content {
  background: #fff3cd;
  color: #856404;
}

.type-tag.moderation {
  background: #f8d7da;
  color: #721c24;
}

.type-tag.system {
  background: #cce5ff;
  color: #004085;
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
  max-width: 800px;
}

.log-details {
  margin-bottom: 20px;
}

.detail-item {
  display: flex;
  align-items: flex-start;
  margin-bottom: 15px;
}

.label {
  width: 120px;
  font-weight: 600;
  color: #6c757d;
}

.value {
  flex: 1;
  word-break: break-word;
}

pre {
  background: #f8f9fa;
  padding: 10px;
  border-radius: 4px;
  overflow-x: auto;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}
</style>
