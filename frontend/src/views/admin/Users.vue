<template>
  <div class="users-page">
    <!-- Users Header -->
    <div class="users-header">
      <h2>User Management</h2>
      <div class="header-actions">
        <button class="btn btn-primary" @click="openUserModal('create')">
          <i class="fas fa-plus"></i>
          <span>Create User</span>
        </button>
      </div>
    </div>

    <!-- Filters -->
    <div class="users-filters">
      <div class="filter-group">
        <label for="username">Username:</label>
        <input type="text" id="username" v-model="filters.username" @input="debouncedFetchUsers">
      </div>
      <div class="filter-group">
        <label for="email">Email:</label>
        <input type="email" id="email" v-model="filters.email" @input="debouncedFetchUsers">
      </div>
      <div class="filter-group">
        <label for="status">Status:</label>
        <select id="status" v-model="filters.status" @change="fetchUsers">
          <option value="">All</option>
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
          <option value="banned">Banned</option>
        </select>
      </div>
      <div class="filter-group">
        <label for="role">Role:</label>
        <select id="role" v-model="filters.role" @change="fetchUsers">
          <option value="">All Roles</option>
          <option v-for="role in roles" :key="role.id" :value="role.id">
            {{ role.name }}
          </option>
        </select>
      </div>
    </div>

    <!-- Users Table -->
    <div class="users-table">
      <table>
        <thead>
          <tr>
            <th>Username</th>
            <th>Email</th>
            <th>Role</th>
            <th>Status</th>
            <th>Last Login</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.id">
            <td>{{ user.username }}</td>
            <td>{{ user.email }}</td>
            <td>
              <span class="badge" :class="user.role">{{ user.role }}</span>
            </td>
            <td>
              <span class="badge" :class="user.status">{{ user.status }}</span>
            </td>
            <td>{{ formatDate(user.last_login) }}</td>
            <td>
              <div class="action-buttons">
                <button class="btn btn-link" @click="openUserModal('edit', user)">
                  <i class="fas fa-edit"></i>
                </button>
                <button class="btn btn-link" @click="toggleStatus(user)">
                  <i :class="user.status === 'active' ? 'fas fa-toggle-on' : 'fas fa-toggle-off'"></i>
                </button>
                <button class="btn btn-link" @click="banUser(user.id)" v-if="user.status !== 'banned'">
                  <i class="fas fa-ban"></i>
                </button>
                <button class="btn btn-link" @click="unbanUser(user.id)" v-else>
                  <i class="fas fa-undo"></i>
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- User Modal -->
    <div class="modal" v-if="showUserModal">
      <div class="modal-content">
        <h3>{{ modalMode === 'create' ? 'Create User' : 'Edit User' }}</h3>
        <form @submit.prevent="saveUser">
          <div class="form-group">
            <label>Username</label>
            <input type="text" v-model="currentUser.username" required>
          </div>
          <div class="form-group">
            <label>Email</label>
            <input type="email" v-model="currentUser.email" required>
          </div>
          <div class="form-group" v-if="modalMode === 'create'">
            <label>Password</label>
            <input type="password" v-model="currentUser.password" required>
          </div>
          <div class="form-group">
            <label>Role</label>
            <select v-model="currentUser.role_id">
              <option v-for="role in roles" :key="role.id" :value="role.id">
                {{ role.name }}
              </option>
            </select>
          </div>
          <div class="form-group">
            <label>Status</label>
            <select v-model="currentUser.status">
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
            </select>
          </div>
          <div class="form-actions">
            <button type="button" class="btn btn-secondary" @click="closeUserModal">
              Cancel
            </button>
            <button type="submit" class="btn btn-primary">
              {{ modalMode === 'create' ? 'Create' : 'Update' }}
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
import { UserStatus, Role } from '@/types/admin'

const adminStore = useAdminStore()

const users = computed(() => adminStore.users.users)
const roles = computed(() => adminStore.roles.roles)
const loading = ref(false)
const error = ref(null)

// User Modal
const showUserModal = ref(false)
const modalMode = ref<'create' | 'edit'>('create')
const currentUser = ref({
  username: '',
  email: '',
  password: '',
  role_id: null,
  status: UserStatus.ACTIVE
})

const openUserModal = (mode: 'create' | 'edit', user?: any) => {
  modalMode.value = mode
  if (user) {
    currentUser.value = { ...user }
  } else {
    currentUser.value = {
      username: '',
      email: '',
      password: '',
      role_id: null,
      status: UserStatus.ACTIVE
    }
  }
  showUserModal.value = true
}

const closeUserModal = () => {
  showUserModal.value = false
}

const saveUser = async () => {
  try {
    loading.value = true
    if (modalMode.value === 'create') {
      await adminStore.createUser(currentUser.value)
    } else {
      await adminStore.updateUser(currentUser.value.id, currentUser.value)
    }
    closeUserModal()
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

// Filters
const filters = ref({
  username: '',
  email: '',
  status: '' as UserStatus | '',
  role: ''
})

const debouncedFetchUsers = useDebounce(() => {
  fetchUsers()
}, 300)

const fetchUsers = async () => {
  try {
    loading.value = true
    await adminStore.getUsers({
      username: filters.value.username,
      email: filters.value.email,
      status: filters.value.status,
      role: filters.value.role
    })
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

// Status Toggle
const toggleStatus = async (user: any) => {
  try {
    loading.value = true
    const newStatus = user.status === UserStatus.ACTIVE ? UserStatus.INACTIVE : UserStatus.ACTIVE
    await adminStore.updateUser(user.id, { status: newStatus })
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

// Ban/Unban User
const banUser = async (userId: number) => {
  if (!confirm('Are you sure you want to ban this user?')) return
  try {
    loading.value = true
    await adminStore.updateUser(userId, { status: UserStatus.BANNED })
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

const unbanUser = async (userId: number) => {
  if (!confirm('Are you sure you want to unban this user?')) return
  try {
    loading.value = true
    await adminStore.updateUser(userId, { status: UserStatus.ACTIVE })
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchUsers()
  adminStore.getRoles()
})

const formatDate = (dateString: string): string => {
  return new Date(dateString).toLocaleString()
}
</script>

<style scoped>
.users-page {
  padding: 20px;
}

.users-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.users-filters {
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

.users-table {
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

.action-buttons {
  display: flex;
  gap: 10px;
}

.badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  margin-right: 8px;
}

.badge.active {
  background: #d4edda;
  color: #155724;
}

.badge.inactive {
  background: #f8d7da;
  color: #721c24;
}

.badge.banned {
  background: #f8d7da;
  color: #721c24;
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
