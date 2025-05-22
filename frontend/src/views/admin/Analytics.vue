<template>
  <div class="analytics-page">
    <!-- Analytics Header -->
    <div class="analytics-header">
      <h2>Analytics Dashboard</h2>
      <div class="header-actions">
        <div class="date-range">
          <button class="btn btn-link" @click="setDateRange('week')">
            <i class="fas fa-calendar-week"></i>
            <span>Week</span>
          </button>
          <button class="btn btn-link" @click="setDateRange('month')">
            <i class="fas fa-calendar-alt"></i>
            <span>Month</span>
          </button>
          <button class="btn btn-link" @click="setDateRange('year')">
            <i class="fas fa-calendar"></i>
            <span>Year</span>
          </button>
          <button class="btn btn-link" @click="setDateRange('custom')">
            <i class="fas fa-calendar-times"></i>
            <span>Custom</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Analytics Cards -->
    <div class="analytics-cards">
      <div class="card">
        <div class="card-header">
          <h3>User Growth</h3>
          <i class="fas fa-users"></i>
        </div>
        <div class="card-body">
          <div class="chart" ref="userGrowthChart"></div>
          <div class="stats">
            <p>Total Users: {{ stats.totalUsers }}</p>
            <p>New Users: {{ stats.newUsers }}</p>
            <p>Active Users: {{ stats.activeUsers }}</p>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <h3>Content Performance</h3>
          <i class="fas fa-chart-bar"></i>
        </div>
        <div class="card-body">
          <div class="chart" ref="contentPerformanceChart"></div>
          <div class="stats">
            <p>Total Posts: {{ stats.totalPosts }}</p>
            <p>Average Engagement: {{ stats.avgEngagement }}%</p>
            <p>Top Category: {{ stats.topCategory }}</p>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <h3>Engagement Metrics</h3>
          <i class="fas fa-heart"></i>
        </div>
        <div class="card-body">
          <div class="chart" ref="engagementChart"></div>
          <div class="stats">
            <p>Total Interactions: {{ stats.totalInteractions }}</p>
            <p>Average Comments: {{ stats.avgComments }} per post</p>
            <p>Average Likes: {{ stats.avgLikes }} per post</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Detailed Metrics -->
    <div class="metrics-grid">
      <div class="metric-card">
        <h3>Top Categories</h3>
        <div class="chart" ref="categoriesChart"></div>
      </div>
      <div class="metric-card">
        <h3>User Activity</h3>
        <div class="chart" ref="userActivityChart"></div>
      </div>
    </div>

    <!-- Custom Date Range Modal -->
    <div class="modal" v-if="showDateRangeModal">
      <div class="modal-content">
        <h3>Select Date Range</h3>
        <form @submit.prevent="applyCustomDateRange">
          <div class="form-group">
            <label>Start Date</label>
            <input type="date" v-model="customStartDate" required>
          </div>
          <div class="form-group">
            <label>End Date</label>
            <input type="date" v-model="customEndDate" required>
          </div>
          <div class="form-actions">
            <button type="button" class="btn btn-secondary" @click="closeDateRangeModal">
              Cancel
            </button>
            <button type="submit" class="btn btn-primary">
              Apply
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import * as echarts from 'echarts'
import { useAdminStore } from '@/store/admin'

const adminStore = useAdminStore()

const stats = computed(() => adminStore.analytics.stats)

// Date Range
const dateRange = ref('week')
const customStartDate = ref('')
const customEndDate = ref('')
const showDateRangeModal = ref(false)

const setDateRange = (range: string) => {
  dateRange.value = range
  if (range === 'custom') {
    showDateRangeModal.value = true
  } else {
    fetchAnalyticsData(range)
  }
}

const closeDateRangeModal = () => {
  showDateRangeModal.value = false
}

const applyCustomDateRange = async () => {
  try {
    await fetchAnalyticsData('custom', {
      start_date: customStartDate.value,
      end_date: customEndDate.value
    })
    showDateRangeModal.value = false
  } catch (error) {
    console.error('Error applying custom date range:', error)
  }
}

// Charts
const userGrowthChart = ref<HTMLDivElement>()
const contentPerformanceChart = ref<HTMLDivElement>()
const engagementChart = ref<HTMLDivElement>()
const categoriesChart = ref<HTMLDivElement>()
const userActivityChart = ref<HTMLDivElement>()

const initCharts = () => {
  if (!userGrowthChart.value) return

  // User Growth Chart
  const userGrowth = echarts.init(userGrowthChart.value)
  const userGrowthOption = {
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
  userGrowth.setOption(userGrowthOption)

  // Content Performance Chart
  const contentPerformance = echarts.init(contentPerformanceChart.value)
  const contentPerformanceOption = {
    xAxis: {
      type: 'category',
      data: ['Post 1', 'Post 2', 'Post 3', 'Post 4', 'Post 5']
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        data: [120, 200, 150, 80, 70],
        type: 'bar'
      }
    ]
  }
  contentPerformance.setOption(contentPerformanceOption)

  // Engagement Chart
  const engagement = echarts.init(engagementChart.value)
  const engagementOption = {
    series: [
      {
        type: 'pie',
        data: [
          { value: 335, name: 'Likes' },
          { value: 310, name: 'Comments' },
          { value: 234, name: 'Shares' }
        ]
      }
    ]
  }
  engagement.setOption(engagementOption)

  // Categories Chart
  const categories = echarts.init(categoriesChart.value)
  const categoriesOption = {
    xAxis: {
      type: 'category',
      data: ['Category 1', 'Category 2', 'Category 3', 'Category 4']
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        data: [120, 200, 150, 80],
        type: 'bar'
      }
    ]
  }
  categories.setOption(categoriesOption)

  // User Activity Chart
  const userActivity = echarts.init(userActivityChart.value)
  const userActivityOption = {
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
  userActivity.setOption(userActivityOption)
}

// Fetch Analytics Data
const fetchAnalyticsData = async (range: string, customDates?: { start_date: string; end_date: string }) => {
  try {
    await adminStore.getAnalytics({
      range,
      ...customDates
    })
    // Update charts with new data
    initCharts()
  } catch (error) {
    console.error('Error fetching analytics data:', error)
  }
}

onMounted(() => {
  fetchAnalyticsData('week')
})
</script>

<style scoped>
.analytics-page {
  padding: 20px;
}

.analytics-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.date-range {
  display: flex;
  gap: 10px;
}

.analytics-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
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
  margin-bottom: 20px;
}

.card-header i {
  font-size: 24px;
  color: #6c757d;
}

.card-body {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.chart {
  height: 300px;
}

.stats {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.stats p {
  margin: 0;
  color: #6c757d;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
}

.metric-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
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
  max-width: 400px;
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
