import api from './api'

export const getProfile = async () => {
    try {
        const response = await api.get('/profile')
        return response.data
    } catch (error) {
        throw error
    }
}

export const updateProfile = async (profileData) => {
    try {
        const response = await api.put('/profile', profileData)
        return response.data
    } catch (error) {
        throw error
    }
}

export const getProfileStats = async () => {
    try {
        const response = await api.get('/profile/stats')
        return response.data
    } catch (error) {
        throw error
    }
}

export const getProfileActivity = async (params = {}) => {
    try {
        const response = await api.get('/profile/activity', { params })
        return response.data
    } catch (error) {
        throw error
    }
}

export const getProfilePreferences = async () => {
    try {
        const response = await api.get('/profile/preferences')
        return response.data
    } catch (error) {
        throw error
    }
}

export const updateProfilePreferences = async (preferences) => {
    try {
        const response = await api.put('/profile/preferences', preferences)
        return response.data
    } catch (error) {
        throw error
    }
}

export const getProfileNotifications = async (params = {}) => {
    try {
        const response = await api.get('/profile/notifications', { params })
        return response.data
    } catch (error) {
        throw error
    }
}

export const markProfileNotificationAsRead = async (notificationId) => {
    try {
        const response = await api.put(`/profile/notifications/${notificationId}/read`)
        return response.data
    } catch (error) {
        throw error
    }
}

export const markAllProfileNotificationsAsRead = async () => {
    try {
        const response = await api.put('/profile/notifications/read-all')
        return response.data
    } catch (error) {
        throw error
    }
}

export const getUnreadProfileNotificationCount = async () => {
    try {
        const response = await api.get('/profile/notifications/unread-count')
        return response.data
    } catch (error) {
        throw error
    }
}
