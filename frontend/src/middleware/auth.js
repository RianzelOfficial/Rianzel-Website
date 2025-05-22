import { store } from '../store'
import { ROUTES, ROLES } from '../constants'
import { api } from '../services/api'

const authMiddleware = {
    // Check authentication status
    checkAuth() {
        const token = localStorage.getItem('token')
        if (!token) {
            return false
        }
        return true
    },

    // Get current user
    async getCurrentUser() {
        try {
            const response = await api.get('/auth/me')
            store.user = response.data
            return response.data
        } catch (error) {
            this.logout()
            throw error
        }
    },

    // Login user
    async login(credentials) {
        try {
            const response = await api.post('/auth/login', credentials)
            const { token, user } = response.data
            
            // Save token and user
            localStorage.setItem('token', token)
            localStorage.setItem('user', JSON.stringify(user))
            
            // Update store
            store.user = user
            
            // Connect WebSocket
            import('../services/websocket').then(({ websocket }) => {
                websocket.connect()
            })
            
            return user
        } catch (error) {
            throw error
        }
    },

    // Register user
    async register(userData) {
        try {
            const response = await api.post('/auth/register', userData)
            return this.login({
                email: userData.email,
                password: userData.password
            })
        } catch (error) {
            throw error
        }
    },

    // Logout user
    logout() {
        // Clear local storage
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        
        // Clear store
        store.user = null
        
        // Disconnect WebSocket
        import('../services/websocket').then(({ websocket }) => {
            websocket.disconnect()
        })
        
        // Redirect to login
        window.location.href = ROUTES.LOGIN
    },

    // Check role
    hasRole(roles) {
        if (!Array.isArray(roles)) {
            roles = [roles]
        }
        return roles.includes(store.user?.role)
    },

    // Check permission
    hasPermission(permission) {
        const permissions = {
            [ROLES.ADMIN]: ['admin', 'moderator', 'member'],
            [ROLES.MODERATOR]: ['moderator', 'member'],
            [ROLES.MEMBER]: ['member']
        }
        return permissions[store.user?.role]?.includes(permission)
    },

    // Create auth guard
    createAuthGuard(to, from, next) {
        const requiresAuth = to.meta.requiresAuth
        const requiresRole = to.meta.requiresRole

        if (requiresAuth && !this.checkAuth()) {
            next(ROUTES.LOGIN)
            return
        }

        if (requiresRole && !this.hasRole(requiresRole)) {
            next(ROUTES.HOME)
            return
        }

        next()
    },

    // Install auth middleware
    install() {
        // Add auth guard to router
        router.beforeEach((to, from, next) => {
            this.createAuthGuard(to, from, next)
        })

        // Add auth check to API requests
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

        // Add token refresh on 401
        api.interceptors.response.use(
            (response) => response,
            async (error) => {
                if (error.response?.status === 401) {
                    const refreshResponse = await api.post('/auth/refresh')
                    if (refreshResponse) {
                        localStorage.setItem('token', refreshResponse.data.token)
                        return api.request(error.config)
                    }
                }
                return Promise.reject(error)
            }
        )
    }
}

export default authMiddleware
