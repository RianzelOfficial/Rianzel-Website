<template>
  <div class="auth-container">
    <div class="auth-card">
      <h2 class="auth-title">Create Your Account</h2>

      <form @submit.prevent="handleRegister">
        <!-- Full Name -->
        <div class="form-group">
          <label for="full_name">Full Name</label>
          <input
            type="text"
            id="full_name"
            class="form-control"
            v-model="registerData.full_name"
            :class="{ 'is-invalid': errors.full_name }"
            required
            @input="clearError('full_name')"
          />
          <div v-if="errors.full_name" class="invalid-feedback">{{ errors.full_name }}</div>
        </div>

        <!-- Username -->
        <div class="form-group">
          <label for="username">Username</label>
          <input
            type="text"
            id="username"
            class="form-control"
            v-model="registerData.username"
            :class="{ 'is-invalid': errors.username }"
            required
            @input="clearError('username')"
          />
          <div v-if="errors.username" class="invalid-feedback">{{ errors.username }}</div>
          <small class="form-text text-muted">3-20 characters, letters, numbers, and underscores only</small>
        </div>

        <!-- Email -->
        <div class="form-group">
          <label for="email">Email Address</label>
          <input
            type="email"
            id="email"
            class="form-control"
            v-model="registerData.email"
            :class="{ 'is-invalid': errors.email }"
            required
            @input="clearError('email')"
          />
          <div v-if="errors.email" class="invalid-feedback">{{ errors.email }}</div>
        </div>

        <!-- Date of Birth -->
        <div class="form-group">
          <label for="date_of_birth">Date of Birth</label>
          <input
            type="date"
            id="date_of_birth"
            class="form-control"
            v-model="registerData.date_of_birth"
            :class="{ 'is-invalid': errors.date_of_birth }"
            required
            @change="validateAge"
          />
          <div v-if="errors.date_of_birth" class="invalid-feedback">{{ errors.date_of_birth }}</div>
          <small class="form-text text-muted">You must be at least 15 years old to register</small>
        </div>

        <!-- Country -->
        <div class="form-group" ref="dropdownRef">
          <label for="country">Country</label>
          <div
            class="custom-country-select"
            tabindex="0"
            @click="toggleDropdown"
            @keydown.enter.prevent="toggleDropdown"
            @keydown.space.prevent="toggleDropdown"
            @keydown.esc="closeDropdown"
          >
            <div class="selected">
              <template v-if="selectedCountry">
                <img
                  v-if="selectedCountry.flagUrl"
                  :src="selectedCountry.flagUrl"
                  :alt="selectedCountry.code"
                  class="flag-icon"
                />
                <span v-else>{{ selectedCountry.flag }}</span>
                {{ selectedCountry.name }}
              </template>
              <template v-else>
                Select your Country
              </template>
            </div>
            <div v-show="showDropdown" class="dropdown-list">
              <div
                v-for="country in countries"
                :key="country.code"
                class="dropdown-option"
                @click="selectCountry(country)"
              >
                <img
                  v-if="country.flagUrl"
                  :src="country.flagUrl"
                  :alt="country.code"
                  class="flag-icon"
                />
                <span v-else>{{ country.flag }}</span>
                {{ country.name }}
              </div>
            </div>
          </div>
          <div v-if="errors.country" class="invalid-feedback d-block">{{ errors.country }}</div>
        </div>

        <!-- Password -->
        <div class="form-group">
          <label for="password">Password</label>
          <div class="input-group">
            <input
              :type="showPassword ? 'text' : 'password'"
              id="password"
              class="form-control"
              v-model="registerData.password"
              :class="{ 'is-invalid': errors.password }"
              required
              @input="validatePassword"
            />
            <div class="input-group-append">
              <button
                class="btn btn-outline-secondary"
                type="button"
                @click="showPassword = !showPassword"
                :aria-label="showPassword ? 'Hide password' : 'Show password'"
              >
                <i :class="showPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
              </button>
            </div>
          </div>
          <div v-if="errors.password" class="invalid-feedback d-block">{{ errors.password }}</div>
          <password-strength-meter :password="registerData.password" class="mt-2" />
          <small class="form-text text-muted">
            Password must be at least 8 characters long and include:
            <ul class="pl-3 mb-0">
              <li :class="{ 'text-success': hasMinLength }">At least 8 characters</li>
              <li :class="{ 'text-success': hasUppercase }">One uppercase letter</li>
              <li :class="{ 'text-success': hasLowercase }">One lowercase letter</li>
              <li :class="{ 'text-success': hasNumber }">One number</li>
              <li :class="{ 'text-success': hasSpecialChar }">One special character</li>
            </ul>
          </small>
        </div>

        <!-- Confirm Password -->
        <div class="form-group">
          <label for="confirmPassword">Confirm Password</label>
          <input
            :type="showConfirmPassword ? 'text' : 'password'"
            id="confirmPassword"
            class="form-control"
            v-model="registerData.confirmPassword"
            :class="{ 'is-invalid': errors.confirmPassword }"
            required
            @input="validateConfirmPassword"
          />
          <div v-if="errors.confirmPassword" class="invalid-feedback">{{ errors.confirmPassword }}</div>
          <button
            type="button"
            class="btn btn-sm btn-link p-0 mt-1 d-block"
            @click="showConfirmPassword = !showConfirmPassword"
          >
            {{ showConfirmPassword ? 'Hide' : 'Show' }} password
          </button>
        </div>

        <!-- reCAPTCHA -->
        <div class="form-group">
          <div
            id="recaptcha"
            class="g-recaptcha"
            :data-sitekey="recaptchaSiteKey"
          ></div>
          <div v-if="errors.recaptcha" class="invalid-feedback d-block">{{ errors.recaptcha }}</div>
        </div>

        <!-- Terms and Conditions -->
        <div class="form-group">
          <div class="form-check">
            <input
              type="checkbox"
              id="terms"
              class="form-check-input"
              v-model="registerData.acceptTerms"
              :class="{ 'is-invalid': errors.acceptTerms }"
              required
            />
            <label class="form-check-label" for="terms">
              I agree to the <a href="/terms" target="_blank">Terms of Service</a> and
              <a href="/privacy" target="_blank">Privacy Policy</a>
            </label>
            <div v-if="errors.acceptTerms" class="invalid-feedback d-block">{{ errors.acceptTerms }}</div>
          </div>
        </div>

        <!-- Submit Button -->
        <div class="form-group">
          <button
            type="submit"
            class="btn btn-primary btn-block btn-lg"
            :disabled="isSubmitting"
          >
            <span
              v-if="isSubmitting"
              class="spinner-border spinner-border-sm mr-2"
              role="status"
              aria-hidden="true"
            ></span>
            {{ isSubmitting ? 'Creating Account...' : 'Create Account' }}
          </button>
        </div>

        <!-- General error message -->
        <div v-if="errors.general" class="alert alert-danger text-center">
          {{ errors.general }}
        </div>

        <!-- Login Link -->
        <div class="text-center mt-3">
          <p class="mb-0">
            Already have an account?
            <router-link to="/auth/login" class="font-weight-bold">Sign In</router-link>
          </p>
        </div>
      </form>
    </div>

    <!-- OTP Verification Modal -->
    <div
      class="modal fade"
      :class="{ 'show d-block': showOtpModal }"
      tabindex="-1"
      role="dialog"
      v-if="showOtpModal"
    >
      <div class="modal-dialog modal-dialog-centered" role="document">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Verify Your Email</h5>
            <button type="button" class="close" @click="showOtpModal = false" aria-label="Close">
              <span aria-hidden="true">&times;</span>
            </button>
          </div>
          <div class="modal-body">
            <p>
              We've sent a verification code to <strong>{{ registerData.email }}</strong>.
              Please enter it below.
            </p>

            <div class="form-group">
              <label for="otp">Verification Code</label>
              <div class="d-flex justify-content-between">
                <input
                  v-for="(digit, i) in 6"
                  :key="i"
                  type="text"
                  maxlength="1"
                  class="form-control text-center mx-1 otp-input"
                  v-model="otp[i]"
                  @input="handleOtpInput($event, i)"
                  @keydown.delete="handleOtpDelete($event, i)"
                  @paste="handleOtpPaste($event)"
                  :id="'otp-' + i"
                />
              </div>
              <div v-if="otpError" class="invalid-feedback d-block">{{ otpError }}</div>
              <div class="text-center mt-3">
                <button
                  type="button"
                  class="btn btn-link p-0"
                  @click="resendOtp"
                  :disabled="resendCooldown > 0"
                >
                  Resend code {{ resendCooldown > 0 ? `(${resendCooldown}s)` : '' }}
                </button>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="showOtpModal = false">
              Cancel
            </button>
            <button
              type="button"
              class="btn btn-primary"
              @click="verifyOtp"
              :disabled="otp.join('').length !== 6 || isVerifying"
            >
              <span
                v-if="isVerifying"
                class="spinner-border spinner-border-sm mr-2"
                role="status"
                aria-hidden="true"
              ></span>
              {{ isVerifying ? 'Verifying...' : 'Verify' }}
            </button>
          </div>
        </div>
      </div>
    </div>
    <div v-if="showOtpModal" class="modal-backdrop fade show"></div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import countriesData from '@/data/countries.json'
import { useAuth } from '../../services/security'

export default {
  name: 'Register',
  setup() {
    const auth = useAuth()
    const countries = ref(countriesData)
    const showDropdown = ref(false)
    const selectedCountry = ref(null)
    const dropdownRef = ref(null)

    const registerData = ref({
      full_name: '',
      username: '',
      email: '',
      date_of_birth: '',
      country: '',
      password: '',
      confirmPassword: '',
      acceptTerms: false
    })

    const errors = ref({})
    const isSubmitting = ref(false)

    // Password visibility
    const showPassword = ref(false)
    const showConfirmPassword = ref(false)

    // OTP modal and related states
    const showOtpModal = ref(false)
    const otp = ref(Array(6).fill(''))
    const otpError = ref('')
    const isVerifying = ref(false)
    const resendCooldown = ref(0)
    let resendTimer = null

    // reCAPTCHA
    const recaptchaSiteKey = import.meta.env.VITE_RECAPTCHA_SITE_KEY || ''
    const recaptchaToken = ref('')

    // Password strength computed properties
    const hasMinLength = computed(() => registerData.value.password.length >= 8)
    const hasUppercase = computed(() => /[A-Z]/.test(registerData.value.password))
    const hasLowercase = computed(() => /[a-z]/.test(registerData.value.password))
    const hasNumber = computed(() => /[0-9]/.test(registerData.value.password))
    const hasSpecialChar = computed(() => /[^A-Za-z0-9]/.test(registerData.value.password))

    // Dropdown handlers
    function toggleDropdown() {
      showDropdown.value = !showDropdown.value
    }

    function closeDropdown() {
      showDropdown.value = false
    }

    function selectCountry(country) {
      selectedCountry.value = country
      registerData.value.country = country.name
      errors.value.country = ''
      closeDropdown()
    }

    function handleClickOutside(event) {
      if (dropdownRef.value && !dropdownRef.value.contains(event.target)) {
        closeDropdown()
      }
    }

    // Clear error on input
    function clearError(field) {
      if (errors.value[field]) errors.value[field] = ''
      if (field === 'password') validatePassword()
      if (field === 'confirmPassword') validateConfirmPassword()
    }

    // Validation functions
    function validateAge() {
      if (!registerData.value.date_of_birth) {
        errors.value.date_of_birth = 'Date of birth is required'
        return
      }
      const minAgeDate = new Date()
      minAgeDate.setFullYear(minAgeDate.getFullYear() - 15)
      const dob = new Date(registerData.value.date_of_birth)
      if (dob > minAgeDate) {
        errors.value.date_of_birth = 'You must be at least 15 years old to register'
      } else {
        errors.value.date_of_birth = ''
      }
    }

    function validatePassword() {
      const pwd = registerData.value.password
      if (!pwd) {
        errors.value.password = 'Password is required'
        return
      }
      if (
        !hasMinLength.value ||
        !hasUppercase.value ||
        !hasLowercase.value ||
        !hasNumber.value ||
        !hasSpecialChar.value
      ) {
        errors.value.password =
          'Password must be at least 8 characters long and include uppercase, lowercase, number, and special character'
      } else {
        errors.value.password = ''
      }
    }

    function validateConfirmPassword() {
      if (!registerData.value.confirmPassword) {
        errors.value.confirmPassword = 'Please confirm your password'
        return
      }
      if (registerData.value.password !== registerData.value.confirmPassword) {
        errors.value.confirmPassword = 'Passwords do not match'
      } else {
        errors.value.confirmPassword = ''
      }
    }

    function validateForm() {
      errors.value = {}
      let valid = true

      if (!registerData.value.full_name.trim()) {
        errors.value.full_name = 'Full name is required'
        valid = false
      } else if (registerData.value.full_name.length < 2) {
        errors.value.full_name = 'Full name is too short'
        valid = false
      }

      if (!registerData.value.username) {
        errors.value.username = 'Username is required'
        valid = false
      } else if (!/^[a-zA-Z0-9_]{3,20}$/.test(registerData.value.username)) {
        errors.value.username =
          'Username must be 3-20 characters and can only contain letters, numbers, and underscores'
        valid = false
      }

      if (!registerData.value.email) {
        errors.value.email = 'Email is required'
        valid = false
      } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(registerData.value.email)) {
        errors.value.email = 'Please enter a valid email address'
        valid = false
      }

      if (!registerData.value.date_of_birth) {
        errors.value.date_of_birth = 'Date of birth is required'
        valid = false
      } else {
        const minAgeDate = new Date()
        minAgeDate.setFullYear(minAgeDate.getFullYear() - 15)
        const dob = new Date(registerData.value.date_of_birth)
        if (dob > minAgeDate) {
          errors.value.date_of_birth = 'You must be at least 15 years old to register'
          valid = false
        }
      }

      if (!registerData.value.country) {
        errors.value.country = 'Please select your country'
        valid = false
      }

      validatePassword()
      if (errors.value.password) valid = false

      validateConfirmPassword()
      if (errors.value.confirmPassword) valid = false

      if (!registerData.value.acceptTerms) {
        errors.value.acceptTerms = 'You must accept the terms and conditions'
        valid = false
      }

      // reCAPTCHA validation (if enabled)
      if (import.meta.env.VITE_RECAPTCHA_ENABLED === 'true') {
        const recaptchaResponse = window.grecaptcha && window.grecaptcha.getResponse()
        if (!recaptchaResponse) {
          errors.value.recaptcha = 'Please complete the reCAPTCHA verification'
          valid = false
        } else {
          recaptchaToken.value = recaptchaResponse
        }
      }

      return valid
    }

    // OTP handlers
    function handleOtpInput(event, index) {
      const value = event.target.value.replace(/\D/g, '')
      if (value) {
        otp.value[index] = value.slice(-1)
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

    function handleOtpDelete(event, index) {
      if (event.key === 'Backspace' && !otp.value[index] && index > 0) {
        nextTick(() => {
          const prevInput = document.getElementById(`otp-${index - 1}`)
          if (prevInput) prevInput.focus()
        })
      }
    }

    function handleOtpPaste(event) {
      event.preventDefault()
      const pasteData = (event.clipboardData || window.clipboardData).getData('text')
      const numbers = pasteData.replace(/\D/g, '').slice(0, 6).split('')
      numbers.forEach((num, i) => {
        otp.value[i] = num
      })
      nextTick(() => {
        const lastIndex = numbers.length - 1
        if (lastIndex >= 0 && lastIndex < 6) {
          const nextInput = document.getElementById(`otp-${lastIndex}`)
          if (nextInput) nextInput.focus()
        }
      })
    }

    async function resendOtp() {
      try {
        await auth.resendVerificationEmail(registerData.value.email)
        startResendCooldown()
      } catch (error) {
        otpError.value = 'Failed to resend OTP. Please try again.'
        console.error('Resend OTP error:', error)
      }
    }

    function startResendCooldown() {
      resendCooldown.value = 30
      resendTimer = setInterval(() => {
        resendCooldown.value--
        if (resendCooldown.value <= 0) {
          clearInterval(resendTimer)
        }
      }, 1000)
    }

    async function verifyOtp() {
      const otpCode = otp.value.join('')
      if (otpCode.length !== 6) {
        otpError.value = 'Please enter a valid 6-digit code'
        return
      }
      isVerifying.value = true
      otpError.value = ''
      try {
        await auth.verifyEmail({
          email: registerData.value.email,
          otp: otpCode
        })
        // Redirect to login with success message
        window.location.href = '/auth/login?registered=true'
      } catch (error) {
        otpError.value = 'Invalid or expired verification code. Please try again.'
        console.error('OTP verification error:', error)
      } finally {
        isVerifying.value = false
      }
    }

    // Handle form submission
    async function handleRegister() {
      if (!validateForm()) {
        // Scroll to first error
        const firstError = Object.keys(errors.value).find(key => errors.value[key])
        if (firstError) {
          const el = document.getElementById(firstError)
          if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' })
        }
        return
      }

      isSubmitting.value = true
      try {
        await auth.register({
          full_name: registerData.value.full_name,
          username: registerData.value.username,
          email: registerData.value.email,
          date_of_birth: registerData.value.date_of_birth,
          country: registerData.value.country,
          password: registerData.value.password,
          recaptcha_token: recaptchaToken.value
        })
        showOtpModal.value = true
        startResendCooldown()
      } catch (error) {
        console.error('Registration error:', error)
        if (error.response && error.response.data) {
          const data = error.response.data
          if (data.detail) {
            if (Array.isArray(data.detail)) {
              data.detail.forEach(err => {
                const field = err.loc[err.loc.length - 1]
                errors.value[field] = err.msg
              })
            } else if (typeof data.detail === 'string') {
              errors.value.general = data.detail
            }
          } else if (data.message) {
            errors.value.general = data.message
          } else {
            errors.value.general = 'Registration failed. Please try again.'
          }
        } else {
          errors.value.general = 'Network error. Please check your connection and try again.'
        }
        window.scrollTo({ top: 0, behavior: 'smooth' })
      } finally {
        isSubmitting.value = false
      }
    }

    // Load reCAPTCHA script dynamically
    function loadRecaptcha() {
      if (document.getElementById('recaptcha-script')) return
      const script = document.createElement('script')
      script.id = 'recaptcha-script'
      script.src = `https://www.google.com/recaptcha/api.js?render=${recaptchaSiteKey}`
      script.async = true
      script.defer = true
      document.head.appendChild(script)
      return new Promise(resolve => {
        script.onload = () => {
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

    onMounted(() => {
      document.addEventListener('click', handleClickOutside)
      if (import.meta.env.VITE_RECAPTCHA_ENABLED === 'true') {
        loadRecaptcha()
      }
    })

    onUnmounted(() => {
      document.removeEventListener('click', handleClickOutside)
      if (resendTimer) clearInterval(resendTimer)
    })

    return {
      countries,
      showDropdown,
      selectedCountry,
      dropdownRef,
      registerData,
      errors,
      isSubmitting,
      showPassword,
      showConfirmPassword,
      showOtpModal,
      otp,
      otpError,
      isVerifying,
      resendCooldown,
      recaptchaSiteKey,
      hasMinLength,
      hasUppercase,
      hasLowercase,
      hasNumber,
      hasSpecialChar,
      toggleDropdown,
      closeDropdown,
      selectCountry,
      clearError,
      validateAge,
      validatePassword,
      validateConfirmPassword,
      handleOtpInput,
      handleOtpDelete,
      handleOtpPaste,
      resendOtp,
      verifyOtp,
      handleRegister
    }
  }
}
</script>

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

.is-invalid {
  border-color: #dc3545;
}

.invalid-feedback {
  color: #dc3545;
  font-size: 0.875rem;
}

.text-muted {
  color: #6c757d;
}

.btn {
  padding: 0.5rem;
  border-radius: 4px;
}

.btn-primary {
  background-color: #4ecdc4;
  border-color: #4ecdc4;
  color: white;
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

.form-check-label a {
  color: #4ecdc4;
  text-decoration: underline;
}

.form-check-label a:hover {
  color: #3ba090;
}

.custom-country-select {
  position: relative;
  width: 100%;
  cursor: pointer;
  user-select: none;
}

.selected {
  border: 1px solid #ccc;
  padding: 8px;
  background: #fff;
  border-radius: 4px;
  min-height: 38px;
  display: flex;
  align-items: center;
}

.dropdown-list {
  position: absolute;
  width: 100%;
  background: #fff;
  border: 1px solid #ddd;
  max-height: 200px;
  overflow-y: auto;
  z-index: 99;
  border-radius: 0 0 4px 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.07);
}

.dropdown-option {
  display: flex;
  align-items: center;
  padding: 6px 10px;
  cursor: pointer;
  font-size: 16px;
}

.dropdown-option:hover {
  background: #f0f0f0;
}

.flag-icon {
  width: 22px;
  height: 16px;
  margin-right: 8px;
  border-radius: 2px;
  background: #eee;
  object-fit: cover;
}

.input-group {
  display: flex;
}

.input-group-append button {
  border: 1px solid #ddd;
  border-left: 0;
  background: white;
  padding: 0 0.75rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.otp-input {
  width: 40px;
  font-size: 1.5rem;
  padding: 0.25rem;
  border: 1px solid #ddd;
  border-radius: 4px;
}

@media (max-width: 768px) {
  .auth-container {
    padding: 1rem;
  }
}
</style>
