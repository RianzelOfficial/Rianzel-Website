<template>
  <div class="roles-page">
    <!-- Role Management Header -->
    <div class="roles-header">
      <h2>Role Management</h2>
      <div class="header-actions">
        <button class="btn btn-primary" @click="openRoleModal('create')">
          <i class="fas fa-plus"></i>
          <span>Create Role</span>
        </button>
      </div>
    </div>

    <!-- Filters -->
    <div class="roles-filters">
      <div class="filter-group">
        <label for="name">Name:</label>
        <input type="text" id="name" v-model="filters.name" @input="debouncedFetchRoles">
      </div>
      <div class="filter-group">
        <label for="status">Status:</label>
        <select id="status" v-model="filters.status" @change="fetchRoles">
          <option value="">All</option>
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
        </select>
      </div>
    </div>

    <!-- Role List -->
    <div class="roles-list">
      <div class="role-item" v-for="role in roles" :key="role.id">
        <div class="role-info">
          <h3>{{ role.name }}</h3>
          <p>{{ role.description }}</p>
          <div class="role-details">
            <span class="badge" :class="role.status">{{ role.status }}</span>
            <span class="badge">{{ role.users_count }} users</span>
          </div>
        </div>
        <div class="role-actions">
          <button class="btn btn-link" @click="openRoleModal('edit', role)">
            <i class="fas fa-edit"></i>
          </button>
          <button class="btn btn-link" @click="openPermissionsModal(role)">
            <i class="fas fa-key"></i>
          </button>
          <button class="btn btn-link" @click="deleteRole(role.id)" v-if="role.status === 'inactive'">
            <i class="fas fa-trash"></i>
          </button>
        </div>
      </div>
    </div>

    <!-- Role Modal -->
    <div class="modal" v-if="showRoleModal">
      <div class="modal-content">
        <h3>{{ modalMode === 'create' ? 'Create Role' : 'Edit Role' }}</h3>
        <form @submit.prevent="saveRole">
          <div class="form-group">
            <label>Name</label>
            <input type="text" v-model="currentRole.name" required>
          </div>
          <div class="form-group">
            <label>Description</label>
            <textarea v-model="currentRole.description"></textarea>
          </div>
          <div class="form-group">
            <label>Status</label>
            <select v-model="currentRole.status">
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
            </select>
          </div>
          <div class="form-actions">
            <button type="button" class="btn btn-secondary" @click="closeRoleModal">
              Cancel
            </button>
            <button type="submit" class="btn btn-primary">
              {{ modalMode === 'create' ? 'Create' : 'Update' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Permissions Modal -->
    <div class="modal" v-if="showPermissionsModal">
      <div class="modal-content">
        <h3>Manage Permissions</h3>
        <div class="permissions-grid">
          <div class="permission-category" v-for="(category, index) in permissionCategories" :key="index">
            <h4>{{ category.name }}</h4>
            <div class="permission-list">
              <div class="permission-item" v-for="permission in category.permissions" :key="permission">
                <input type="checkbox" :id="permission" :value="permission" v-model="selectedPermissions">
                <label :for="permission">{{ permission }}</label>
              </div>
            </div>
          </div>
        </div>
        <div class="form-actions">
          <button type="button" class="btn btn-secondary" @click="closePermissionsModal">
            Cancel
          </button>
          <button type="button" class="btn btn-primary" @click="savePermissions">
            Save Changes
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useAdminStore } from '@/store/admin'
import { Role, RoleStatus } from '@/types/admin'

const adminStore = useAdminStore()

const roles = computed(() => adminStore.roles.roles)
const loading = ref(false)
const error = ref(null)

// Role Modal
const showRoleModal = ref(false)
const modalMode = ref<'create' | 'edit'>('create')
const currentRole = ref({
  name: '',
  description: '',
  status: RoleStatus.ACTIVE
} as Role)

const openRoleModal = (mode: 'create' | 'edit', role?: Role) => {
  modalMode.value = mode
  if (role) {
    currentRole.value = { ...role }
  } else {
    currentRole.value = {
      name: '',
      description: '',
      status: RoleStatus.ACTIVE
    }
  }
  showRoleModal.value = true
}

const closeRoleModal = () => {
  showRoleModal.value = false
}

const saveRole = async () => {
  try {
    loading.value = true
    if (modalMode.value === 'create') {
      await adminStore.createRole(currentRole.value)
    } else {
      await adminStore.updateRole(currentRole.value.id, currentRole.value)
    }
    closeRoleModal()
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

// Permissions Modal
const showPermissionsModal = ref(false)
const selectedRole = ref<Role | null>(null)
const selectedPermissions = ref<string[]>([])

const permissionCategories = [
  {
    name: 'Content Management',
    permissions: ['create_post', 'edit_post', 'delete_post', 'approve_content']
  },
  {
    name: 'User Management',
    permissions: ['create_user', 'edit_user', 'delete_user', 'assign_role']
  },
  {
    name: 'Moderation',
    permissions: ['moderate_content', 'ban_user', 'manage_reports']
  },
  {
    name: 'System',
    permissions: ['manage_settings', 'view_logs', 'manage_roles']
  }
]

const openPermissionsModal = (role: Role) => {
  selectedRole.value = role
  selectedPermissions.value = role.permissions || []
  showPermissionsModal.value = true
}

const closePermissionsModal = () => {
  showPermissionsModal.value = false
}

const savePermissions = async () => {
  if (!selectedRole.value) return
  try {
    loading.value = true
    await adminStore.updateRole(selectedRole.value.id, {
      permissions: selectedPermissions.value
    })
    closePermissionsModal()
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

// Filters
const filters = ref({
  name: '',
  status: '' as RoleStatus | ''
})

const debouncedFetchRoles = useDebounce(() => {
  fetchRoles()
}, 300)

const fetchRoles = async () => {
  try {
    loading.value = true
    await adminStore.getRoles({
      name: filters.value.name,
      status: filters.value.status
    })
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

// Delete Role
const deleteRole = async (roleId: number) => {
  if (!confirm('Are you sure you want to delete this role?')) return
  try {
    loading.value = true
    await adminStore.deleteRole(roleId)
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchRoles()
})
</script>

<style scoped>
.roles-page {
  padding: 20px;
}

.roles-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.roles-filters {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 10px;
}

.roles-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.role-item {
  background: white;
  border-radius: 8px;
  padding: 20px;
  border: 1px solid #eee;
}

.role-info {
  flex: 1;
}

.role-actions {
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

.permissions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.permission-category {
  border: 1px solid #eee;
  padding: 15px;
  border-radius: 4px;
}

.permission-list {
  margin-top: 10px;
}

.permission-item {
  display: flex;
  align-items: center;
  margin-bottom: 5px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}
</style>
