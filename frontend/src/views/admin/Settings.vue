<template>
  <div class="settings-page">
    <!-- Settings Tabs -->
    <div class="settings-tabs">
      <button 
        v-for="tab in tabs" 
        :key="tab.id" 
        :class="['tab-btn', { active: activeTab === tab.id }]"
        @click="activeTab = tab.id"
      >
        <i :class="tab.icon"></i>
        <span>{{ tab.title }}</span>
      </button>
    </div>

    <!-- Site Settings -->
    <div class="settings-section" v-if="activeTab === 'site-settings'">
      <h3>Site Settings</h3>
      <form @submit.prevent="saveSiteSettings">
        <div class="form-group">
          <label>Site Title</label>
          <input type="text" v-model="siteSettings.title" required>
        </div>
        <div class="form-group">
          <label>Site Description</label>
          <textarea v-model="siteSettings.description" required></textarea>
        </div>
        <div class="form-group">
          <label>Site Logo</label>
          <div class="logo-preview" v-if="siteSettings.logo">
            <img :src="siteSettings.logo" alt="Site Logo">
          </div>
          <input type="file" @change="handleLogoUpload">
        </div>
        <div class="form-group">
          <label>Site Theme</label>
          <select v-model="siteSettings.theme">
            <option value="light">Light</option>
            <option value="dark">Dark</option>
            <option value="auto">Auto</option>
          </select>
        </div>
        <div class="form-group">
          <label>Maintenance Mode</label>
          <div class="switch">
            <input type="checkbox" v-model="siteSettings.maintenance_mode">
            <span class="slider"></span>
          </div>
        </div>
        <div class="form-actions">
          <button type="submit" class="btn btn-primary">
            <i class="fas fa-save"></i>
            <span>Save Settings</span>
          </button>
        </div>
      </form>
    </div>

    <!-- Security Settings -->
    <div class="settings-section" v-if="activeTab === 'security-settings'">
      <h3>Security Settings</h3>
      <form @submit.prevent="saveSecuritySettings">
        <div class="form-group">
          <label>Require Two-Factor Auth</label>
          <div class="switch">
            <input type="checkbox" v-model="securitySettings.require_2fa">
            <span class="slider"></span>
          </div>
        </div>
        <div class="form-group">
          <label>Password Policy</label>
          <div class="password-policy">
            <div class="policy-item">
              <input type="checkbox" v-model="securitySettings.require_uppercase">
              <span>Require uppercase letters</span>
            </div>
            <div class="policy-item">
              <input type="checkbox" v-model="securitySettings.require_lowercase">
              <span>Require lowercase letters</span>
            </div>
            <div class="policy-item">
              <input type="checkbox" v-model="securitySettings.require_numbers">
              <span>Require numbers</span>
            </div>
            <div class="policy-item">
              <input type="checkbox" v-model="securitySettings.require_special_chars">
              <span>Require special characters</span>
            </div>
            <div class="policy-item">
              <label>
                <input type="number" v-model="securitySettings.min_length">
                <span>Minimum length</span>
              </label>
            </div>
          </div>
        </div>
        <div class="form-group">
          <label>Session Timeout (minutes)</label>
          <input type="number" v-model="securitySettings.session_timeout" required>
        </div>
        <div class="form-actions">
          <button type="submit" class="btn btn-primary">
            <i class="fas fa-save"></i>
            <span>Save Settings</span>
          </button>
        </div>
      </form>
    </div>

    <!-- Email Settings -->
    <div class="settings-section" v-if="activeTab === 'email-settings'">
      <h3>Email Settings</h3>
      <form @submit.prevent="saveEmailSettings">
        <div class="form-group">
          <label>SMTP Host</label>
          <input type="text" v-model="emailSettings.smtp_host" required>
        </div>
        <div class="form-group">
          <label>SMTP Port</label>
          <input type="number" v-model="emailSettings.smtp_port" required>
        </div>
        <div class="form-group">
          <label>SMTP Username</label>
          <input type="text" v-model="emailSettings.smtp_username" required>
        </div>
        <div class="form-group">
          <label>SMTP Password</label>
          <input type="password" v-model="emailSettings.smtp_password">
        </div>
        <div class="form-group">
          <label>From Email</label>
          <input type="email" v-model="emailSettings.from_email" required>
        </div>
        <div class="form-group">
          <label>Test Email</label>
          <input type="email" v-model="testEmail">
          <button class="btn btn-secondary" @click="testEmailSettings">
            <i class="fas fa-envelope"></i>
            <span>Send Test Email</span>
          </button>
        </div>
        <div class="form-actions">
          <button type="submit" class="btn btn-primary">
            <i class="fas fa-save"></i>
            <span>Save Settings</span>
          </button>
        </div>
      </form>
    </div>

    <!-- Backup Settings -->
    <div class="settings-section" v-if="activeTab === 'backup-settings'">
      <h3>Backup Settings</h3>
      <div class="backup-grid">
        <div class="backup-card">
          <h4>Database Backup</h4>
          <div class="backup-info">
            <p>Last Backup: {{ formatDate(lastDatabaseBackup) }}</p>
            <p>Size: {{ formatSize(databaseBackupSize) }}</p>
            <p>Status: <span class="status-tag" :class="databaseBackupStatus">{{ databaseBackupStatus }}</span></p>
          </div>
          <button class="btn btn-primary" @click="createDatabaseBackup">
            <i class="fas fa-database"></i>
            <span>Create Backup</span>
          </button>
        </div>
        <div class="backup-card">
          <h4>File Backup</h4>
          <div class="backup-info">
            <p>Last Backup: {{ formatDate(lastFileBackup) }}</p>
            <p>Size: {{ formatSize(fileBackupSize) }}</p>
            <p>Status: <span class="status-tag" :class="fileBackupStatus">{{ fileBackupStatus }}</span></p>
          </div>
          <button class="btn btn-primary" @click="createFileBackup">
            <i class="fas fa-file-archive"></i>
            <span>Create Backup</span>
          </button>
        </div>
      </div>
      <div class="backup-actions">
        <button class="btn btn-secondary" @click="downloadBackup">
          <i class="fas fa-download"></i>
          <span>Download Backup</span>
        </button>
        <button class="btn btn-danger" @click="restoreBackup">
          <i class="fas fa-undo"></i>
          <span>Restore Backup</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAdminStore } from '@/store/admin'

const adminStore = useAdminStore()

// Tabs
const tabs = [
  { id: 'site-settings', title: 'Site Settings', icon: 'fas fa-cog' },
  { id: 'security-settings', title: 'Security Settings', icon: 'fas fa-shield-alt' },
  { id: 'email-settings', title: 'Email Settings', icon: 'fas fa-envelope' },
  { id: 'backup-settings', title: 'Backup Settings', icon: 'fas fa-save' }
]

const activeTab = ref('site-settings')

// Site Settings
const siteSettings = ref({
  title: '',
  description: '',
  logo: null,
  theme: 'light',
  maintenance_mode: false
})

const handleLogoUpload = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files[0]) {
    const file = target.files[0]
    const reader = new FileReader()
    reader.onload = (e) => {
      siteSettings.value.logo = e.target?.result as string
    }
    reader.readAsDataURL(file)
  }
}

const saveSiteSettings = async () => {
  try {
    await adminStore.saveSiteSettings(siteSettings.value)
  } catch (error) {
    console.error('Error saving site settings:', error)
  }
}

// Security Settings
const securitySettings = ref({
  require_2fa: false,
  require_uppercase: true,
  require_lowercase: true,
  require_numbers: true,
  require_special_chars: true,
  min_length: 8,
  session_timeout: 30
})

const saveSecuritySettings = async () => {
  try {
    await adminStore.saveSecuritySettings(securitySettings.value)
  } catch (error) {
    console.error('Error saving security settings:', error)
  }
}

// Email Settings
const emailSettings = ref({
  smtp_host: '',
  smtp_port: 587,
  smtp_username: '',
  smtp_password: '',
  from_email: ''
})

const testEmail = ref('')

const testEmailSettings = async () => {
  try {
    await adminStore.testEmailSettings(testEmail.value)
  } catch (error) {
    console.error('Error testing email settings:', error)
  }
}

const saveEmailSettings = async () => {
  try {
    await adminStore.saveEmailSettings(emailSettings.value)
  } catch (error) {
    console.error('Error saving email settings:', error)
  }
}

// Backup Settings
const lastDatabaseBackup = ref('')
const databaseBackupSize = ref(0)
const databaseBackupStatus = ref('idle')
const lastFileBackup = ref('')
const fileBackupSize = ref(0)
const fileBackupStatus = ref('idle')

const createDatabaseBackup = async () => {
  try {
    databaseBackupStatus.value = 'processing'
    await adminStore.createDatabaseBackup()
    databaseBackupStatus.value = 'success'
  } catch (error) {
    databaseBackupStatus.value = 'error'
    console.error('Error creating database backup:', error)
  }
}

const createFileBackup = async () => {
  try {
    fileBackupStatus.value = 'processing'
    await adminStore.createFileBackup()
    fileBackupStatus.value = 'success'
  } catch (error) {
    fileBackupStatus.value = 'error'
    console.error('Error creating file backup:', error)
  }
}

const downloadBackup = async () => {
  try {
    const backup = await adminStore.downloadBackup()
    const blob = new Blob([backup], { type: 'application/zip' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `backup-${new Date().toISOString()}.zip`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
  } catch (error) {
    console.error('Error downloading backup:', error)
  }
}

const restoreBackup = async () => {
  if (!confirm('Are you sure you want to restore from backup? This will overwrite existing data.')) return
  try {
    await adminStore.restoreBackup()
  } catch (error) {
    console.error('Error restoring backup:', error)
  }
}

// Helper Functions
const formatDate = (dateString: string): string => {
  return new Date(dateString).toLocaleString()
}

const formatSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

onMounted(async () => {
  try {
    await adminStore.loadSettings()
    siteSettings.value = { ...adminStore.settings.site }
    securitySettings.value = { ...adminStore.settings.security }
    emailSettings.value = { ...adminStore.settings.email }
    
    // Load backup status
    const backupStatus = await adminStore.getBackupStatus()
    lastDatabaseBackup.value = backupStatus.last_database_backup
    databaseBackupSize.value = backupStatus.database_size
    lastFileBackup.value = backupStatus.last_file_backup
    fileBackupSize.value = backupStatus.file_size
  } catch (error) {
    console.error('Error loading settings:', error)
  }
})
</script>

<style scoped>
.settings-page {
  padding: 20px;
}

.settings-tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border: none;
  background: none;
  cursor: pointer;
  color: #6c757d;
  border-radius: 4px 4px 0 0;
}

.tab-btn.active {
  color: #007bff;
  background: white;
  border-bottom: 2px solid #007bff;
}

.tab-btn i {
  font-size: 16px;
}

.settings-section {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 15px;
}

.logo-preview {
  margin-bottom: 10px;
}

.logo-preview img {
  max-width: 200px;
  height: auto;
}

.switch {
  position: relative;
  display: inline-block;
  width: 60px;
  height: 34px;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #ccc;
  transition: .4s;
  border-radius: 34px;
}

.slider:before {
  position: absolute;
  content: "";
  height: 26px;
  width: 26px;
  left: 4px;
  bottom: 4px;
  background-color: white;
  transition: .4s;
  border-radius: 50%;
}

input:checked + .slider {
  background-color: #2196F3;
}

input:checked + .slider:before {
  transform: translateX(26px);
}

.password-policy {
  display: grid;
  gap: 10px;
}

.policy-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.backup-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.backup-card {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.backup-info {
  margin-bottom: 15px;
}

.status-tag {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.status-tag.idle {
  background: #e9ecef;
  color: #495057;
}

.status-tag.processing {
  background: #fff3cd;
  color: #856404;
}

.status-tag.success {
  background: #d4edda;
  color: #155724;
}

.status-tag.error {
  background: #f8d7da;
  color: #721c24;
}

.backup-actions {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}
</style>
