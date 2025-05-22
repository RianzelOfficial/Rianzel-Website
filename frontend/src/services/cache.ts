import { store } from '../store'
import { getPosts, getPost, getComments, getCategories } from './forum'
import { getNotifications } from './notification'

interface CacheEntry {
    data: any
    timestamp: number
    duration: number
}

interface CacheService {
    cache: Map<string, CacheEntry>
    setupCacheCleaner(): void
    cleanExpiredCache(): void
    getPosts(): Promise<any[]>
    getPost(postId: number): Promise<any>
    getComments(postId: number): Promise<any[]>
    getCategories(): Promise<any[]>
    getNotifications(): Promise<any[]>
    invalidatePost(postId: number): void
    invalidateComments(postId: number): void
    invalidateNotifications(): void
    clearCache(): void
}

const CACHE_KEYS = {
    POSTS: 'posts',
    POST: 'post:',
    COMMENTS: 'comments:',
    CATEGORIES: 'categories',
    NOTIFICATIONS: 'notifications'
} as const

type CacheKey = typeof CACHE_KEYS[keyof typeof CACHE_KEYS]

const CACHE_DURATION = {
    SHORT: 5 * 60 * 1000, // 5 minutes
    MEDIUM: 15 * 60 * 1000, // 15 minutes
    LONG: 60 * 60 * 1000 // 1 hour
} as const

type CacheDuration = typeof CACHE_DURATION[keyof typeof CACHE_DURATION]

class CacheServiceImpl implements CacheService {
    private cache: Map<string, CacheEntry> = new Map()

    constructor() {
        this.setupCacheCleaner()
    }

    private setupCacheCleaner() {
        // Clean expired cache entries every hour
        setInterval(() => {
            this.cleanExpiredCache()
        }, 60 * 60 * 1000)
    }

    private cleanExpiredCache() {
        const now = Date.now()
        for (const [key, entry] of this.cache.entries()) {
            if (now - entry.timestamp > entry.duration) {
                this.cache.delete(key)
            }
        }
    }

    async getPosts(): Promise<any[]> {
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

    async getPost(postId: number): Promise<any> {
        const key = `${CACHE_KEYS.POST}${postId}`
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

    async getComments(postId: number): Promise<any[]> {
        const key = `${CACHE_KEYS.COMMENTS}${postId}`
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

    async getCategories(): Promise<any[]> {
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

    async getNotifications(): Promise<any[]> {
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

    invalidatePost(postId: number) {
        this.cache.delete(`${CACHE_KEYS.POST}${postId}`)
        this.cache.delete(CACHE_KEYS.POSTS)
    }

    invalidateComments(postId: number) {
        this.cache.delete(`${CACHE_KEYS.COMMENTS}${postId}`)
    }

    invalidateNotifications() {
        this.cache.delete(CACHE_KEYS.NOTIFICATIONS)
    }

    clearCache() {
        this.cache.clear()
    }
}

// Export a singleton instance
export const cache = new CacheServiceImpl()
