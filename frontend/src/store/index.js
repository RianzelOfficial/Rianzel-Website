import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getProfile, getUnreadNotificationCount } from '../services/profile'
import { getNotifications } from '../services/notification'

export const useAppStore = defineStore('app', () => {
    // State
    const user = ref(null)
    const isLoading = ref(false)
    const error = ref(null)
    const notifications = ref([])
    const unreadNotificationCount = ref(0)

    // Actions
    const initializeApp = async () => {
        isLoading.value = true
        error.value = null

        try {
            // Fetch user profile
            const profile = await getProfile()
            user.value = profile

            // Fetch notifications
            const unreadCount = await getUnreadNotificationCount()
            unreadNotificationCount.value = unreadCount

            // Fetch recent notifications
            const recentNotifications = await getNotifications({ limit: 5 })
            notifications.value = recentNotifications
        } catch (err) {
            error.value = err.message
        } finally {
            isLoading.value = false
        }
    }

    const updateUser = (userData) => {
        user.value = { ...user.value, ...userData }
    }

    const addNotification = (notification) => {
        notifications.value.unshift(notification)
        unreadNotificationCount.value++
    }

    const markNotificationAsRead = (notificationId) => {
        const index = notifications.value.findIndex(n => n.id === notificationId)
        if (index !== -1) {
            notifications.value[index].read = true
            unreadNotificationCount.value--
        }
    }

    const markAllNotificationsAsRead = () => {
        notifications.value.forEach(n => n.read = true)
        unreadNotificationCount.value = 0
    }

    // Getters
    const isAuthenticated = computed(() => user.value !== null)
    const isAdmin = computed(() => user.value?.role === 'admin')
    const hasUnreadNotifications = computed(() => unreadNotificationCount.value > 0)

    return {
        // State
        user,
        isLoading,
        error,
        notifications,
        unreadNotificationCount,

        // Actions
        initializeApp,
        updateUser,
        addNotification,
        markNotificationAsRead,
        markAllNotificationsAsRead,

        // Getters
        isAuthenticated,
        isAdmin,
        hasUnreadNotifications
    }
})

// Create the store
export const store = useAppStore()
