<template>
  <div class="not-found">
    <!-- 404 Animation -->
    <div class="error-animation">
      <div class="number">4</div>
      <div class="number">0</div>
      <div class="number">4</div>
    </div>

    <!-- Error Message -->
    <div class="error-message">
      <h1>Page Not Found</h1>
      <p>
        The page you're looking for doesn't exist or has been moved. 
        Please check the URL and try again.
      </p>
    </div>

    <!-- Cute Animated Couple -->
    <div class="couple-animation">
      <div class="couple">
        <div class="person person-1"></div>
        <div class="person person-2"></div>
        <div class="heart"></div>
      </div>
    </div>

    <!-- Navigation Buttons -->
    <div class="navigation-buttons">
      <router-link to="/" class="btn btn-primary">
        <i class="fas fa-home"></i> Go Home
      </router-link>
      <router-link to="/forum" class="btn btn-secondary">
        <i class="fas fa-comments"></i> Go to Forum
      </router-link>
    </div>

    <!-- Heart-Shaped Button -->
    <div class="heart-button">
      <button class="btn btn-outline-danger" @click="goBack">
        <i class="fas fa-heart"></i> Try Again
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'NotFound',
  methods: {
    goBack() {
      this.$router.go(-1)
    }
  }
}
</script>

<style scoped>
.not-found {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  background: linear-gradient(135deg, #ff6b6b, #4ecdc4);
  color: white;
}

.error-animation {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
}

.number {
  font-size: 8rem;
  font-weight: bold;
  animation: float 3s ease-in-out infinite;
}

.number:nth-child(2) {
  animation-delay: 0.5s;
}

.error-message {
  text-align: center;
  margin-bottom: 3rem;
}

.error-message h1 {
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

.error-message p {
  font-size: 1.2rem;
  opacity: 0.9;
}

.couple-animation {
  width: 300px;
  height: 200px;
  position: relative;
  margin-bottom: 2rem;
}

.couple {
  position: absolute;
  width: 100%;
  height: 100%;
  animation: couple 3s ease-in-out infinite;
}

.person {
  position: absolute;
  width: 50px;
  height: 100px;
  background: white;
  border-radius: 50px 50px 0 0;
  animation: walk 2s ease-in-out infinite;
}

.person-1 {
  left: 50%;
  transform: translateX(-50%);
}

.person-2 {
  left: 50%;
  transform: translateX(-50%);
  animation-delay: -1s;
}

.heart {
  position: absolute;
  width: 40px;
  height: 40px;
  background: #ff6b6b;
  border-radius: 50% 50% 0 0;
  transform: rotate(45deg);
  top: 50%;
  left: 50%;
  animation: heart 2s ease-in-out infinite;
}

.navigation-buttons {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
}

.btn {
  padding: 0.75rem 1.5rem;
  border-radius: 25px;
  transition: transform 0.2s;
}

.btn:hover {
  transform: translateY(-2px);
}

.heart-button {
  position: relative;
}

.heart-button button {
  position: relative;
  z-index: 1;
  padding: 0.75rem 2rem;
  border-radius: 25px;
  border: 2px solid white;
  background: transparent;
  color: white;
  transition: all 0.3s ease;
}

.heart-button button:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: scale(1.05);
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-20px);
  }
}

@keyframes couple {
  0%, 100% {
    transform: translateX(0);
  }
  50% {
    transform: translateX(-20px);
  }
}

@keyframes walk {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

@keyframes heart {
  0%, 100% {
    transform: rotate(45deg) scale(1);
  }
  50% {
    transform: rotate(45deg) scale(1.2);
  }
}

@media (max-width: 768px) {
  .number {
    font-size: 6rem;
  }

  .error-message h1 {
    font-size: 2rem;
  }

  .couple-animation {
    width: 200px;
    height: 150px;
  }

  .person {
    width: 40px;
    height: 80px;
  }
}
</style>
