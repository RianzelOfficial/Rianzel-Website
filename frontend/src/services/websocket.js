import { store } from '../store'
import { markNotificationAsRead, markAllNotificationsAsRead } from './notification'

class WebSocketService {
    constructor() {
        this.socket = null
        this.reconnectAttempts = 0
        this.maxReconnectAttempts = 5
        this.reconnectInterval = 1000 // 1 second
    }

    connect() {
        if (this.socket) {
            this.socket.close()
        }

        const token = localStorage.getItem('token')
        if (!token) {
            return
        }

        const wsUrl = `${import.meta.env.VITE_WS_URL || 'ws://localhost:8000'}/ws/notifications/?token=${token}`
        
        this.socket = new WebSocket(wsUrl)

        this.socket.onopen = () => {
            console.log('WebSocket connection established')
            this.reconnectAttempts = 0
        }

        this.socket.onmessage = (event) => {
            const data = JSON.parse(event.data)
            this.handleMessage(data)
        }

        this.socket.onclose = () => {
            console.log('WebSocket connection closed')
            this.reconnect()
        }

        this.socket.onerror = (error) => {
            console.error('WebSocket error:', error)
            this.reconnect()
        }
    }

    reconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++
            setTimeout(() => {
                this.connect()
            }, this.reconnectInterval * this.reconnectAttempts)
        } else {
            console.error('Max reconnect attempts reached')
        }
    }

    handleMessage(data) {
        switch (data.type) {
            case 'notification':
                this.handleNotification(data)
                break
            case 'read_notification':
                this.handleReadNotification(data)
                break
            case 'read_all_notifications':
                this.handleReadAllNotifications(data)
                break
            default:
                console.log('Unknown message type:', data.type)
        }
    }

    handleNotification(data) {
        store.addNotification(data.notification)
    }

    handleReadNotification(data) {
        store.markNotificationAsRead(data.notification_id)
    }

    handleReadAllNotifications() {
        store.markAllNotificationsAsRead()
    }

    send(type, data = {}) {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify({
                type,
                ...data
            }))
        }
    }

    markAsRead(notificationId) {
        this.send('read_notification', { notification_id: notificationId })
    }

    markAllAsRead() {
        this.send('read_all_notifications')
    }

    disconnect() {
        if (this.socket) {
            this.socket.close()
        }
    }
}

// Export a singleton instance
export const websocket = new WebSocketService()
