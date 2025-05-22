<template>
  <div class="reports-page">
    <!-- Reports Header -->
    <div class="reports-header">
      <h2>Reports Management</h2>
      <div class="header-actions">
        <button class="btn btn-primary" @click="exportReports">
          <i class="fas fa-file-export"></i>
          <span>Export Reports</span>
        </button>
      </div>
    </div>

    <!-- Filters -->
    <div class="reports-filters">
      <div class="filter-group">
        <label for="status">Status:</label>
        <select id="status" v-model="filters.status" @change="fetchReports">
          <option value="">All</option>
          <option value="pending">Pending</option>
          <option value="resolved">Resolved</option>
          <option value="ignored">Ignored</option>
        </select>
      </div>
      <div class="filter-group">
        <label for="type">Content Type:</label>
        <select id="type" v-model="filters.type" @change="fetchReports">
          <option value="">All Types</option>
          <option value="post">Post</option>
          <option value="comment">Comment</option>
          <option value="user">User</option>
        </select>
      </div>
      <div class="filter-group">
        <label for="category">Category:</label>
        <select id="category" v-model="filters.category" @change="fetchReports">
          <option value="">All Categories</option>
          <option v-for="cat in categories" :key="cat.id" :value="cat.id">
            {{ cat.name }}
          </option>
        </select>
      </div>
      <div class="filter-group">
        <label for="date">Date Range:</label>
        <input type="date" id="date" v-model="filters.date" @change="fetchReports">
      </div>
    </div>

    <!-- Reports Table -->
    <div class="reports-table">
      <table>
        <thead>
          <tr>
            <th>Reporter</th>
            <th>Content</th>
            <th>Type</th>
            <th>Category</th>
            <th>Reason</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="report in reports" :key="report.id">
            <td>
              <span class="user-badge">
                {{ report.reporter.username }}
                <span class="role-tag" :class="report.reporter.role">{{ report.reporter.role }}</span>
              </span>
            </td>
            <td>
              <div class="content-preview">
                <h4>{{ report.title }}</h4>
                <p>{{ report.content }}</p>
              </div>
            </td>
            <td>
              <span class="type-tag" :class="report.type">
                {{ report.type }}
              </span>
            </td>
            <td>{{ report.category.name }}</td>
            <td>{{ report.reason }}</td>
            <td>
              <span class="status-tag" :class="report.status">
                {{ report.status }}
              </span>
            </td>
            <td>
              <div class="action-buttons">
                <button class="btn btn-link" @click="openReportModal(report)">
                  <i class="fas fa-eye"></i>
                </button>
                <button class="btn btn-link" @click="resolveReport(report.id)" v-if="report.status === 'pending'">
                  <i class="fas fa-check"></i>
                </button>
                <button class="btn btn-link" @click="ignoreReport(report.id)" v-if="report.status === 'pending'">
                  <i class="fas fa-times"></i>
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Report Modal -->
    <div class="modal" v-if="showReportModal">
      <div class="modal-content">
        <h3>Report Details</h3>
        <div class="report-details">
          <div class="detail-item">
            <span class="label">Reporter:</span>
            <span class="value">
              {{ selectedReport.reporter.username }}
              <span class="role-tag" :class="selectedReport.reporter.role">{{ selectedReport.reporter.role }}</span>
            </span>
          </div>
          <div class="detail-item">
            <span class="label">Content:</span>
            <div class="content-preview">
              <h4>{{ selectedReport.title }}</h4>
              <p>{{ selectedReport.content }}</p>
            </div>
          </div>
          <div class="detail-item">
            <span class="label">Type:</span>
            <span class="value">
              <span class="type-tag" :class="selectedReport.type">
                {{ selectedReport.type }}
              </span>
            </span>
          </div>
          <div class="detail-item">
            <span class="label">Category:</span>
            <span class="value">{{ selectedReport.category.name }}</span>
          </div>
          <div class="detail-item">
            <span class="label">Reason:</span>
            <span class="value">{{ selectedReport.reason }}</span>
          </div>
          <div class="detail-item">
            <span class="label">Status:</span>
            <span class="value">
              <span class="status-tag" :class="selectedReport.status">
                {{ selectedReport.status }}
              </span>
            </span>
          </div>
          <div class="detail-item">
            <span class="label">Created At:</span>
            <span class="value">{{ formatDate(selectedReport.created_at) }}</span>
          </div>
          <div class="detail-item">
            <span class="label">Resolved At:</span>
            <span class="value">{{ formatDate(selectedReport.resolved_at) }}</span>
          </div>
          <div class="detail-item" v-if="selectedReport.resolution_notes">
            <span class="label">Resolution Notes:</span>
            <pre class="value">{{ selectedReport.resolution_notes }}</pre>
          </div>
        </div>
        <div class="form-actions">
          <button type="button" class="btn btn-secondary" @click="closeReportModal">
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
import { ReportStatus, ReportType } from '@/types/admin'

const adminStore = useAdminStore()

const reports = computed(() => adminStore.reports.reports)
const categories = computed(() => adminStore.categories.categories)
const loading = ref(false)
const error = ref(null)

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

// Filters
const filters = ref({
  status: '' as ReportStatus | '',
  type: '' as ReportType | '',
  category: '',
  date: ''
})

const fetchReports = async () => {
  try {
    loading.value = true
    await adminStore.getReports({
      status: filters.value.status,
      type: filters.value.type,
      category: filters.value.category,
      date: filters.value.date
    })
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

// Actions
const resolveReport = async (reportId: number) => {
  try {
    loading.value = true
    await adminStore.resolveReport(reportId)
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

const ignoreReport = async (reportId: number) => {
  if (!confirm('Are you sure you want to ignore this report?')) return
  try {
    loading.value = true
    await adminStore.ignoreReport(reportId)
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

// Export Reports
const exportReports = async () => {
  try {
    loading.value = true
    const blob = new Blob([
      JSON.stringify(reports.value, null, 2)
    ], { type: 'application/json' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `reports-${new Date().toISOString()}.json`
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
  fetchReports()
  adminStore.getCategories()
})

const formatDate = (dateString: string): string => {
  return new Date(dateString).toLocaleString()
}
</script>

<style scoped>
.reports-page {
  padding: 20px;
}

.reports-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.reports-filters {
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

.reports-table {
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

.content-preview {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.content-preview h4 {
  margin: 0;
  color: #333;
}

.content-preview p {
  margin: 0;
  color: #6c757d;
}

.type-tag {
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
}

.type-tag.post {
  background: #d4edda;
  color: #155724;
}

.type-tag.comment {
  background: #fff3cd;
  color: #856404;
}

.type-tag.user {
  background: #cce5ff;
  color: #004085;
}

.status-tag {
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
}

.status-tag.pending {
  background: #fff3cd;
  color: #856404;
}

.status-tag.resolved {
  background: #d4edda;
  color: #155724;
}

.status-tag.ignored {
  background: #f8d7da;
  color: #721c24;
}

.action-buttons {
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

.report-details {
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
