<template>
  <div class="auth-container">
    <div class="auth-card">
      <h2 class="auth-title">Forgot Password</h2>
      <p class="mb-4 text-muted">Enter your email address and we will send you a link to reset your password.</p>
      <form @submit.prevent="handleForgotPassword">
        <div class="form-group">
          <label for="email">Email Address</label>
          <input
            type="email"
            class="form-control"
            id="email"
            v-model="email"
            required
            :class="{ 'is-invalid': error }"
          />
          <div v-if="error" class="invalid-feedback">{{ error }}</div>
        </div>
        <div class="form-group">
          <button type="submit" class="btn btn-primary btn-block" :disabled="isSubmitting">
            <span v-if="isSubmitting" class="spinner-border spinner-border-sm mr-2" role="status" aria-hidden="true"></span>
            {{ isSubmitting ? 'Sending...' : 'Send Reset Link' }}
          </button>
        </div>
        <div v-if="success" class="alert alert-success mt-3" role="alert">
          {{ success }}
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

export default {
  name: 'ForgotPassword',
  setup() {
    const email = ref('')
    const error = ref('')
    const success = ref('')
    const isSubmitting = ref(false)

    const handleForgotPassword = async () => {
      error.value = ''
      success.value = ''
      if (!email.value) {
        error.value = 'Email is required'
        return
      }
      isSubmitting.value = true
      try {
        // Replace with your backend endpoint
        await axios.post(`${import.meta.env.VITE_API_BASE_URL}/auth/forgot-password`, { email: email.value })
        success.value = 'If your email is registered, you will receive a password reset link shortly.'
      } catch (err) {
        error.value = 'Something went wrong. Please try again.'
      } finally {
        isSubmitting.value = false
      }
    }

    return {
      email,
      error,
      success,
      isSubmitting,
      handleForgotPassword
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
