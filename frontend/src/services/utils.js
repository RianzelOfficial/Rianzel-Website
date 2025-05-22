export const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    })
}

export const formatTimeAgo = (dateString) => {
    const now = new Date()
    const date = new Date(dateString)
    const diff = now - date

    const minute = 60 * 1000
    const hour = minute * 60
    const day = hour * 24
    const week = day * 7
    const month = day * 30
    const year = day * 365

    if (diff < minute) {
        return 'Just now'
    } else if (diff < hour) {
        const minutes = Math.floor(diff / minute)
        return `${minutes} minute${minutes > 1 ? 's' : ''} ago`
    } else if (diff < day) {
        const hours = Math.floor(diff / hour)
        return `${hours} hour${hours > 1 ? 's' : ''} ago`
    } else if (diff < week) {
        const days = Math.floor(diff / day)
        return `${days} day${days > 1 ? 's' : ''} ago`
    } else if (diff < month) {
        const weeks = Math.floor(diff / week)
        return `${weeks} week${weeks > 1 ? 's' : ''} ago`
    } else if (diff < year) {
        const months = Math.floor(diff / month)
        return `${months} month${months > 1 ? 's' : ''} ago`
    } else {
        const years = Math.floor(diff / year)
        return `${years} year${years > 1 ? 's' : ''} ago`
    }
}

export const truncateText = (text, length = 200) => {
    if (text.length <= length) {
        return text
    }
    return text.substring(0, length) + '...'
}

export const formatNumber = (number) => {
    return new Intl.NumberFormat('en-US').format(number)
}

export const generateSlug = (text) => {
    return text
        .toLowerCase()
        .replace(/[^\w\s-]/g, '')
        .replace(/[\s_-]+/g, '-')
        .replace(/^-+|-+$/g, '')
}

export const debounce = (func, wait) => {
    let timeout
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout)
            func(...args)
        }
        clearTimeout(timeout)
        timeout = setTimeout(later, wait)
    }
}

export const throttle = (func, limit) => {
    let inThrottle
    return function executedFunction(...args) {
        if (!inThrottle) {
            func(...args)
            inThrottle = true
            setTimeout(() => inThrottle = false, limit)
        }
    }
}

export const validateEmail = (email) => {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return re.test(email)
}

export const validatePassword = (password) => {
    // At least 8 characters, one uppercase, one lowercase, one number, one special character
    const re = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/
    return re.test(password)
}

export const generateRandomString = (length = 10) => {
    const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    let result = ''
    for (let i = 0; i < length; i++) {
        result += characters.charAt(Math.floor(Math.random() * characters.length))
    }
    return result
}

export const copyToClipboard = async (text) => {
    try {
        await navigator.clipboard.writeText(text)
        return true
    } catch (err) {
        console.error('Failed to copy text: ', err)
        return false
    }
}
