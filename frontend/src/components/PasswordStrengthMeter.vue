<template>
  <div class="password-strength-meter">
    <div class="password-strength-indicator">
      <div class="strength-bar" :style="{ width: strengthPercentage + '%' }"></div>
    </div>
    <div class="strength-label" :class="strengthClass">
      {{ strengthLabel }}
    </div>
  </div>
</template>

<script>
import { computed, watch } from 'vue'

export default {
  name: 'PasswordStrengthMeter',
  props: {
    password: {
      type: String,
      default: ''
    }
  },
  setup(props) {
    // Password requirements
    const requirements = {
      length: 8,
      uppercase: /[A-Z]/,
      lowercase: /[a-z]/,
      number: /[0-9]/,
      special: /[!@#$%^&*(),.?":{}|<>]/
    }

    const score = computed(() => {
      if (!props.password) return 0

      let score = 0
      const hasLength = props.password.length >= requirements.length
      const hasUppercase = requirements.uppercase.test(props.password)
      const hasLowercase = requirements.lowercase.test(props.password)
      const hasNumber = requirements.number.test(props.password)
      const hasSpecial = requirements.special.test(props.password)

      if (hasLength) score += 20
      if (hasUppercase) score += 20
      if (hasLowercase) score += 20
      if (hasNumber) score += 20
      if (hasSpecial) score += 20

      return score
    })

    const strengthPercentage = computed(() => {
      return Math.min(score.value, 100)
    })

    const strengthClass = computed(() => {
      if (score.value >= 80) return 'strong'
      if (score.value >= 50) return 'medium'
      return 'weak'
    })

    const strengthLabel = computed(() => {
      if (score.value >= 80) return 'Strong'
      if (score.value >= 50) return 'Medium'
      return 'Weak'
    })

    return {
      strengthPercentage,
      strengthClass,
      strengthLabel
    }
  }
}
</script>

<style scoped>
.password-strength-meter {
  margin-top: 0.5rem;
}

.password-strength-indicator {
  width: 100%;
  height: 6px;
  background-color: #e1e5eb;
  border-radius: 3px;
  overflow: hidden;
}

.strength-bar {
  height: 100%;
  background-color: #dc3545;
  transition: width 0.3s ease;
  border-radius: 3px;
}

.strength-label {
  font-size: 0.875rem;
  font-weight: 500;
  margin-top: 0.5rem;
  text-transform: capitalize;
  transition: color 0.3s ease;
}

.strength-label.weak {
  color: #dc3545;
}

.strength-label.medium {
  color: #ffc107;
}

.strength-label.strong {
  color: #28a745;
}

/* Update bar colors based on strength */
.strength-bar.weak {
  background-color: #dc3545;
}

.strength-bar.medium {
  background-color: #ffc107;
}

.strength-bar.strong {
  background-color: #28a745;
}
</style>
