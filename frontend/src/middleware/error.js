import { store } from '../store'
import { ERROR_MESSAGES } from '../constants'
import { toast } from 'vue-toastification'

const errorHandler = {
    // Global error handler
    handleError(error) {
        console.error('Global error:', error)
        this.showErrorMessage(error)
    },

    // API error handler
    handleApiError(error) {
        console.error('API error:', error)
        
        if (error.response) {
            // Server responded with error status
            const status = error.response.status
            const data = error.response.data || {}
            
            switch (status) {
                case 401:
                    this.handleUnauthorized()
                    break
                case 403:
                    this.showErrorMessage(ERROR_MESSAGES.FORBIDDEN)
                    break
                case 404:
                    this.showErrorMessage(ERROR_MESSAGES.NOT_FOUND)
                    break
                case 422:
                    this.handleValidationErrors(data.errors)
                    break
                default:
                    this.showErrorMessage(data.message || ERROR_MESSAGES.SERVER_ERROR)
            }
        } else if (error.request) {
            // Request made but no response
            this.showErrorMessage(ERROR_MESSAGES.NETWORK)
        } else {
            // Something happened in setting up the request
            this.showErrorMessage(ERROR_MESSAGES.SERVER_ERROR)
        }
    },

    // Handle unauthorized access
    handleUnauthorized() {
        // Clear user data
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        
        // Redirect to login
        window.location.href = '/login'
    },

    // Handle validation errors
    handleValidationErrors(errors) {
        if (Array.isArray(errors)) {
            errors.forEach(error => {
                this.showErrorMessage(error.message)
            })
        } else {
            Object.values(errors).forEach(error => {
                if (Array.isArray(error)) {
                    error.forEach(msg => this.showErrorMessage(msg))
                } else {
                    this.showErrorMessage(error)
                }
            })
        }
    },

    // Show error message with toast
    showErrorMessage(message) {
        toast.error(message, {
            position: 'top-right',
            timeout: 5000,
            closeOnClick: true,
            pauseOnFocusLoss: true,
            pauseOnHover: true,
            draggable: true,
            draggablePercent: 0.6,
            showCloseButtonOnHover: false,
            hideProgressBar: true,
            closeButton: 'button',
            icon: true,
            rtl: false
        })
    },

    // Handle network connection changes
    handleNetworkChange() {
        if (!navigator.onLine) {
            this.showErrorMessage(ERROR_MESSAGES.NETWORK_ISSUE)
        }
    },

    // Install error handler
    install() {
        // Add global error handler
        window.onerror = (msg, url, line, col, error) => {
            this.handleError({
                message: msg,
                url,
                line,
                col,
                error
            })
            return true
        }

        // Add network change handler
        window.addEventListener('online', () => this.handleNetworkChange())
        window.addEventListener('offline', () => this.handleNetworkChange())
    }
}

export default errorHandler
