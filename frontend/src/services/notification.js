import api from './api'

export const getNotifications = async (params = {}) => {
    try {
        const response = await api.get('/notifications', { params })
        return response.data
    } catch (error) {
        throw error
    }
}

export const markNotificationAsRead = async (notificationId) => {
    try {
        const response = await api.put(`/notifications/${notificationId}/read`)
        return response.data
    } catch (error) {
        throw error
    }
}

export const markAllNotificationsAsRead = async () => {
    try {
        const response = await api.put('/notifications/read-all')
        return response.data
    } catch (error) {
        throw error
    }
}

export const deleteNotification = async (notificationId) => {
    try {
        await api.delete(`/notifications/${notificationId}`)
    } catch (error) {
        throw error
    }
}

export const getUnreadNotificationCount = async () => {
    try {
        const response = await api.get('/notifications/unread-count')
        return response.data
    } catch (error) {
        throw error
    }
}

export const createPostNotification = async (postId) => {
    try {
        const response = await api.post('/notifications/post', { post_id: postId })
        return response.data
    } catch (error) {
        throw error
    }
}

export const createCommentNotification = async (commentId) => {
    try {
        const response = await api.post('/notifications/comment', { comment_id: commentId })
        return response.data
    } catch (error) {
        throw error
    }
}

export const createLikeNotification = async (postId) => {
    try {
        const response = await api.post('/notifications/like', { post_id: postId })
        return response.data
    } catch (error) {
        throw error
    }
}
