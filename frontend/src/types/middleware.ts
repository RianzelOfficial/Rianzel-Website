import { AxiosError } from 'axios'
import { ToastOptions } from 'vue-toastification'

export interface ErrorMiddleware {
    handleError(error: Error): void
    handleApiError(error: AxiosError): void
    handleUnauthorized(): void
    handleValidationErrors(errors: any): void
    showErrorMessage(message: string): void
    handleNetworkChange(): void
    install(): void
}

export interface LoadingMiddleware {
    loadingStates: Map<string, number>
    startLoading(key?: string): void
    stopLoading(key?: string): void
    updateLoadingState(): void
    createLoadingInterceptor(api: any): void
    createLoadingWrapper(func: Function): Function
    createLoadingComponent(): any
    install(): void
}

export interface AuthMiddleware {
    checkAuth(): boolean
    getCurrentUser(): Promise<any>
    login(credentials: {
        email: string
        password: string
    }): Promise<any>
    register(userData: {
        email: string
        password: string
        username: string
    }): Promise<any>
    logout(): void
    hasRole(roles: string | string[]): boolean
    hasPermission(permission: string): boolean
    createAuthGuard(to: any, from: any, next: Function): void
    install(): void
}

export interface ToastConfig extends ToastOptions {
    position?: 'top-right' | 'top-center' | 'top-left' | 
                 'bottom-right' | 'bottom-center' | 'bottom-left'
    timeout?: number
    closeOnClick?: boolean
    pauseOnFocusLoss?: boolean
    pauseOnHover?: boolean
    draggable?: boolean
    draggablePercent?: number
    showCloseButtonOnHover?: boolean
    hideProgressBar?: boolean
    closeButton?: string
    icon?: boolean
    rtl?: boolean
}

export interface LoadingConfig {
    message?: string
    delay?: number
    timeout?: number
}

export interface AuthConfig {
    requiresAuth?: boolean
    requiresRole?: string | string[]
}
