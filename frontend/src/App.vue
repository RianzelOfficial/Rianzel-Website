<template>
  <div id="app">
    <!-- Loading Screen -->
    <div v-if="isLoading" class="loading-screen">
      <div class="loading-content">
        <div class="loading-spinner"></div>
        <h2 class="loading-title">Welcome to Rianzel Official Website</h2>
        <div class="loading-progress"></div>
        <div class="loading-quotes">
          <p v-for="quote in quotes" :key="quote.id" :class="{ active: currentQuote === quote.id }">
            {{ quote.text }}
          </p>
        </div>
      </div>
    </div>

    <!-- Main App Content -->
    <div v-else>
      <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
          <router-link to="/" class="navbar-brand">Rianzel</router-link>
          <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
            <span class="navbar-toggler-icon"></span>
          </button>
          <div class="collapse navbar-collapse" id="navbarNav">
            <ul class="navbar-nav">
              <li class="nav-item">
                <router-link to="/forum" class="nav-link">Forum</router-link>
              </li>
              <li class="nav-item">
                <router-link to="/about" class="nav-link">About</router-link>
              </li>
              <li class="nav-item">
                <router-link to="/contact" class="nav-link">Contact</router-link>
              </li>
              <li class="nav-item">
                <router-link to="/faq" class="nav-link">FAQ</router-link>
              </li>
            </ul>
            <ul class="navbar-nav ms-auto">
              <li class="nav-item">
                <router-link to="/auth/login" class="nav-link">Login</router-link>
              </li>
              <li class="nav-item">
                <router-link to="/auth/register" class="nav-link">Register</router-link>
              </li>
            </ul>
          </div>
        </div>
      </nav>

      <div class="container mt-4">
        <router-view></router-view>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useAuth } from './services/security'

export default {
  setup() {
    const isLoading = ref(true)
    const currentQuote = ref(0)
    const quotes = [
      { id: 1, text: "Love is not about finding the perfect person, it's about seeing an imperfect person perfectly." },
      { id: 2, text: "The best thing to hold onto in life is each other." },
      { id: 3, text: "Love is composed of a single soul inhabiting two bodies." }
    ]

    const auth = useAuth()

    onMounted(() => {
      // Simulate loading
      setTimeout(() => {
        isLoading.value = false
      }, 3000)

      // Change quotes periodically
      setInterval(() => {
        currentQuote.value = (currentQuote.value + 1) % quotes.length
      }, 5000)
    })

    return {
      isLoading,
      quotes,
      currentQuote,
      auth
    }
  }
}
</script>

<style scoped>
.loading-screen {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #ff6b6b, #4ecdc4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.loading-content {
  text-align: center;
  color: white;
}

.loading-spinner {
  width: 100px;
  height: 100px;
  border: 5px solid #fff;
  border-radius: 50%;
  border-top-color: transparent;
  animation: spin 1s linear infinite;
  margin: 20px auto;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.loading-title {
  font-size: 2em;
  margin: 20px 0;
}

.loading-progress {
  width: 200px;
  height: 10px;
  background: rgba(255, 255, 255, 0.2);
  margin: 20px auto;
  border-radius: 5px;
  overflow: hidden;
}

.loading-progress::after {
  content: '';
  display: block;
  width: 0;
  height: 100%;
  background: white;
  animation: progress 3s ease-in-out forwards;
}

@keyframes progress {
  to {
    width: 100%;
  }
}

.loading-quotes {
  margin-top: 20px;
}

.loading-quotes p {
  opacity: 0;
  transition: opacity 0.5s;
}

.loading-quotes p.active {
  opacity: 1;
}
</style>
