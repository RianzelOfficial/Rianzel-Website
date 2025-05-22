<template>
  <div class="home">
    <!-- Hero Section -->
    <section class="hero-section">
      <div class="hero-content">
        <h1>Welcome to Rianzel Official Website</h1>
        <p class="lead">Discover our love story and join our community</p>
        <div class="cta-buttons">
          <router-link to="/forum" class="btn btn-primary btn-lg">
            Join the Forum
          </router-link>
          <router-link to="/about" class="btn btn-outline-primary btn-lg">
            Learn More
          </router-link>
        </div>
      </div>
    </section>

    <!-- Relationship Milestone -->
    <section class="milestone-section">
      <div class="container">
        <h2 class="section-title">Our Journey</h2>
        <div class="milestone-timer">
          <div class="milestone-item">
            <span class="number" id="days">0</span>
            <span class="label">Days</span>
          </div>
          <div class="milestone-item">
            <span class="number" id="hours">0</span>
            <span class="label">Hours</span>
          </div>
          <div class="milestone-item">
            <span class="number" id="minutes">0</span>
            <span class="label">Minutes</span>
          </div>
        </div>
      </div>
    </section>

    <!-- Featured Posts -->
    <section class="featured-section">
      <div class="container">
        <h2 class="section-title">Featured Posts</h2>
        <div class="row">
          <div v-for="post in featuredPosts" :key="post.id" class="col-md-4">
            <div class="card">
              <router-link :to="`/forum/post/${post.id}`" class="card-img-top">
                <img :src="post.image" :alt="post.title" class="img-fluid">
              </router-link>
              <div class="card-body">
                <h5 class="card-title">{{ post.title }}</h5>
                <p class="card-text">{{ post.excerpt }}</p>
                <div class="post-meta">
                  <span class="author">by {{ post.author }}</span>
                  <span class="comments">{{ post.comments }} comments</span>
                  <span class="likes">{{ post.likes }} likes</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Love Message Widget -->
    <section class="love-message-section">
      <div class="container">
        <h2 class="section-title">Daily Love Message</h2>
        <div class="love-message">
          <p class="message">{{ dailyMessage }}</p>
          <button class="btn btn-primary" @click="getNewMessage">
            Get New Message
          </button>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import axios from 'axios'

export default {
  name: 'Home',
  setup() {
    const featuredPosts = ref([])
    const dailyMessage = ref('')
    const startDate = new Date('2022-01-01') // Replace with actual start date

    const updateTimer = () => {
      const now = new Date()
      const diff = now - startDate
      const days = Math.floor(diff / (1000 * 60 * 60 * 24))
      const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60))
      const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))

      document.getElementById('days').textContent = days
      document.getElementById('hours').textContent = hours
      document.getElementById('minutes').textContent = minutes
    }

    const getFeaturedPosts = async () => {
      try {
        const response = await axios.get('/api/posts?featured=true')
        featuredPosts.value = response.data
      } catch (error) {
        console.error('Error fetching featured posts:', error)
      }
    }

    const getNewMessage = async () => {
      try {
        const response = await axios.get('/api/love-messages/random')
        dailyMessage.value = response.data.message
      } catch (error) {
        console.error('Error fetching love message:', error)
      }
    }

    onMounted(() => {
      updateTimer()
      setInterval(updateTimer, 60000) // Update every minute
      getFeaturedPosts()
      getNewMessage()
    })

    return {
      featuredPosts,
      dailyMessage,
      getNewMessage
    }
  }
}
</script>

<style scoped>
.hero-section {
  background: linear-gradient(135deg, #ff6b6b, #4ecdc4);
  color: white;
  padding: 100px 0;
  text-align: center;
}

.hero-content h1 {
  font-size: 3.5rem;
  margin-bottom: 1rem;
}

.hero-content .lead {
  font-size: 1.5rem;
  margin-bottom: 2rem;
}

.cta-buttons {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.milestone-section {
  padding: 50px 0;
  background-color: #f8f9fa;
}

.section-title {
  text-align: center;
  margin-bottom: 3rem;
}

.milestone-timer {
  display: flex;
  justify-content: center;
  gap: 2rem;
  margin-top: 2rem;
}

.milestone-item {
  text-align: center;
}

.milestone-item .number {
  font-size: 2.5rem;
  font-weight: bold;
  color: #ff6b6b;
}

.milestone-item .label {
  display: block;
  color: #6c757d;
}

.featured-section {
  padding: 50px 0;
}

.card {
  margin-bottom: 2rem;
  transition: transform 0.3s ease;
}

.card:hover {
  transform: translateY(-5px);
}

.post-meta {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
  font-size: 0.9rem;
  color: #6c757d;
}

.love-message-section {
  padding: 50px 0;
  background-color: #f8f9fa;
}

.love-message {
  max-width: 600px;
  margin: 0 auto;
  text-align: center;
  padding: 2rem;
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.love-message .message {
  font-style: italic;
  margin-bottom: 1rem;
}
</style>
