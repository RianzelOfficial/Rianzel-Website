<template>
  <div class="profile">
    <!-- Profile Header -->
    <div class="profile-header">
      <div class="profile-cover">
        <img :src="user.coverPhoto" alt="Cover Photo" class="cover-image">
        <div class="profile-avatar">
          <img :src="user.avatar" alt="Profile Photo" class="avatar-image">
        </div>
      </div>
      <div class="profile-info">
        <h1>{{ user.username }}</h1>
        <p class="user-role">{{ user.role }}</p>
        <p class="user-stats">
          <span>{{ user.postsCount }} Posts</span>
          <span>{{ user.commentsCount }} Comments</span>
          <span>{{ user.likesCount }} Likes</span>
        </p>
        <div class="profile-actions">
          <button class="btn btn-primary" @click="editProfile">
            Edit Profile
          </button>
          <button class="btn btn-outline-primary" @click="viewPreferences">
            Preferences
          </button>
        </div>
      </div>
    </div>

    <!-- Profile Tabs -->
    <div class="profile-tabs">
      <ul class="nav nav-tabs" role="tablist">
        <li class="nav-item">
          <a class="nav-link active" data-bs-toggle="tab" href="#posts">Posts</a>
        </li>
        <li class="nav-item">
          <a class="nav-link" data-bs-toggle="tab" href="#comments">Comments</a>
        </li>
        <li class="nav-item">
          <a class="nav-link" data-bs-toggle="tab" href="#likes">Likes</a>
        </li>
        <li class="nav-item">
          <a class="nav-link" data-bs-toggle="tab" href="#notifications">Notifications</a>
        </li>
      </ul>

      <!-- Tab Content -->
      <div class="tab-content">
        <!-- Posts Tab -->
        <div id="posts" class="tab-pane active">
          <div class="row">
            <div v-for="post in user.posts" :key="post.id" class="col-md-4 mb-4">
              <div class="card">
                <div class="card-body">
                  <h5 class="card-title">{{ post.title }}</h5>
                  <p class="card-text">{{ post.excerpt }}</p>
                  <div class="post-meta">
                    <span class="badge bg-primary">{{ post.category }}</span>
                    <span class="text-muted">{{ formatDate(post.createdAt) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Comments Tab -->
        <div id="comments" class="tab-pane">
          <div class="comments-list">
            <div v-for="comment in user.comments" :key="comment.id" class="comment-item">
              <div class="comment-content">
                <p>{{ comment.content }}</p>
                <div class="comment-meta">
                  <span class="text-muted">{{ formatDate(comment.createdAt) }}</span>
                  <span class="text-muted">{{ comment.postTitle }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Likes Tab -->
        <div id="likes" class="tab-pane">
          <div class="likes-list">
            <div v-for="like in user.likes" :key="like.id" class="like-item">
              <div class="like-content">
                <h6>{{ like.postTitle }}</h6>
                <p class="text-muted">{{ formatDate(like.createdAt) }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Notifications Tab -->
        <div id="notifications" class="tab-pane">
          <div class="notifications-list">
            <div v-for="notification in user.notifications" :key="notification.id" class="notification-item">
              <div class="notification-content">
                <p>{{ notification.message }}</p>
                <span class="text-muted">{{ formatDate(notification.createdAt) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useAuth } from '../services/security'

export default {
  name: 'Profile',
  setup() {
    const auth = useAuth()
    const user = ref({
      username: '',
      role: '',
      avatar: '',
      coverPhoto: '',
      postsCount: 0,
      commentsCount: 0,
      likesCount: 0,
      posts: [],
      comments: [],
      likes: [],
      notifications: []
    })

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    const fetchProfileData = async () => {
      try {
        const response = await axios.get(`/api/users/${auth.currentUser.value.id}`)
        user.value = response.data
      } catch (error) {
        console.error('Error fetching profile data:', error)
      }
    }

    onMounted(() => {
      fetchProfileData()
    })

    const editProfile = () => {
      // TODO: Implement edit profile functionality
    }

    const viewPreferences = () => {
      // TODO: Implement preferences view functionality
    }

    return {
      user,
      formatDate,
      editProfile,
      viewPreferences
    }
  }
}
</script>

<style scoped>
.profile-header {
  background: linear-gradient(135deg, #ff6b6b, #4ecdc4);
  color: white;
  padding: 2rem;
  margin-bottom: 2rem;
}

.profile-cover {
  position: relative;
  height: 200px;
  overflow: hidden;
}

.cover-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.profile-avatar {
  position: absolute;
  bottom: -50px;
  left: 50%;
  transform: translateX(-50%);
}

.avatar-image {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  border: 3px solid white;
  object-fit: cover;
}

.profile-info {
  text-align: center;
  margin-top: 2rem;
}

.user-role {
  color: #ffd700;
  font-size: 0.9rem;
  margin-bottom: 1rem;
}

.user-stats {
  margin: 1rem 0;
}

.user-stats span {
  margin-right: 1rem;
  padding: 0.25rem 0.75rem;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 15px;
}

.profile-actions {
  margin-top: 1rem;
}

.profile-tabs {
  background: white;
  padding: 2rem;
  border-radius: 10px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.nav-tabs {
  border-bottom: 2px solid #dee2e6;
}

.nav-link {
  color: #333;
  font-weight: 500;
}

.nav-link.active {
  color: #4ecdc4;
  border-bottom: 2px solid #4ecdc4;
}

.tab-pane {
  padding-top: 2rem;
}

.card {
  height: 100%;
  transition: transform 0.2s;
}

.card:hover {
  transform: translateY(-5px);
}

.post-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 1rem;
}

.badge {
  font-size: 0.8rem;
}

.comments-list,
.likes-list,
.notifications-list {
  padding: 1rem;
}

.comment-item,
.like-item,
.notification-item {
  border-bottom: 1px solid #eee;
  padding: 1rem 0;
}

.comment-content,
.like-content,
.notification-content {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
}

@media (max-width: 768px) {
  .profile-header {
    padding: 1rem;
  }

  .profile-cover {
    height: 150px;
  }

  .avatar-image {
    width: 80px;
    height: 80px;
  }
}
</style>
