<template>
  <div class="maintenance">
    <!-- Maintenance Banner -->
    <div class="maintenance-banner">
      <h1>Website Under Maintenance</h1>
      <p>We're making things even better for our love story. Please check back later!</p>
      <div class="maintenance-timer">
        <div class="timer-item">
          <span class="number" id="days">00</span>
          <span class="label">Days</span>
        </div>
        <div class="timer-item">
          <span class="number" id="hours">00</span>
          <span class="label">Hours</span>
        </div>
        <div class="timer-item">
          <span class="number" id="minutes">00</span>
          <span class="label">Minutes</span>
        </div>
        <div class="timer-item">
          <span class="number" id="seconds">00</span>
          <span class="label">Seconds</span>
        </div>
      </div>
    </div>

    <!-- Romantic Background -->
    <div class="romantic-background">
      <div class="heart-shower">
        <div v-for="n in 50" :key="n" class="heart" :style="getRandomHeartStyle(n)"></div>
      </div>
      <div class="love-quote">
        <p>{{ randomQuote }}</p>
        <button class="btn btn-primary" @click="getNewQuote">
          Get Another Quote
        </button>
      </div>
    </div>

    <!-- Social Media Links -->
    <div class="social-links">
      <h3>Follow Us</h3>
      <div class="social-icons">
        <a href="#" class="social-icon">
          <i class="fab fa-facebook"></i>
        </a>
        <a href="#" class="social-icon">
          <i class="fab fa-instagram"></i>
        </a>
        <a href="#" class="social-icon">
          <i class="fab fa-twitter"></i>
        </a>
        <a href="#" class="social-icon">
          <i class="fab fa-youtube"></i>
        </a>
      </div>
    </div>

    <!-- Footer -->
    <footer class="maintenance-footer">
      <p>&copy; {{ new Date().getFullYear() }} Rianzel Official Website. All rights reserved.</p>
    </footer>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'

export default {
  name: 'Maintenance',
  setup() {
    const randomQuote = ref('')
    const quotes = [
      'Love is not a feeling of happiness. Love is a willingness to sacrifice.',
      'The best thing to hold onto in life is each other.',
      'Love recognizes no barriers. It jumps hurdles, leaps fences, penetrates walls to arrive at its destination full of hope.',
      'You know you're in love when you can't fall asleep because reality is finally better than your dreams.',
      'Love is composed of a single soul inhabiting two bodies.'
    ]

    const getNewQuote = () => {
      const randomIndex = Math.floor(Math.random() * quotes.length)
      randomQuote.value = quotes[randomIndex]
    }

    const getRandomHeartStyle = (index) => {
      const size = Math.random() * 20 + 10
      const speed = Math.random() * 2 + 1
      const delay = Math.random() * 5
      return {
        '--size': `${size}px`,
        '--speed': `${speed}s`,
        '--delay': `${delay}s`
      }
    }

    // Initialize
    getNewQuote()

    return {
      randomQuote,
      getNewQuote,
      getRandomHeartStyle
    }
  }
}
</script>

<style scoped>
.maintenance {
  min-height: 100vh;
  background: linear-gradient(135deg, #ff6b6b, #4ecdc4);
  color: white;
  position: relative;
}

.maintenance-banner {
  text-align: center;
  padding: 4rem 2rem;
}

.maintenance-banner h1 {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.maintenance-banner p {
  font-size: 1.2rem;
  opacity: 0.9;
  margin-bottom: 2rem;
}

.maintenance-timer {
  display: flex;
  justify-content: center;
  gap: 2rem;
  margin-bottom: 3rem;
}

.timer-item {
  text-align: center;
}

.timer-item .number {
  font-size: 2.5rem;
  font-weight: bold;
  color: #ffd700;
  margin-bottom: 0.5rem;
}

.timer-item .label {
  color: rgba(255, 255, 255, 0.8);
}

.romantic-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  z-index: 0;
}

.heart-shower {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.heart {
  position: absolute;
  width: var(--size);
  height: var(--size);
  background: #ff6b6b;
  border-radius: 50% 50% 0 0;
  transform: rotate(45deg);
  animation: float var(--speed) linear infinite;
  animation-delay: var(--delay);
}

@keyframes float {
  0% {
    transform: translateY(0) rotate(45deg);
  }
  100% {
    transform: translateY(100vh) rotate(45deg);
  }
}

.love-quote {
  text-align: center;
  position: relative;
  z-index: 1;
  padding: 2rem;
}

.love-quote p {
  font-style: italic;
  font-size: 1.5rem;
  margin-bottom: 1rem;
}

.social-links {
  text-align: center;
  position: relative;
  z-index: 1;
  padding: 2rem;
}

.social-icons {
  display: flex;
  justify-content: center;
  gap: 1rem;
  margin-top: 1rem;
}

.social-icon {
  color: white;
  font-size: 1.5rem;
  transition: color 0.3s;
}

.social-icon:hover {
  color: #ffd700;
}

.maintenance-footer {
  text-align: center;
  position: relative;
  z-index: 1;
  padding: 1rem;
  background: rgba(0, 0, 0, 0.3);
  margin-top: 2rem;
}

.btn {
  padding: 0.75rem 1.5rem;
  border-radius: 25px;
  transition: transform 0.2s;
}

.btn:hover {
  transform: translateY(-2px);
}

@media (max-width: 768px) {
  .maintenance-banner h1 {
    font-size: 2rem;
  }

  .maintenance-timer {
    gap: 1rem;
  }

  .timer-item .number {
    font-size: 2rem;
  }
}
</style>
