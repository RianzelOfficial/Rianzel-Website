import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios'
import { store } from '../store'
import { ERROR_MESSAGES } from '../constants'

interface ApiResponse<T> {
    data: T
}

interface ApiError extends Error {
    response?: {
        status: number
        data?: {
            message?: string
            errors?: Record<string, string[]>
        }
    }
}

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

export class ApiService {
    private api: AxiosInstance

    constructor() {
        this.api = axios.create({
            baseURL: API_BASE_URL,
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        })

        // Request interceptor
        this.api.interceptors.request.use(
            (config: AxiosRequestConfig) => {
                const token = localStorage.getItem('token')
                if (token) {
                    config.headers.Authorization = `Bearer ${token}`
                }
                return config
            },
            (error: AxiosError) => {
                return Promise.reject(error)
            }
        )

        // Response interceptor
        this.api.interceptors.response.use(
            (response: AxiosResponse) => response,
            (error: AxiosError) => {
                if (error.response) {
                    // Handle different error statuses
                    if (error.response.status === 401) {
                        // Token expired or invalid
                        localStorage.removeItem('token')
                        window.location.href = '/login'
                    } else if (error.response.status === 403) {
                        // Forbidden
                        throw new Error('Access denied')
                    } else if (error.response.status === 404) {
                        // Not found
                        throw new Error('Resource not found')
                    }
                }
                return Promise.reject(error)
            }
        )
    }

    public async get<T>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
        try {
            const response = await this.api.get<T>(url, config)
            return { data: response.data }
        } catch (error) {
            throw this.handleError(error)
        }
    }

    public async post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
        try {
            const response = await this.api.post<T>(url, data, config)
            return { data: response.data }
        } catch (error) {
            throw this.handleError(error)
        }
    }

    public async put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
        try {
            const response = await this.api.put<T>(url, data, config)
            return { data: response.data }
        } catch (error) {
            throw this.handleError(error)
        }
    }

    public async delete<T>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
        try {
            const response = await this.api.delete<T>(url, config)
            return { data: response.data }
        } catch (error) {
            throw this.handleError(error)
        }
    }

    private handleError(error: ApiError): ApiError {
        if (error.response) {
            const { status, data } = error.response
            const message = data?.message || ERROR_MESSAGES.SERVER_ERROR
            error.message = message
        } else {
            error.message = ERROR_MESSAGES.NETWORK
        }
        return error
    }
}

// Export a singleton instance
export const api = new ApiService()
