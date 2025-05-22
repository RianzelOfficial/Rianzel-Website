<template>
  <div class="categories-page">
    <!-- Categories Header -->
    <div class="categories-header">
      <h2>Categories Management</h2>
      <div class="header-actions">
        <button class="btn btn-primary" @click="openCategoryModal('create')">
          <i class="fas fa-plus"></i>
          <span>Create Category</span>
        </button>
      </div>
    </div>

    <!-- Filters -->
    <div class="categories-filters">
      <div class="filter-group">
        <label for="name">Name:</label>
        <input type="text" id="name" v-model="filters.name" @input="debouncedFetchCategories">
      </div>
      <div class="filter-group">
        <label for="status">Status:</label>
        <select id="status" v-model="filters.status" @change="fetchCategories">
          <option value="">All</option>
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
        </select>
      </div>
      <div class="filter-group">
        <label for="type">Type:</label>
        <select id="type" v-model="filters.type" @change="fetchCategories">
          <option value="">All</option>
          <option value="post">Posts</option>
          <option value="comment">Comments</option>
        </select>
      </div>
    </div>

    <!-- Categories Grid -->
    <div class="categories-grid">
      <div class="category-item" v-for="category in categories" :key="category.id">
        <div class="category-header">
          <h3>{{ category.name }}</h3>
          <div class="category-badge" :class="category.status">{{ category.status }}</div>
        </div>
        <div class="category-content">
          <p>{{ category.description }}</p>
          <div class="category-stats">
            <span>Posts: {{ category.post_count }}</span>
            <span>Comments: {{ category.comment_count }}</span>
          </div>
        </div>
        <div class="category-actions">
          <button class="btn btn-link" @click="openCategoryModal('edit', category)">
            <i class="fas fa-edit"></i>
          </button>
          <button class="btn btn-link" @click="toggleStatus(category)">
            <i :class="category.status === 'active' ? 'fas fa-toggle-on' : 'fas fa-toggle-off'"></i>
          </button>
          <button class="btn btn-link" @click="deleteCategory(category.id)" v-if="category.status === 'inactive'">
            <i class="fas fa-trash"></i>
          </button>
        </div>
      </div>
    </div>

    <!-- Category Modal -->
    <div class="modal" v-if="showCategoryModal">
      <div class="modal-content">
        <h3>{{ modalMode === 'create' ? 'Create Category' : 'Edit Category' }}</h3>
        <form @submit.prevent="saveCategory">
          <div class="form-group">
            <label>Name</label>
            <input type="text" v-model="currentCategory.name" required>
          </div>
          <div class="form-group">
            <label>Description</label>
            <textarea v-model="currentCategory.description"></textarea>
          </div>
          <div class="form-group">
            <label>Content Type</label>
            <select v-model="currentCategory.content_type">
              <option value="post">Posts</option>
              <option value="comment">Comments</option>
            </select>
          </div>
          <div class="form-group">
            <label>Status</label>
            <select v-model="currentCategory.status">
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
            </select>
          </div>
          <div class="form-group">
            <label>Parent Category</label>
            <select v-model="currentCategory.parent_id">
              <option value="">None</option>
              <option v-for="cat in parentCategories" :key="cat.id" :value="cat.id">
                {{ cat.name }}
              </option>
            </select>
          </div>
          <div class="form-actions">
            <button type="button" class="btn btn-secondary" @click="closeCategoryModal">
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
import { Category, CategoryStatus, ContentType } from '@/types/admin'

const adminStore = useAdminStore()

const categories = computed(() => adminStore.categories.categories)
const loading = ref(false)
const error = ref(null)

// Category Modal
const showCategoryModal = ref(false)
const modalMode = ref<'create' | 'edit'>('create')
const currentCategory = ref({
  name: '',
  description: '',
  content_type: ContentType.POST,
  status: CategoryStatus.ACTIVE,
  parent_id: null
} as Category)

const openCategoryModal = (mode: 'create' | 'edit', category?: Category) => {
  modalMode.value = mode
  if (category) {
    currentCategory.value = { ...category }
  } else {
    currentCategory.value = {
      name: '',
      description: '',
      content_type: ContentType.POST,
      status: CategoryStatus.ACTIVE,
      parent_id: null
    }
  }
  showCategoryModal.value = true
}

const closeCategoryModal = () => {
  showCategoryModal.value = false
}

const saveCategory = async () => {
  try {
    loading.value = true
    if (modalMode.value === 'create') {
      await adminStore.createCategory(currentCategory.value)
    } else {
      await adminStore.updateCategory(currentCategory.value.id, currentCategory.value)
    }
    closeCategoryModal()
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

// Parent Categories (for dropdown)
const parentCategories = computed(() => {
  return categories.value.filter(cat => !cat.parent_id)
})

// Filters
const filters = ref({
  name: '',
  status: '' as CategoryStatus | '',
  type: '' as ContentType | ''
})

const debouncedFetchCategories = useDebounce(() => {
  fetchCategories()
}, 300)

const fetchCategories = async () => {
  try {
    loading.value = true
    await adminStore.getCategories({
      name: filters.value.name,
      status: filters.value.status,
      content_type: filters.value.type
    })
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

// Status Toggle
const toggleStatus = async (category: Category) => {
  try {
    loading.value = true
    const newStatus = category.status === CategoryStatus.ACTIVE ? CategoryStatus.INACTIVE : CategoryStatus.ACTIVE
    await adminStore.updateCategory(category.id, { status: newStatus })
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

// Delete Category
const deleteCategory = async (categoryId: number) => {
  if (!confirm('Are you sure you want to delete this category?')) return
  try {
    loading.value = true
    await adminStore.deleteCategory(categoryId)
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchCategories()
})
</script>

<style scoped>
.categories-page {
  padding: 20px;
}

.categories-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.categories-filters {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 10px;
}

.categories-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.category-item {
  background: white;
  border-radius: 8px;
  padding: 20px;
  border: 1px solid #eee;
}

.category-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.category-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  margin-right: 8px;
}

.category-badge.active {
  background: #d4edda;
  color: #155724;
}

.category-badge.inactive {
  background: #f8d7da;
  color: #721c24;
}

.category-content {
  margin-bottom: 15px;
}

.category-stats {
  display: flex;
  gap: 20px;
  color: #6c757d;
}

.category-actions {
  display: flex;
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
