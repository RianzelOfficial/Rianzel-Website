import { store } from '../store'
import { DEFAULTS } from '../constants'

const loadingMiddleware = {
    // Loading states
    loadingStates: new Map(),

    // Start loading
    startLoading(key = 'global') {
        if (!this.loadingStates.has(key)) {
            this.loadingStates.set(key, 0)
        }
        this.loadingStates.set(key, this.loadingStates.get(key) + 1)
        this.updateLoadingState()
    },

    // Stop loading
    stopLoading(key = 'global') {
        if (this.loadingStates.has(key)) {
            const count = this.loadingStates.get(key) - 1
            if (count <= 0) {
                this.loadingStates.delete(key)
            } else {
                this.loadingStates.set(key, count)
            }
            this.updateLoadingState()
        }
    },

    // Update loading state
    updateLoadingState() {
        const isLoading = this.loadingStates.size > 0
        store.isLoading = isLoading
    },

    // Create loading interceptor for API calls
    createLoadingInterceptor(api) {
        // Request interceptor
        api.interceptors.request.use(
            (config) => {
                this.startLoading(config.url)
                return config
            },
            (error) => {
                this.stopLoading()
                return Promise.reject(error)
            }
        )

        // Response interceptor
        api.interceptors.response.use(
            (response) => {
                this.stopLoading(response.config.url)
                return response
            },
            (error) => {
                this.stopLoading()
                return Promise.reject(error)
            }
        )
    },

    // Create loading wrapper for async functions
    createLoadingWrapper(func) {
        return async (...args) => {
            this.startLoading()
            try {
                return await func(...args)
            } finally {
                this.stopLoading()
            }
        }
    },

    // Create loading component
    createLoadingComponent() {
        return {
            template: `
                <div v-if="isLoading" class="loading-overlay">
                    <div class="loading-spinner">
                        <div class="spinner"></div>
                        <p>{{ loadingMessage }}</p>
                    </div>
                </div>
            `,
            props: {
                message: {
                    type: String,
                    default: DEFAULTS.INFO.LOADING
                }
            },
            computed: {
                isLoading() {
                    return store.isLoading
                },
                loadingMessage() {
                    return this.message
                }
            },
            methods: {
                startLoading() {
                    this.loadingStates.set('component', 1)
                    this.updateLoadingState()
                },
                stopLoading() {
                    this.loadingStates.delete('component')
                    this.updateLoadingState()
                }
            }
        }
    },

    // Install loading middleware
    install() {
        // Add loading component globally
        const LoadingComponent = this.createLoadingComponent()
        const app = Vue.createApp(App)
        app.component('Loading', LoadingComponent)
    }
}

export default loadingMiddleware
