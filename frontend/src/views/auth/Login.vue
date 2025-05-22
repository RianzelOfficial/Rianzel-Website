<template>
  <div class="auth-container">
    <div class="auth-card">
      <!-- Success message after registration -->
      <div v-if="$route.query.registered" class="alert alert-success" role="alert">
        Registration successful! Please log in to continue.
      </div>
      
      <!-- Error message for general errors -->
      <div v-if="errors.general" class="alert alert-danger" role="alert">
        {{ errors.general }}
      </div>
      
      <h2 class="auth-title">Welcome Back</h2>
      <p class="text-muted text-center mb-4">Sign in to your account to continue</p>
      
      <form @submit.prevent="handleLogin">
        <!-- Username/Email Field -->
        <div class="form-group">
          <label for="identifier">Username or Email</label>
          <input
            type="text"
            class="form-control"
            id="identifier"
            v-model="loginData.identifier"
            :class="{ 'is-invalid': errors.identifier }"
            @input="clearError('identifier')"
            required
            autofocus
          />
          <div v-if="errors.identifier" class="invalid-feedback">
            {{ errors.identifier }}
          </div>
        </div>

        <!-- Password Field -->
        <div class="form-group">
          <div class="d-flex justify-content-between">
            <label for="password">Password</label>
            <router-link to="/auth/forgot-password" class="forgot-password">
              Forgot Password?
            </router-link>
          </div>
          <div class="input-group">
            <input
              :type="showPassword ? 'text' : 'password'"
              class="form-control"
              id="password"
              v-model="loginData.password"
              :class="{ 'is-invalid': errors.password }"
              @input="clearError('password')"
              required
            />
            <div class="input-group-append">
              <button 
                class="btn btn-outline-secondary" 
                type="button"
                @click="togglePasswordVisibility"
              >
                <i :class="showPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
              </button>
            </div>
          </div>
          <div v-if="errors.password" class="invalid-feedback d-block">
            {{ errors.password }}
          </div>
          
          <!-- Remaining Attempts Warning -->
          <div v-if="remainingAttempts > 0 && remainingAttempts <= 3" class="alert alert-warning mt-2 py-1 small">
            <i class="fas fa-exclamation-triangle mr-1"></i>
            {{ remainingAttempts }} attempt{{ remainingAttempts > 1 ? 's' : '' }} remaining before account is locked.
          </div>
          
          <!-- Account Locked Message -->
          <div v-if="accountLocked" class="alert alert-danger mt-2 py-1 small">
            <i class="fas fa-lock mr-1"></i>
            Account locked. Please try again in {{ lockoutTime }} minute{{ lockoutTime > 1 ? 's' : '' }} or 
            <router-link to="/auth/forgot-password">reset your password</router-link>.
          </div>
        </div>

        <!-- reCAPTCHA (shown after failed attempts) -->
        <div v-if="showRecaptcha" class="form-group">
          <div id="recaptcha" class="g-recaptcha" :data-sitekey="recaptchaSiteKey"></div>
          <div v-if="errors.recaptcha" class="invalid-feedback d-block">
            {{ errors.recaptcha }}
          </div>
        </div>

        <!-- Remember Me & 2FA Options -->
        <div class="form-group d-flex justify-content-between align-items-center">
          <div class="form-check">
            <input
              type="checkbox"
              class="form-check-input"
              id="remember"
              v-model="loginData.remember"
            />
            <label class="form-check-label" for="remember">
              Remember me
            </label>
          </div>
          
          <router-link v-if="!show2fa" to="/auth/register" class="btn btn-sm btn-link p-0">
            Enable 2FA
          </router-link>
        </div>

        <!-- Submit Button -->
        <div class="form-group">
          <button 
            type="submit" 
            class="btn btn-primary btn-block btn-lg"
            :disabled="isSubmitting || accountLocked"
          >
            <span v-if="isSubmitting" class="spinner-border spinner-border-sm mr-2" role="status" aria-hidden="true"></span>
            {{ isSubmitting ? 'Signing in...' : 'Sign In' }}
          </button>
        </div>

        <!-- Social Login Options -->
        <div class="divider my-4">
          <span class="divider-text">or continue with</span>
        </div>
        
        <div class="row">
          <div class="col-4">
            <button type="button" class="btn btn-outline-secondary btn-block" @click="socialLogin('google')">
              <i class="fab fa-google"></i>
            </button>
          </div>
          <div class="col-4">
            <button type="button" class="btn btn-outline-primary btn-block" @click="socialLogin('facebook')">
              <i class="fab fa-facebook-f"></i>
            </button>
          </div>
          <div class="col-4">
            <button type="button" class="btn btn-dark btn-block" @click="socialLogin('github')">
              <i class="fab fa-github"></i>
            </button>
          </div>
        </div>
      </form>
    </div>
    
    <div class="text-center mt-4">
      <p class="mb-0">
        Don't have an account? 
        <router-link to="/auth/register" class="font-weight-bold">Sign up</router-link>
      </p>
    </div>
    
    <!-- 2FA Verification Modal -->
    <div class="modal fade" :class="{ 'show d-block': show2fa }" tabindex="-1" role="dialog" v-if="show2fa">
      <div class="modal-dialog modal-dialog-centered" role="document">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Two-Factor Authentication</h5>
            <button type="button" class="close" @click="cancel2fa" aria-label="Close">
              <span aria-hidden="true">&times;</span>
            </button>
          </div>
          <div class="modal-body">
            <p>Please enter the 6-digit verification code from your authenticator app.</p>
            
            <div class="form-group">
              <label for="otp">Verification Code</label>
              <div class="d-flex justify-content-between">
                <input
                  v-for="i in 6"
                  :key="i"
                  type="text"
                  maxlength="1"
                  class="form-control text-center mx-1 otp-input"
                  v-model="otp[i-1]"
                  @keyup="handleOtpInput($event, i-1)"
                  @keydown.delete="handleOtpDelete($event, i-1)"
                  @paste="handleOtpPaste($event)"
                  :ref="'otp' + (i-1)"
                  :disabled="isVerifying"
                />
              </div>
              <div v-if="otpError" class="invalid-feedback d-block">
                {{ otpError }}
              </div>
              <div class="text-center mt-3">
                <button 
                  type="button" 
                  class="btn btn-link p-0"
                  @click="resend2faCode"
                  :disabled="resendCooldown > 0"
                >
                  Didn't receive a code? {{ resendCooldown > 0 ? `(${resendCooldown}s)` : 'Resend' }}
                </button>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="cancel2fa" :disabled="isVerifying">
              Cancel
            </button>
            <button 
              type="button" 
              class="btn btn-primary" 
              @click="verify2fa" 
              :disabled="otp.join('').length !== 6 || isVerifying"
            >
              <span v-if="isVerifying" class="spinner-border spinner-border-sm mr-2" role="status" aria-hidden="true"></span>
              {{ isVerifying ? 'Verifying...' : 'Verify' }}
            </button>
          </div>
        </div>
      </div>
    </div>
    <div v-if="show2fa" class="modal-backdrop fade show"></div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useAuth } from '../../services/security'
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'

export default {
  name: 'Login',
  setup() {
    const auth = useAuth()
    const router = useRouter()
    const route = useRoute()
    
    // Form data
    const loginData = ref({
      identifier: '',
      password: '',
      remember: false,
      otp: ''
    })
    
    // UI state
    const showPassword = ref(false)
    const isSubmitting = ref(false)
    const show2fa = ref(false)
    const otp = ref(Array(6).fill(''))
    const otpError = ref('')
    const isVerifying = ref(false)
    const resendCooldown = ref(0)
    let resendTimer = null
    
    // Security state
    const failedAttempts = ref(0)
    const accountLocked = ref(false)
    const lockoutTime = ref(0)
    const showRecaptcha = ref(false)
    const recaptchaToken = ref('')
    const recaptchaSiteKey = import.meta.env.VITE_RECAPTCHA_SITE_KEY || 'your-recaptcha-site-key'
    
    // Form errors
    const errors = ref({})
    
    // Computed properties
    const remainingAttempts = computed(() => {
      const maxAttempts = 5 // Should match your backend setting
      return Math.max(0, maxAttempts - failedAttempts.value)
    })
    
    // Clear error when user starts typing
    const clearError = (field) => {
      if (errors.value[field]) {
        errors.value[field] = ''
      }
    }
    
    // Toggle password visibility
    const togglePasswordVisibility = () => {
      showPassword.value = !showPassword.value
    }
    
    // Handle OTP input
    const handleOtpInput = (event, index) => {
      // Only allow numbers
      const value = event.target.value.replace(/\D/g, '')
      
      if (value) {
        otp.value[index] = value.slice(-1) // Only take the last character
        
        // Auto-focus next input
        if (index < 5) {
          nextTick(() => {
            const nextInput = document.getElementById(`otp-${index + 1}`)
            if (nextInput) nextInput.focus()
          })
        }
      } else {
        otp.value[index] = ''
      }
      
      otpError.value = ''
    }
    
    // Handle OTP delete
    const handleOtpDelete = (event, index) => {
      if (event.key === 'Backspace' && !otp.value[index] && index > 0) {
        // Move to previous input on backspace if current is empty
        nextTick(() => {
          const prevInput = document.getElementById(`otp-${index - 1}`)
          if (prevInput) prevInput.focus()
        })
      }
    }
    
    // Handle OTP paste
    const handleOtpPaste = (event) => {
      event.preventDefault()
      const pasteData = (event.clipboardData || window.clipboardData).getData('text')
      const numbers = pasteData.replace(/\D/g, '').split('').slice(0, 6)
      
      numbers.forEach((num, i) => {
        if (i < 6) otp.value[i] = num
      })
      
      // Focus the last input with a value
      const lastFilledIndex = otp.value.findIndex(val => !val) - 1
      if (lastFilledIndex >= 0 && lastFilledIndex < 5) {
        nextTick(() => {
          const nextInput = document.getElementById(`otp-${lastFilledIndex + 1}`)
          if (nextInput) nextInput.focus()
        })
      }
    }
    
    // Resend 2FA code
    const resend2faCode = async () => {
      try {
        await auth.resend2faCode(loginData.value.identifier)
        startResendCooldown()
      } catch (error) {
        otpError.value = 'Failed to resend verification code. Please try again.'
        console.error('Resend 2FA code error:', error)
      }
    }
    
    // Start resend cooldown timer
    const startResendCooldown = () => {
      resendCooldown.value = 30
      
      resendTimer = setInterval(() => {
        resendCooldown.value--
        
        if (resendCooldown.value <= 0) {
          clearInterval(resendTimer)
        }
      }, 1000)
    }
    
    // Cancel 2FA verification
    const cancel2fa = () => {
      show2fa.value = false
      otp.value = Array(6).fill('')
      otpError.value = ''
      isVerifying.value = false
    }
    
    // Verify 2FA code
    const verify2fa = async () => {
      const otpCode = otp.value.join('')
      
      if (otpCode.length !== 6) {
        otpError.value = 'Please enter a valid 6-digit code'
        return
      }
      
      isVerifying.value = true
      otpError.value = ''
      
      try {
        await auth.verify2fa({
          identifier: loginData.value.identifier,
          otp: otpCode,
          remember: loginData.value.remember
        })
        
        // Redirect to intended URL or home
        const redirectTo = route.query.redirect || '/dashboard'
        router.push(redirectTo)
      } catch (error) {
        otpError.value = 'Invalid or expired verification code. Please try again.'
        console.error('2FA verification error:', error)
      } finally {
        isVerifying.value = false
      }
    }
    
    // Handle social login
    const socialLogin = async (provider) => {
      try {
        // This URL should be handled by your backend's OAuth endpoints
        window.location.href = `${import.meta.env.VITE_API_BASE_URL}/auth/${provider}/login?redirect=${encodeURIComponent(route.query.redirect || '/')}`
      } catch (error) {
        console.error('Social login error:', error)
        errors.value.general = `Failed to initiate ${provider} login. Please try again.`
      }
    }
    
    // Load reCAPTCHA script
    const loadRecaptcha = () => {
      if (document.getElementById('recaptcha-script') || !showRecaptcha.value) return
      
      const script = document.createElement('script')
      script.id = 'recaptcha-script'
      script.src = `https://www.google.com/recaptcha/api.js?render=${recaptchaSiteKey}`
      script.async = true
      script.defer = true
      document.head.appendChild(script)
      
      return new Promise((resolve) => {
        script.onload = () => {
          // Wait for grecaptcha to be available
          const checkGrecaptcha = setInterval(() => {
            if (window.grecaptcha) {
              clearInterval(checkGrecaptcha)
              window.grecaptcha.ready(() => {
                resolve()
              })
            }
          }, 100)
        }
      })
    }
    
    // Handle login form submission
    const handleLogin = async () => {
      // Reset errors
      errors.value = {}
      
      // Basic validation
      if (!loginData.value.identifier) {
        errors.value.identifier = 'Username or email is required'
        return
      }
      
      if (!loginData.value.password) {
        errors.value.password = 'Password is required'
        return
      }
      
      // Validate reCAPTCHA if shown
      if (showRecaptcha.value) {
        try {
          const token = await executeRecaptcha()
          recaptchaToken.value = token
        } catch (error) {
          console.error('reCAPTCHA error:', error)
          errors.value.recaptcha = 'Please complete the reCAPTCHA verification'
          return
        }
      }
      
      isSubmitting.value = true
      
      try {
        // Attempt to log in
        const response = await auth.login({
          identifier: loginData.value.identifier,
          password: loginData.value.password,
          remember: loginData.value.remember,
          recaptcha_token: recaptchaToken.value
        })
        
        // If 2FA is required, show the 2FA modal
        if (response.requires_2fa) {
          show2fa.value = true
          startResendCooldown()
          return
        }
        
        // Otherwise, redirect to dashboard or intended URL
        const redirectTo = route.query.redirect || '/dashboard'
        router.push(redirectTo)
        
      } catch (error) {
        console.error('Login error:', error)
        
        if (error.response) {
          const { status, data } = error.response
          
          switch (status) {
            case 400:
            case 422:
              // Handle validation errors
              if (data.detail) {
                if (Array.isArray(data.detail)) {
                  data.detail.forEach(err => {
                    const field = err.loc[err.loc.length - 1]
                    errors.value[field] = err.msg
                  })
                } else if (typeof data.detail === 'string') {
                  errors.value.general = data.detail
                }
              } else {
                errors.value.general = data.message || 'Invalid credentials'
              }
              break
              
            case 401:
              errors.value.general = 'Invalid username or password'
              failedAttempts.value++
              
              // Show reCAPTCHA after 3 failed attempts
              if (failedAttempts.value >= 3) {
                showRecaptcha.value = true
                loadRecaptcha()
              }
              break
              
            case 403:
              // Account locked
              accountLocked.value = true
              lockoutTime.value = data.retry_after || 15 // Default to 15 minutes if not provided
              errors.value.general = 'Account locked. Please try again later.'
              break
              
            case 429:
              // Rate limited
              errors.value.general = 'Too many login attempts. Please try again later.'
              break
              
            default:
              errors.value.general = 'An unexpected error occurred. Please try again.'
          }
        } else {
          errors.value.general = 'Network error. Please check your connection and try again.'
        }
      } finally {
        isSubmitting.value = false
      }
    }
    
    // Execute reCAPTCHA
    const executeRecaptcha = () => {
      return new Promise((resolve, reject) => {
        if (!window.grecaptcha) {
          reject(new Error('reCAPTCHA not loaded'))
          return
        }
        
        window.grecaptcha.ready(async () => {
          try {
            const token = await window.grecaptcha.execute(recaptchaSiteKey, { action: 'login' })
            resolve(token)
          } catch (error) {
            reject(error)
          }
        })
      })
    }
    
    // Initialize component
    onMounted(() => {
      // Check for redirect messages
      if (route.query.error) {
        errors.value.general = route.query.error
      }
      
      // Check for password reset success
      if (route.query.reset === 'success') {
        errors.value.general = 'Your password has been reset. You can now log in with your new password.'
      }
      
      // Check for account verification
      if (route.query.verified === 'true') {
        errors.value.general = 'Your email has been verified. You can now log in.'
      }
    })
    
    // Clean up
    onUnmounted(() => {
      if (resendTimer) {
        clearInterval(resendTimer)
      }
    })
    
    return {
      // Data
      loginData,
      errors,
      showPassword,
      isSubmitting,
      show2fa,
      otp,
      otpError,
      isVerifying,
      resendCooldown,
      accountLocked,
      lockoutTime,
      remainingAttempts,
      showRecaptcha,
      recaptchaSiteKey,
      
      // Methods
      clearError,
      togglePasswordVisibility,
      handleOtpInput,
      handleOtpDelete,
      handleOtpPaste,
      resend2faCode,
      cancel2fa,
      verify2fa,
      socialLogin,
      handleLogin
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

.input-group-append .btn {
  border-top-left-radius: 0;
  border-bottom-left-radius: 0;
  border-left: none;
  background: #f8f9fa;
  border-color: #e1e5eb;
  color: #6c757d;
  transition: all 0.2s;
}

.input-group-append .btn:hover {
  background: #e9ecef;
  border-color: #dee2e6;
  color: #495057;
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

.forgot-password {
  color: #6c757d;
  font-size: 0.85rem;
  text-decoration: none;
  transition: color 0.2s;
}

.forgot-password:hover {
  color: #4a6cf7;
  text-decoration: none;
}

.divider {
  display: flex;
  align-items: center;
  text-align: center;
  color: #6c757d;
  font-size: 0.9rem;
  margin: 1.5rem 0;
}

.divider::before,
.divider::after {
  content: '';
  flex: 1;
  border-bottom: 1px solid #e1e5eb;
}

.divider:not(:empty)::before {
  margin-right: 1em;
}

.divider:not(:empty)::after {
  margin-left: 1em;
}

.social-login-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 48px;
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.3s;
  margin-bottom: 0.75rem;
}

.social-login-btn i {
  font-size: 1.2rem;
  margin-right: 8px;
}

.btn-google {
  background: #fff;
  color: #757575;
  border: 1px solid #e1e5eb;
}

.btn-google:hover {
  background: #f8f9fa;
  transform: translateY(-1px);
}

.btn-facebook {
  background: #1877f2;
  color: white;
  border: none;
}

.btn-facebook:hover {
  background: #166fe5;
  transform: translateY(-1px);
}

.btn-github {
  background: #333;
  color: white;
  border: none;
}

.btn-github:hover {
  background: #2b2b2b;
  transform: translateY(-1px);
}

/* 2FA Modal */
.modal-content {
  border: none;
  border-radius: 12px;
  overflow: hidden;
}

.modal-header {
  border-bottom: 1px solid #e9ecef;
  padding: 1.5rem;
}

.modal-title {
  font-weight: 600;
  color: #2c3e50;
  margin: 0;
}

.modal-body {
  padding: 1.5rem;
}

.modal-footer {
  border-top: 1px solid #e9ecef;
  padding: 1rem 1.5rem;
  justify-content: space-between;
}

.otp-input {
  height: 60px;
  width: 45px;
  text-align: center;
  font-size: 1.5rem;
  font-weight: 600;
  padding: 0;
  margin: 0 2px;
}

.otp-input:focus {
  border-color: #4a6cf7;
  box-shadow: 0 0 0 0.2rem rgba(74, 108, 247, 0.25);
}

/* Responsive adjustments */
@media (max-width: 576px) {
  .auth-card {
    padding: 1.5rem;
    margin: 1rem;
  }
  
  .auth-title {
    font-size: 1.5rem;
  }
  
  .otp-input {
    width: 40px;
    height: 50px;
    font-size: 1.25rem;
  }
}

/* Animations */
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

/* Custom checkbox */
.form-check-input:checked {
  background-color: #4a6cf7;
  border-color: #4a6cf7;
}

.form-check-input:focus {
  border-color: #4a6cf7;
  box-shadow: 0 0 0 0.2rem rgba(74, 108, 247, 0.25);
}

/* Error states */
.is-invalid {
  border-color: #dc3545 !important;
  padding-right: calc(1.5em + 0.75rem);
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 12 12' width='12' height='12' fill='none' stroke='%23dc3545'%3e%3ccircle cx='6' cy='6' r='4.5'/%3e%3cpath stroke-linejoin='round' d='M5.8 3.6h.4L6 6.5z'/%3e%3ccircle cx='6' cy='8.2' r='.6' fill='%23dc3545' stroke='none'/%3e%3c/svg%3e");
  background-repeat: no-repeat;
  background-position: right calc(0.375em + 0.1875rem) center;
  background-size: calc(0.75em + 0.375rem) calc(0.75em + 0.375rem);
}

.invalid-feedback {
  display: block;
  width: 100%;
  margin-top: 0.25rem;
  font-size: 0.875em;
  color: #dc3545;
}

/* reCAPTCHA container */
.g-recaptcha {
  display: flex;
  justify-content: center;
  margin: 1rem 0;
}

/* Loading spinner */
.spinner-border {
  width: 1.25rem;
  height: 1.25rem;
  border-width: 0.2em;
}
</style>

<style scoped>
.auth-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #ff6b6b, #4ecdc4);
}

.auth-card {
  background: white;
  padding: 2rem;
  border-radius: 10px;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
}

.auth-title {
  text-align: center;
  margin-bottom: 2rem;
  color: #333;
}

.form-group {
  margin-bottom: 1rem;
}

.form-control {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.btn {
  padding: 0.5rem;
  border-radius: 4px;
}

.btn-primary {
  background-color: #4ecdc4;
  border-color: #4ecdc4;
}

.btn-primary:hover {
  background-color: #3ba090;
  border-color: #3ba090;
}

.btn-link {
  color: #4ecdc4;
  text-decoration: none;
}

.btn-link:hover {
  color: #3ba090;
  text-decoration: underline;
}

.form-check-label {
  margin-left: 0.5rem;
}

@media (max-width: 768px) {
  .auth-container {
    padding: 1rem;
  }
}
</style>
