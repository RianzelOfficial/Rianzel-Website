<template>
  <div class="auth-container">
    <div class="auth-card">
      <h2 class="auth-title">Reset Password</h2>
      <form @submit.prevent="handleResetPassword">
        <div class="form-group">
          <label for="newPassword">New Password</label>
          <input
            type="password"
            class="form-control"
            id="newPassword"
            v-model="newPassword"
            required
            :class="{ 'is-invalid': errors.newPassword }"
          />
          <div v-if="errors.newPassword" class="invalid-feedback">{{ errors.newPassword }}</div>
        </div>
        <div class="form-group">
          <label for="confirmPassword">Confirm Password</label>
          <input
            type="password"
            class="form-control"
            id="confirmPassword"
            v-model="confirmPassword"
            required
            :class="{ 'is-invalid': errors.confirmPassword }"
          />
          <div v-if="errors.confirmPassword" class="invalid-feedback">{{ errors.confirmPassword }}</div>
        </div>
        <div class="form-group">
          <button type="submit" class="btn btn-primary btn-block" :disabled="isSubmitting">
            <span v-if="isSubmitting" class="spinner-border spinner-border-sm mr-2" role="status" aria-hidden="true"></span>
            {{ isSubmitting ? 'Resetting...' : 'Reset Password' }}
          </button>
        </div>
        <div v-if="success" class="alert alert-success mt-3" role="alert">
          {{ success }}
        </div>
        <div v-if="error" class="alert alert-danger mt-3" role="alert">
          {{ error }}
        </div>
      </form>
      <div class="text-center mt-3">
        <router-link to="/auth/login">Back to Login</router-link>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import axios from 'axios'
import { useRoute, useRouter } from 'vue-router'

export default {
  name: 'ResetPassword',
  setup() {
    const route = useRoute()
    const router = useRouter()
    const newPassword = ref('')
    const confirmPassword = ref('')
    const isSubmitting = ref(false)
    const success = ref('')
    const error = ref('')
    const errors = ref({})

    const validate = () => {
      errors.value = {}
      let valid = true
      if (!newPassword.value) {
        errors.value.newPassword = 'New password is required'
        valid = false
      } else if (newPassword.value.length < 8) {
        errors.value.newPassword = 'Password must be at least 8 characters.'
        valid = false
      }
      if (!confirmPassword.value) {
        errors.value.confirmPassword = 'Please confirm your password.'
        valid = false
      } else if (confirmPassword.value !== newPassword.value) {
        errors.value.confirmPassword = 'Passwords do not match.'
        valid = false
      }
      return valid
    }

    const handleResetPassword = async () => {
      if (!validate()) return
      isSubmitting.value = true
      error.value = ''
      success.value = ''
      try {
        const reset_token = route.query.token
        await axios.post(`${import.meta.env.VITE_API_BASE_URL}/auth/reset-password`, {
          reset_token,
          new_password: newPassword.value
        })
        success.value = 'Password reset successful! You can now log in.'
        setTimeout(() => router.push('/auth/login'), 2000)
      } catch (err) {
        error.value = err.response?.data?.detail || 'Something went wrong. Try again.'
      } finally {
        isSubmitting.value = false
      }
    }

    return {
      newPassword,
      confirmPassword,
      isSubmitting,
      success,
      error,
      errors,
      handleResetPassword
    }
  }
}
</script>

<style scoped>
.auth-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 2rem 1rem;
}
.auth-card {
  width: 100%;
  max-width: 420px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  padding: 2.5rem;
  animation: fadeIn 0.3s ease-in-out;
}
.auth-title {
  color: #2c3e50;
  font-weight: 700;
  text-align: center;
  margin-bottom: 1.5rem;
  font-size: 1.8rem;
}
.form-group {
  margin-bottom: 1.5rem;
}
.form-control {
  height: 48px;
  border-radius: 8px;
  border: 1px solid #e1e5eb;
  transition: all 0.3s ease;
  padding: 0.5rem 1rem;
  font-size: 0.95rem;
}
.form-control:focus {
  border-color: #4a6cf7;
  box-shadow: 0 0 0 0.2rem rgba(74, 108, 247, 0.25);
}
.btn-primary {
  background-color: #4a6cf7;
  border: none;
  font-weight: 600;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  transition: all 0.3s;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.btn-primary:hover {
  background-color: #3a5bd9;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(74, 108, 247, 0.25);
}
.btn-primary:disabled {
  background-color: #6c757d;
  transform: none;
  box-shadow: none;
  cursor: not-allowed;
  opacity: 0.8;
}
.invalid-feedback {
  display: block;
  width: 100%;
  margin-top: 0.25rem;
  font-size: 0.875em;
  color: #dc3545;
}
.alert-success {
  margin-top: 1rem;
}
.alert-danger {
  margin-top: 1rem;
}
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
