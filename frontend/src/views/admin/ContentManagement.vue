<template>
  <div class="content-management-page">
    <!-- Content Header -->
    <div class="content-header">
      <h2>Content Management</h2>
      <div class="header-actions">
        <button class="btn btn-primary" @click="openContentModal('create')">
          <i class="fas fa-plus"></i>
          <span>Create Content</span>
        </button>
      </div>
    </div>

    <!-- Filters -->
    <div class="content-filters">
      <div class="filter-group">
        <label for="type">Type:</label>
        <select id="type" v-model="filters.type" @change="fetchContent">
          <option value="">All Types</option>
          <option value="post">Post</option>
          <option value="page">Page</option>
          <option value="article">Article</option>
          <option value="media">Media</option>
        </select>
      </div>
      <div class="filter-group">
        <label for="status">Status:</label>
        <select id="status" v-model="filters.status" @change="fetchContent">
          <option value="">All Statuses</option>
          <option value="published">Published</option>
          <option value="draft">Draft</option>
          <option value="archived">Archived</option>
          <option value="pending">Pending</option>
        </select>
      </div>
      <div class="filter-group">
        <label for="category">Category:</label>
        <select id="category" v-model="filters.category" @change="fetchContent">
          <option value="">All Categories</option>
          <option v-for="cat in categories" :key="cat.id" :value="cat.id">
            {{ cat.name }}
          </option>
        </select>
      </div>
      <div class="filter-group">
        <label for="author">Author:</label>
        <select id="author" v-model="filters.author" @change="fetchContent">
          <option value="">All Authors</option>
          <option v-for="user in users" :key="user.id" :value="user.id">
            {{ user.username }}
          </option>
        </select>
      </div>
    </div>

    <!-- Content Grid -->
    <div class="content-grid">
      <div class="content-card" v-for="content in contents" :key="content.id">
        <div class="content-header">
          <h3>{{ content.title }}</h3>
          <div class="content-meta">
            <span class="status-tag" :class="content.status">
              {{ content.status }}
            </span>
            <span class="type-tag" :class="content.type">
              {{ content.type }}
            </span>
          </div>
        </div>
        <div class="content-body">
          <img v-if="content.thumbnail" :src="content.thumbnail" :alt="content.title" class="thumbnail">
          <p>{{ content.excerpt }}</p>
        </div>
        <div class="content-footer">
          <div class="content-info">
            <span class="author">{{ content.author.username }}</span>
            <span class="category">{{ content.category.name }}</span>
            <span class="date">{{ formatDate(content.created_at) }}</span>
          </div>
          <div class="content-actions">
            <button class="btn btn-link" @click="openContentModal('edit', content)">
              <i class="fas fa-edit"></i>
            </button>
            <button class="btn btn-link" @click="publishContent(content.id)" v-if="content.status !== 'published'">
              <i class="fas fa-check"></i>
            </button>
            <button class="btn btn-link" @click="archiveContent(content.id)" v-if="content.status !== 'archived'">
              <i class="fas fa-archive"></i>
            </button>
            <button class="btn btn-link" @click="deleteContent(content.id)" v-if="content.status !== 'archived'">
              <i class="fas fa-trash"></i>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Content Modal -->
    <div class="modal" v-if="showContentModal">
      <div class="modal-content">
        <h3>{{ modalMode === 'create' ? 'Create Content' : 'Edit Content' }}</h3>
        <form @submit.prevent="saveContent">
          <div class="form-group">
            <label>Title</label>
            <input type="text" v-model="currentContent.title" required>
          </div>
          <div class="form-group">
            <label>Type</label>
            <select v-model="currentContent.type" required>
              <option value="post">Post</option>
              <option value="page">Page</option>
              <option value="article">Article</option>
              <option value="media">Media</option>
            </select>
          </div>
          <div class="form-group">
            <label>Category</label>
            <select v-model="currentContent.category_id" required>
              <option v-for="cat in categories" :key="cat.id" :value="cat.id">
                {{ cat.name }}
              </option>
            </select>
          </div>
          <div class="form-group">
            <label>Author</label>
            <select v-model="currentContent.author_id" required>
              <option v-for="user in users" :key="user.id" :value="user.id">
                {{ user.username }}
              </option>
            </select>
          </div>
          <div class="form-group">
            <label>Thumbnail</label>
            <input type="file" @change="handleFileUpload">
          </div>
          <div class="form-group">
            <label>Content</label>
            <textarea v-model="currentContent.content" required></textarea>
          </div>
          <div class="form-group">
            <label>Status</label>
            <select v-model="currentContent.status" required>
              <option value="draft">Draft</option>
              <option value="published">Published</option>
              <option value="pending">Pending</option>
            </select>
          </div>
          <div class="form-actions">
            <button type="button" class="btn btn-secondary" @click="closeContentModal">
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
import { ContentType, ContentStatus } from '@/types/admin'

const adminStore = useAdminStore()

const contents = computed(() => adminStore.contents.contents)
const categories = computed(() => adminStore.categories.categories)
const users = computed(() => adminStore.users.users)
const loading = ref(false)
const error = ref(null)

// Content Modal
const showContentModal = ref(false)
const modalMode = ref<'create' | 'edit'>('create')
const currentContent = ref({
  title: '',
  type: ContentType.POST,
  category_id: null,
  author_id: null,
  thumbnail: null,
  content: '',
  status: ContentStatus.DRAFT
})

const openContentModal = (mode: 'create' | 'edit', content?: any) => {
  modalMode.value = mode
  if (content) {
    currentContent.value = { ...content }
  } else {
    currentContent.value = {
      title: '',
      type: ContentType.POST,
      category_id: null,
      author_id: null,
      thumbnail: null,
      content: '',
      status: ContentStatus.DRAFT
    }
  }
  showContentModal.value = true
}

const closeContentModal = () => {
  showContentModal.value = false
}

const handleFileUpload = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files[0]) {
    currentContent.value.thumbnail = target.files[0]
  }
}

const saveContent = async () => {
  try {
    loading.value = true
    if (modalMode.value === 'create') {
      await adminStore.createContent(currentContent.value)
    } else {
      await adminStore.updateContent(currentContent.value.id, currentContent.value)
    }
    closeContentModal()
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

// Filters
const filters = ref({
  type: '' as ContentType | '',
  status: '' as ContentStatus | '',
  category: '',
  author: ''
})

const fetchContent = async () => {
  try {
    loading.value = true
    await adminStore.getContent({
      type: filters.value.type,
      status: filters.value.status,
      category: filters.value.category,
      author: filters.value.author
    })
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

// Actions
const publishContent = async (contentId: number) => {
  try {
    loading.value = true
    await adminStore.publishContent(contentId)
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

const archiveContent = async (contentId: number) => {
  if (!confirm('Are you sure you want to archive this content?')) return
  try {
    loading.value = true
    await adminStore.archiveContent(contentId)
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

const deleteContent = async (contentId: number) => {
  if (!confirm('Are you sure you want to delete this content?')) return
  try {
    loading.value = true
    await adminStore.deleteContent(contentId)
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchContent()
  adminStore.getCategories()
  adminStore.getUsers()
})

const formatDate = (dateString: string): string => {
  return new Date(dateString).toLocaleString()
}
</script>

<style scoped>
.content-management-page {
  padding: 20px;
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.content-filters {
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

.content-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.content-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.content-meta {
  display: flex;
  gap: 10px;
}

.status-tag {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.status-tag.draft {
  background: #fff3cd;
  color: #856404;
}

.status-tag.published {
  background: #d4edda;
  color: #155724;
}

.status-tag.pending {
  background: #f8d7da;
  color: #721c24;
}

.status-tag.archived {
  background: #e9ecef;
  color: #495057;
}

.type-tag {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.type-tag.post {
  background: #d4edda;
  color: #155724;
}

.type-tag.page {
  background: #fff3cd;
  color: #856404;
}

.type-tag.article {
  background: #cce5ff;
  color: #004085;
}

.type-tag.media {
  background: #f8d7da;
  color: #721c24;
}

.thumbnail {
  width: 100%;
  height: 200px;
  object-fit: cover;
  border-radius: 4px;
  margin-bottom: 15px;
}

.content-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 15px;
}

.content-info {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.content-actions {
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
  max-width: 800px;
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
