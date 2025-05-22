<template>
  <div class="dashboard">
    <!-- Overview Cards -->
    <div class="dashboard-cards">
      <div class="card">
        <div class="card-header">
          <h3>Total Users</h3>
          <i class="fas fa-users"></i>
        </div>
        <div class="card-body">
          <h2>{{ stats.total_users }}</h2>
          <p>New Today: {{ stats.new_users_today }}</p>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <h3>Active Users</h3>
          <i class="fas fa-chart-line"></i>
        </div>
        <div class="card-body">
          <h2>{{ stats.active_users }}</h2>
          <p>Last 7 Days: {{ stats.active_users_7d }}</p>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <h3>Total Posts</h3>
          <i class="fas fa-newspaper"></i>
        </div>
        <div class="card-body">
          <h2>{{ stats.total_posts }}</h2>
          <p>New Today: {{ stats.new_posts_today }}</p>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <h3>Comments</h3>
          <i class="fas fa-comments"></i>
        </div>
        <div class="card-body">
          <h2>{{ stats.total_comments }}</h2>
          <p>Per Post: {{ stats.avg_comments_per_post.toFixed(1) }}</p>
        </div>
      </div>
    </div>

    <!-- Charts -->
    <div class="dashboard-charts">
      <!-- User Activity Chart -->
      <div class="chart-card">
        <h3>User Activity</h3>
        <div ref="userActivityChart" class="chart"></div>
      </div>

      <!-- Content Metrics -->
      <div class="chart-card">
        <h3>Content Metrics</h3>
        <div class="metrics-grid">
          <div class="metric">
            <h4>Pending Moderation</h4>
            <p>{{ stats.pending_moderation }}</p>
          </div>
          <div class="metric">
            <h4>Reported Content</h4>
            <p>{{ stats.reported_content }}</p>
          </div>
          <div class="metric">
            <h4>Active Categories</h4>
            <p>{{ stats.active_categories }}</p>
          </div>
          <div class="metric">
            <h4>Storage Usage</h4>
            <p>{{ formatBytes(stats.storage_usage) }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Recent Activity -->
    <div class="dashboard-activity">
      <h3>Recent Activity</h3>
      <div class="activity-list">
        <div v-for="log in recentLogs" :key="log.id" class="activity-item">
          <div class="activity-content">
            <span class="activity-type" :class="log.type">
              {{ log.type }}
            </span>
            <div class="activity-details">
              <p>{{ log.message }}</p>
              <small>{{ formatDate(log.timestamp) }}</small>
            </div>
          </div>
          <div class="activity-actions">
            <button class="btn btn-link" @click="viewDetails(log)">
              <i class="fas fa-eye"></i>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useAdminStore } from '@/store/admin'
import * as echarts from 'echarts'

const adminStore = useAdminStore()
const userActivityChart = ref<HTMLDivElement>()

const stats = computed(() => adminStore.dashboardStats || {
  total_users: 0,
  active_users: 0,
  new_users_today: 0,
  active_users_7d: 0,
  total_posts: 0,
  active_posts: 0,
  new_posts_today: 0,
  total_comments: 0,
  new_comments_today: 0,
  avg_comments_per_post: 0,
  pending_moderation: 0,
  reported_content: 0,
  storage_usage: 0,
  bandwidth_usage: 0,
  active_categories: 0
})

const recentLogs = computed(() => adminStore.activityLogs.logs.slice(0, 10))

onMounted(async () => {
  await adminStore.fetchDashboardStats()
  await adminStore.fetchActivityLogs({ page: 1, page_size: 10 })
  initUserActivityChart()
})

const initUserActivityChart = () => {
  if (!userActivityChart.value) return

  const chart = echarts.init(userActivityChart.value)
  const option = {
    xAxis: {
      type: 'category',
      data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        data: [820, 932, 901, 934, 1290, 1330, 1320],
        type: 'line'
      }
    ]
  }
  chart.setOption(option)
}

const formatBytes = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const formatDate = (timestamp: string): string => {
  return new Date(timestamp).toLocaleString()
}

const viewDetails = (log: any) => {
  // Implement view details logic
}
</script>

<style scoped>
.dashboard {
  padding: 20px;
}

.dashboard-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 15px;
}

.card-header i {
  font-size: 24px;
  color: #6c757d;
}

.card-body h2 {
  font-size: 28px;
  margin: 0 0 10px 0;
  color: #333;
}

.card-body p {
  color: #6c757d;
  margin: 0;
}

.dashboard-charts {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.chart-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.chart {
  height: 300px;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.metric {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 4px;
  text-align: center;
}

.metric h4 {
  color: #6c757d;
  margin: 0 0 10px 0;
}

.metric p {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin: 0;
}

.dashboard-activity {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.dashboard-activity h3 {
  margin: 0 0 20px 0;
  color: #333;
}

.activity-list {
  max-height: 400px;
  overflow-y: auto;
}

.activity-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  border-bottom: 1px solid #eee;
}

.activity-content {
  flex: 1;
}

.activity-type {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  margin-right: 8px;
}

.activity-type.user {
  background: #cce5ff;
  color: #004085;
}

.activity-type.post {
  background: #d4edda;
  color: #155724;
}

.activity-type.comment {
  background: #fff3cd;
  color: #856404;
}

.activity-details p {
  margin: 0 0 5px 0;
  color: #333;
}

.activity-details small {
  color: #6c757d;
}

.activity-actions {
  display: flex;
  align-items: center;
}
</style>
