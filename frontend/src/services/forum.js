import api from './api'

export const getPosts = async (params = {}) => {
    try {
        const response = await api.get('/posts', { params })
        return response.data
    } catch (error) {
        throw error
    }
}

export const getPost = async (postId) => {
    try {
        const response = await api.get(`/posts/${postId}`)
        return response.data
    } catch (error) {
        throw error
    }
}

export const createPost = async (postData) => {
    try {
        const response = await api.post('/posts', postData)
        return response.data
    } catch (error) {
        throw error
    }
}

export const updatePost = async (postId, postData) => {
    try {
        const response = await api.put(`/posts/${postId}`, postData)
        return response.data
    } catch (error) {
        throw error
    }
}

export const deletePost = async (postId) => {
    try {
        await api.delete(`/posts/${postId}`)
    } catch (error) {
        throw error
    }
}

export const createComment = async (commentData) => {
    try {
        const response = await api.post('/comments', commentData)
        return response.data
    } catch (error) {
        throw error
    }
}

export const updateComment = async (commentId, commentData) => {
    try {
        const response = await api.put(`/comments/${commentId}`, commentData)
        return response.data
    } catch (error) {
        throw error
    }
}

export const deleteComment = async (commentId) => {
    try {
        await api.delete(`/comments/${commentId}`)
    } catch (error) {
        throw error
    }
}

export const createLike = async (postId) => {
    try {
        const response = await api.post('/likes', { post_id: postId })
        return response.data
    } catch (error) {
        throw error
    }
}

export const removeLike = async (postId) => {
    try {
        await api.delete(`/likes/${postId}`)
    } catch (error) {
        throw error
    }
}

export const getCategories = async () => {
    try {
        const response = await api.get('/categories')
        return response.data
    } catch (error) {
        throw error
    }
}

export const createCategory = async (categoryData) => {
    try {
        const response = await api.post('/categories', categoryData)
        return response.data
    } catch (error) {
        throw error
    }
}

export const incrementPostViews = async (postId) => {
    try {
        const response = await api.get(`/posts/${postId}/views`)
        return response.data
    } catch (error) {
        throw error
    }
}
