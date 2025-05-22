<template>
  <div class="moderation-page">
    <!-- Moderation Header -->
    <div class="moderation-header">
      <h2>Content Moderation</h2>
      <div class="header-actions">
        <button class="btn btn-primary" @click="openModerationModal">
          <i class="fas fa-filter"></i>
          <span>Filters</span>
        </button>
      </div>
    </div>

    <!-- Moderation Stats -->
    <div class="moderation-stats">
      <div class="stat-card">
        <h3>Pending Moderation</h3>
        <p>{{ stats.pending }}</p>
      </div>
      <div class="stat-card">
        <h3>Approved Today</h3>
        <p>{{ stats.approved_today }}</p>
      </div>
      <div class="stat-card">
        <h3>Rejected Today</h3>
        <p>{{ stats.rejected_today }}</p>
      </div>
    </div>

    <!-- Moderation Queue -->
    <div class="moderation-queue">
      <h3>Moderation Queue</h3>
      <div class="queue-filters">
        <select v-model="filters.status" @change="fetchQueue">
          <option value="">All</option>
          <option value="pending">Pending</option>
          <option value="approved">Approved</option>
          <option value="rejected">Rejected</option>
        </select>
        <select v-model="filters.content_type" @change="fetchQueue">
          <option value="">All Content</option>
          <option value="post">Posts</option>
          <option value="comment">Comments</option>
        </select>
      </div>
      
      <div class="queue-items">
        <div v-for="item in queue" :key="item.id" class="queue-item">
          <div class="item-header">
            <span class="item-type" :class="item.type">
              {{ item.type }}
            </span>
            <span class="item-status" :class="item.status">
              {{ item.status }}
            </span>
          </div>
          <div class="item-content">
            <h4>{{ item.title || item.content }}</h4>
            <p v-if="item.author">By: {{ item.author }}</p>
            <p v-if="item.category">Category: {{ item.category }}</p>
          </div>
          <div class="item-actions">
            <button class="btn btn-success" @click="approve(item)">
              <i class="fas fa-check"></i>
            </button>
            <button class="btn btn-danger" @click="reject(item)">
              <i class="fas fa-times"></i>
            </button>
            <button class="btn btn-secondary" @click="viewDetails(item)">
              <i class="fas fa-eye"></i>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Moderation Modal -->
    <div class="modal" v-if="showModerationModal">
      <div class="modal-content">
        <h3>Moderation Filters</h3>
        <form @submit.prevent="applyFilters">
          <div class="form-group">
            <label>Content Type</label>
            <select v-model="filters.content_type">
              <option value="">All</option>
              <option value="post">Posts</option>
              <option value="comment">Comments</option>
            </select>
          </div>
          <div class="form-group">
            <label>Status</label>
            <select v-model="filters.status">
              <option value="">All</option>
              <option value="pending">Pending</option>
              <option value="approved">Approved</option>
              <option value="rejected">Rejected</option>
            </select>
          </div>
          <div class="form-group">
            <label>Category</label>
            <select v-model="filters.category">
              <option value="">All</option>
              <option v-for="cat in categories" :key="cat.id" :value="cat.name">
                {{ cat.name }}
              </option>
            </select>
          </div>
          <div class="form-actions">
            <button type="button" class="btn btn-secondary" @click="closeModerationModal">
              Cancel
            </button>
            <button type="submit" class="btn btn-primary">
              Apply Filters
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Report Modal -->
    <div class="modal" v-if="showReportModal">
      <div class="modal-content">
        <h3>Report Details</h3>
        <div class="report-content">
          <h4>{{ selectedReport.title || selectedReport.content }}</h4>
          <p><strong>Author:</strong> {{ selectedReport.author }}</p>
          <p><strong>Category:</strong> {{ selectedReport.category }}</p>
          <p><strong>Content Type:</strong> {{ selectedReport.type }}</p>
          <p><strong>Status:</strong> {{ selectedReport.status }}</p>
          <p><strong>Created:</strong> {{ formatDate(selectedReport.created_at) }}</p>
          <div class="report-actions">
            <button class="btn btn-success" @click="approveReport">
              <i class="fas fa-check"></i> Approve
            </button>
            <button class="btn btn-danger" @click="rejectReport">
              <i class="fas fa-times"></i> Reject
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useAdminStore } from '@/store/admin'
import { ModerationStatus, ContentType } from '@/types/admin'

const adminStore = useAdminStore()

const queue = computed(() => adminStore.moderationLogs.logs)
const stats = computed(() => {
  return {
    pending: adminStore.moderationLogs.pending_count,
    approved_today: adminStore.moderationLogs.by_category['approved'] || 0,
    rejected_today: adminStore.moderationLogs.by_category['rejected'] || 0
  }
})

// Moderation Modal
const showModerationModal = ref(false)

const filters = ref({
  status: '' as ModerationStatus | '',
  content_type: '' as ContentType | '',
  category: ''
})

const openModerationModal = () => {
  showModerationModal.value = true
}

const closeModerationModal = () => {
  showModerationModal.value = false
}

const applyFilters = async () => {
  try {
    await adminStore.getContentModerationLogs({
      status: filters.value.status,
      content_type: filters.value.content_type,
      category: filters.value.category
    })
  } catch (error) {
    console.error('Error applying filters:', error)
  } finally {
    closeModerationModal()
  }
}

// Report Modal
const showReportModal = ref(false)
const selectedReport = ref(null)

const openReportModal = (report) => {
  selectedReport.value = report
  showReportModal.value = true
}

const closeReportModal = () => {
  showReportModal.value = false
}

const approve = async (item) => {
  try {
    await adminStore.approveContent(item.id, item.type)
    await fetchQueue()
  } catch (error) {
    console.error('Error approving content:', error)
  }
}

const reject = async (item) => {
  try {
    await adminStore.rejectContent(item.id, item.type, 'Content not appropriate')
    await fetchQueue()
  } catch (error) {
    console.error('Error rejecting content:', error)
  }
}

const viewDetails = (item) => {
  openReportModal(item)
}

const approveReport = async () => {
  if (!selectedReport.value) return
  try {
    await adminStore.approveContent(selectedReport.value.id, selectedReport.value.type)
    closeReportModal()
    await fetchQueue()
  } catch (error) {
    console.error('Error approving report:', error)
  }
}

const rejectReport = async () => {
  if (!selectedReport.value) return
  try {
    await adminStore.rejectContent(selectedReport.value.id, selectedReport.value.type, 'Content not appropriate')
    closeReportModal()
    await fetchQueue()
  } catch (error) {
    console.error('Error rejecting report:', error)
  }
}

const fetchQueue = async () => {
  try {
    await adminStore.getContentModerationLogs({
      status: filters.value.status,
      content_type: filters.value.content_type,
      category: filters.value.category
    })
  } catch (error) {
    console.error('Error fetching queue:', error)
  }
}

onMounted(() => {
  fetchQueue()
})

const formatDate = (dateString: string): string => {
  return new Date(dateString).toLocaleString()
}
</script>

<style scoped>
.moderation-page {
  padding: 20px;
}

.moderation-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.moderation-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: white;
  padding: 20px;
  border-radius: 8px;
  text-align: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.stat-card h3 {
  color: #6c757d;
  margin: 0 0 10px 0;
}

.stat-card p {
  font-size: 24px;
  font-weight: bold;
  margin: 0;
  color: #333;
}

.moderation-queue {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.queue-filters {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.queue-items {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.queue-item {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 4px;
}

.item-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}

.item-type {
  background: #e9ecef;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.item-status {
  background: #fff3cd;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.item-content h4 {
  margin: 0 0 5px 0;
  color: #333;
}

.item-content p {
  margin: 0;
  color: #6c757d;
}

.item-actions {
  display: flex;
  gap: 10px;
  margin-top: 10px;
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

.report-content {
  margin-bottom: 20px;
}

.report-content h4 {
  margin: 0 0 10px 0;
}

.report-content p {
  margin: 5px 0;
}

.report-actions {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}
</style>
