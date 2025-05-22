import { ref, computed } from 'vue'
import axios from 'axios'

const currentUser = ref(null)
const isAuthenticated = computed(() => currentUser.value !== null)

export const useAuth = () => {
  const login = async (username, password) => {
    try {
      const response = await axios.post('/api/auth/login', {
        username,
        password
      })
      currentUser.value = response.data
      return true
    } catch (error) {
      console.error('Login error:', error)
      return false
    }
  }

  const register = async (userData) => {
    try {
      const response = await axios.post('/api/auth/register', userData)
      currentUser.value = response.data
      return true
    } catch (error) {
      console.error('Registration error:', error)
      return false
    }
  }

  const logout = () => {
    currentUser.value = null
  }

  const checkAuth = async () => {
    try {
      const response = await axios.get('/api/auth/me')
      currentUser.value = response.data
    } catch (error) {
      currentUser.value = null
    }
  }

  return {
    login,
    register,
    logout,
    checkAuth,
    isAuthenticated,
    currentUser
  }
}

// Create a router guard
export const authGuard = async (to, from, next) => {
  const { isAuthenticated, checkAuth } = useAuth()
  
  if (to.meta.requiresAuth) {
    await checkAuth()
    if (!isAuthenticated.value) {
      // Redirect to login with the intended route
      next({
        name: 'Login',
        query: { redirect: to.fullPath }
      })
      return
    }
  }
  
  if (to.meta.requiresUnauth && isAuthenticated.value) {
    next('/')
    return
  }
  
  next()
}
