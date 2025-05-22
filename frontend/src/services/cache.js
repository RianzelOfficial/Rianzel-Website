import { store } from '../store'
import { getPosts, getPost, getComments, getCategories } from './forum'
import { getNotifications } from './notification'

const CACHE_KEYS = {
    POSTS: 'posts',
    POST: 'post:',
    COMMENTS: 'comments:',
    CATEGORIES: 'categories',
    NOTIFICATIONS: 'notifications'
}

const CACHE_DURATION = {
    SHORT: 5 * 60 * 1000, // 5 minutes
    MEDIUM: 15 * 60 * 1000, // 15 minutes
    LONG: 60 * 60 * 1000 // 1 hour
}

class CacheService {
    constructor() {
        this.cache = new Map()
        this.setupCacheCleaner()
    }

    setupCacheCleaner() {
        // Clean expired cache entries every hour
        setInterval(() => {
            this.cleanExpiredCache()
        }, 60 * 60 * 1000)
    }

    cleanExpiredCache() {
        const now = Date.now()
        for (const [key, entry] of this.cache.entries()) {
            if (now - entry.timestamp > entry.duration) {
                this.cache.delete(key)
            }
        }
    }

    // Cache getters
    getPosts() {
        const key = CACHE_KEYS.POSTS
        const cached = this.cache.get(key)
        if (cached && Date.now() - cached.timestamp < CACHE_DURATION.MEDIUM) {
            return Promise.resolve(cached.data)
        }
        return getPosts().then(data => {
            this.cache.set(key, {
                data,
                timestamp: Date.now(),
                duration: CACHE_DURATION.MEDIUM
            })
            return data
        })
    }

    getPost(postId) {
        const key = CACHE_KEYS.POST + postId
        const cached = this.cache.get(key)
        if (cached && Date.now() - cached.timestamp < CACHE_DURATION.SHORT) {
            return Promise.resolve(cached.data)
        }
        return getPost(postId).then(data => {
            this.cache.set(key, {
                data,
                timestamp: Date.now(),
                duration: CACHE_DURATION.SHORT
            })
            return data
        })
    }

    getComments(postId) {
        const key = CACHE_KEYS.COMMENTS + postId
        const cached = this.cache.get(key)
        if (cached && Date.now() - cached.timestamp < CACHE_DURATION.SHORT) {
            return Promise.resolve(cached.data)
        }
        return getComments(postId).then(data => {
            this.cache.set(key, {
                data,
                timestamp: Date.now(),
                duration: CACHE_DURATION.SHORT
            })
            return data
        })
    }

    getCategories() {
        const key = CACHE_KEYS.CATEGORIES
        const cached = this.cache.get(key)
        if (cached && Date.now() - cached.timestamp < CACHE_DURATION.LONG) {
            return Promise.resolve(cached.data)
        }
        return getCategories().then(data => {
            this.cache.set(key, {
                data,
                timestamp: Date.now(),
                duration: CACHE_DURATION.LONG
            })
            return data
        })
    }

    getNotifications() {
        const key = CACHE_KEYS.NOTIFICATIONS
        const cached = this.cache.get(key)
        if (cached && Date.now() - cached.timestamp < CACHE_DURATION.SHORT) {
            return Promise.resolve(cached.data)
        }
        return getNotifications().then(data => {
            this.cache.set(key, {
                data,
                timestamp: Date.now(),
                duration: CACHE_DURATION.SHORT
            })
            return data
        })
    }

    // Cache invalidators
    invalidatePost(postId) {
        this.cache.delete(CACHE_KEYS.POST + postId)
        this.cache.delete(CACHE_KEYS.POSTS)
    }

    invalidateComments(postId) {
        this.cache.delete(CACHE_KEYS.COMMENTS + postId)
    }

    invalidateNotifications() {
        this.cache.delete(CACHE_KEYS.NOTIFICATIONS)
    }

    clearCache() {
        this.cache.clear()
    }
}

// Export a singleton instance
export const cache = new CacheService()
