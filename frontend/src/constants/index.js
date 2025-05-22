export const API = {
    BASE_URL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
    WS_URL: import.meta.env.VITE_WS_URL || 'ws://localhost:8000'
}

export const ROUTES = {
    HOME: '/',
    FORUM: '/forum',
    POST: '/post/:id',
    CATEGORY: '/category/:id',
    LOGIN: '/login',
    REGISTER: '/register',
    PROFILE: '/profile',
    SETTINGS: '/settings',
    ABOUT: '/about',
    CONTACT: '/contact',
    MAINTENANCE: '/maintenance',
    NOT_FOUND: '/404'
}

export const ROLES = {
    ADMIN: 'admin',
    MODERATOR: 'moderator',
    MEMBER: 'member'
}

export const NOTIFICATION_TYPES = {
    POST: 'post',
    COMMENT: 'comment',
    LIKE: 'like',
    MENTION: 'mention',
    FOLLOW: 'follow'
}

export const POST_STATUS = {
    DRAFT: 'draft',
    PUBLISHED: 'published',
    ARCHIVED: 'archived'
}

export const COMMENT_STATUS = {
    PENDING: 'pending',
    APPROVED: 'approved',
    REJECTED: 'rejected'
}

export const THEME = {
    LIGHT: 'light',
    DARK: 'dark',
    SYSTEM: 'system'
}

export const ERROR_MESSAGES = {
    NETWORK: 'Network error. Please check your connection.',
    UNAUTHORIZED: 'Unauthorized. Please login again.',
    FORBIDDEN: 'Access denied. You don't have permission to perform this action.',
    NOT_FOUND: 'The requested resource was not found.',
    BAD_REQUEST: 'Invalid request. Please check your input.',
    SERVER_ERROR: 'Server error. Please try again later.',
    TIMEOUT: 'Request timeout. Please try again.',
    VALIDATION: 'Validation error. Please check your input.',
    DUPLICATE: 'Resource already exists.',
    NOT_IMPLEMENTED: 'This feature is not implemented yet.',
    MAINTENANCE: 'The website is currently in maintenance mode.'
}

export const DEFAULTS = {
    PAGE_SIZE: 10,
    MAX_POST_LENGTH: 10000,
    MAX_COMMENT_LENGTH: 2000,
    MAX_USERNAME_LENGTH: 50,
    MIN_PASSWORD_LENGTH: 8,
    MAX_AVATAR_SIZE: 2 * 1024 * 1024, // 2MB
    CACHE_DURATION: {
        SHORT: 5 * 60 * 1000, // 5 minutes
        MEDIUM: 15 * 60 * 1000, // 15 minutes
        LONG: 60 * 60 * 1000 // 1 hour
    }
}

export const MESSAGES = {
    SUCCESS: {
        LOGIN: 'Successfully logged in!',
        REGISTER: 'Successfully registered!',
        POST_CREATE: 'Post created successfully!',
        POST_UPDATE: 'Post updated successfully!',
        POST_DELETE: 'Post deleted successfully!',
        COMMENT_CREATE: 'Comment created successfully!',
        COMMENT_UPDATE: 'Comment updated successfully!',
        COMMENT_DELETE: 'Comment deleted successfully!',
        LIKE: 'Post liked successfully!',
        UNLIKE: 'Like removed successfully!',
        PROFILE_UPDATE: 'Profile updated successfully!',
        SETTINGS_UPDATE: 'Settings updated successfully!'
    },
    INFO: {
        LOADING: 'Loading...',
        SAVING: 'Saving...',
        DELETING: 'Deleting...',
        UPDATING: 'Updating...'
    },
    WARNING: {
        CONFIRM_DELETE: 'Are you sure you want to delete this?',
        CONFIRM_UPDATE: 'Are you sure you want to update this?',
        UNSAVED_CHANGES: 'You have unsaved changes. Are you sure you want to leave?',
        NETWORK_ISSUE: 'Network connection lost. Please check your internet connection.'
    }
}
