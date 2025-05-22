<template>
  <div class="forum">
    <!-- Forum Header -->
    <div class="forum-header">
      <div class="container">
        <div class="row">
          <div class="col-12">
            <h1>Welcome to the Nazzel & Rian Forums</h1>
            <p class="lead">Be sure to check out the FAQ. <span v-if="!isLoggedIn">You have to register before you can post. <router-link to="/auth/register" class="text-primary">Click here to register</router-link></span></p>
          </div>
        </div>
      </div>
    </div>

    <!-- Forum Categories -->
    <div class="container mt-4">
      <div class="row">
        <div class="col-12">
          <div class="card">
            <div class="card-body">
              <h3 class="card-title">Categories</h3>
              <div class="row">
                <div v-for="category in categories" :key="category.id" class="col-md-4 mb-3">
                  <div class="category-card">
                    <h4>{{ category.name }}</h4>
                    <p>{{ category.description }}</p>
                    <p class="text-muted">
                      Topics: {{ category.topicCount }} | Posts: {{ category.postCount }}
                    </p>
                    <div v-if="isLoggedIn" class="mt-2">
                      <button class="btn btn-sm btn-primary" @click="showCreatePost = true; selectedCategory = category.id">
                        Create New Topic
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Post Modal -->
    <div v-if="showCreatePost && isLoggedIn" class="modal fade show" style="display: block;">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Create New Topic</h5>
            <button type="button" class="btn-close" @click="showCreatePost = false"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="createPost">
              <div class="mb-3">
                <label for="title" class="form-label">Topic Title</label>
                <input type="text" class="form-control" id="title" v-model="newPost.title" required>
              </div>
              <div class="mb-3">
                <label for="content" class="form-label">Your Message</label>
                <textarea class="form-control" id="content" v-model="newPost.content" rows="5" required></textarea>
              </div>
              <div class="modal-footer">
                <button type="button" class="btn btn-secondary" @click="showCreatePost = false">
                  Cancel
                </button>
                <button type="submit" class="btn btn-primary">
                  Post Topic
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>

    <!-- Login Required Modal -->
    <div v-if="showLoginRequired" class="modal fade show" style="display: block;">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Login Required</h5>
            <button type="button" class="btn-close" @click="showLoginRequired = false"></button>
          </div>
          <div class="modal-body">
            <p>You need to be logged in to create posts. Please <router-link to="/auth/login" class="text-primary">login</router-link> or <router-link to="/auth/register" class="text-primary">register</router-link> first.</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Posts Grid -->
    <div class="container mt-4">
      <div class="row">
        <!-- Categories Sidebar -->
        <div class="col-md-3">
          <div class="card">
            <div class="card-header">
              <h5 class="mb-0">Categories</h5>
            </div>
            <div class="card-body">
              <div class="list-group">
                <a href="#" class="list-group-item list-group-item-action" v-for="cat in categories" :key="cat.id">
                  {{ cat.name }}
                  <span class="badge bg-primary rounded-pill float-end">
                    {{ cat.postCount }}
                  </span>
                </a>
              </div>
            </div>
          </div>
        </div>

        <!-- Posts List -->
        <div class="col-md-9">
          <div class="card">
            <div class="card-body">
              <div class="table-responsive">
                <table class="table table-hover">
                  <thead>
                    <tr>
                      <th>Title</th>
                      <th>Author</th>
                      <th>Category</th>
                      <th>Replies</th>
                      <th>Views</th>
                      <th>Last Post</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="post in posts" :key="post.id">
                      <td>
                        <router-link :to="`/forum/post/${post.id}`" class="text-decoration-none">
                          {{ post.title }}
                        </router-link>
                      </td>
                      <td>
                        <router-link :to="`/profile/${post.author.id}`" class="text-decoration-none">
                          {{ post.author.username }}
                        </router-link>
                      </td>
                      <td>
                        <span class="badge bg-secondary">
                          {{ post.category.name }}
                        </span>
                      </td>
                      <td>{{ post.comments.length }}</td>
                      <td>{{ post.views }}</td>
                      <td>
                        <small>
                          {{ formatDate(post.lastComment?.createdAt) }}
                        </small>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { useAuth } from '../services/security'
import { useI18n } from 'vue-i18n'
import { useStore } from '@/stores'
import countriesData from '../data/countries.json'

// Map country codes to language codes
const countryLanguages = {
  PH: 'tl', US: 'en', JP: 'ja', GB: 'en', AU: 'en', CA: 'en', DE: 'de', FR: 'fr', ES: 'es', IT: 'it', BR: 'pt', IN: 'en', CN: 'zh', KR: 'ko', ID: 'id', MY: 'ms', TH: 'th', VN: 'vi', MO: 'zh'
}

export default {
  name: 'Forum',
  setup() {
    const auth = useAuth()
    const posts = ref([])
    const categories = ref([])
    const showCreatePost = ref(false)
    const showLoginRequired = ref(false)
    const selectedCategory = ref(null)
    const newPost = ref({
      title: '',
      content: ''
    })

    // Pinia store and i18n
    const store = useStore()
    const { locale, t } = useI18n()

    // Set the locale based on the user's selected language (from store)
    locale.value = store.language

    // Get language code by country code
    const getLanguageByCountryCode = (code) => countryLanguages[code] || 'en'

    // Get date/time format by language
    const getDateFormat = () => store.dateFormat || 'yyyy-MM-dd'
    const getTimeFormat = () => store.timeFormat || 'HH:mm'

    // Format date/time using Intl API
    const formatDate = (dateString) => {
      const lang = store.language
      const date = new Date(dateString)
      return new Intl.DateTimeFormat(lang, {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      }).format(date)
    }

    // Countries for reference (not used for dropdown here, but available)
    const countries = ref(countriesData)

    const fetchCategories = async () => {
      try {
        const response = await axios.get('/api/categories')
        categories.value = response.data
      } catch (error) {
        console.error('Error fetching categories:', error)
      }
    }

    const fetchPosts = async () => {
      try {
        const response = await axios.get('/api/posts')
        posts.value = response.data.map(post => ({
          ...post,
          createdAt: new Date(post.createdAt).toISOString(),
          lastComment: post.lastComment ? {
            ...post.lastComment,
            createdAt: new Date(post.lastComment.createdAt).toISOString()
          } : null
        }))
      } catch (error) {
        console.error('Error fetching posts:', error)
      }
    }

    const createPost = async () => {
      if (!auth.isAuthenticated.value) {
        showLoginRequired.value = true
        return
      }

      try {
        // TODO: Implement actual post creation with API call
        console.log('Create post:', newPost.value)
        showCreatePost.value = false
        newPost.value = { title: '', content: '' }
      } catch (error) {
        console.error('Error creating post:', error)
      }
    }



    onMounted(() => {
      Promise.all([
        fetchCategories(),
        fetchPosts()
      ]).catch(error => {
        console.error('Error initializing forum:', error)
      })
    })

    return {
      posts,
      categories,
      showCreatePost,
      showLoginRequired,
      selectedCategory,
      newPost,
      createPost,
      formatDate,
      auth,
      t
    }
  }
}
</script>

<style scoped>
.forum-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.forum-actions {
  display: flex;
  gap: 1rem;
}

.card {
  margin-bottom: 1rem;
}

.table {
  margin-bottom: 0;
}

.table th {
  white-space: nowrap;
}

.badge {
  font-size: 0.8rem;
}

.list-group-item {
  border: none;
  padding: 0.5rem 1rem;
}

.list-group-item:hover {
  background-color: #f8f9fa;
}

.modal {
  background-color: rgba(0, 0, 0, 0.5);
}

@media (max-width: 768px) {
  .forum-actions {
    width: 100%;
    justify-content: center;
    margin-top: 1rem;
  }
}
</style>
