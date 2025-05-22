import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
})

// Add a request interceptor to add auth token
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token')
        if (token) {
            config.headers.Authorization = `Bearer ${token}`
        }
        return config
    },
    (error) => {
        return Promise.reject(error)
    }
)

// Add a response interceptor to handle errors
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response) {
            // Handle different error statuses
            if (error.response.status === 401) {
                // Token expired or invalid
                localStorage.removeItem('token')
                window.location.href = '/login'
            } else if (error.response.status === 403) {
                // Forbidden
                throw new Error('Access denied')
            } else if (error.response.status === 404) {
                // Not found
                throw new Error('Resource not found')
            }
        }
        return Promise.reject(error)
    }
)

// Export the API instance
export default api
