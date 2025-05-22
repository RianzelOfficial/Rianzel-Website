import { store } from '../store'
import { markNotificationAsRead, markAllNotificationsAsRead } from './notification'
import { MessageType, WebSocketMessage, NotificationMessage, UserStatusMessage } from '../types/websocket'

interface WebSocketOptions {
    token: string
    url: string
    reconnectAttempts: number
    reconnectInterval: number
    heartbeatInterval: number
    maxReconnectAttempts: number
}

interface WebSocketService {
    connect(): void
    disconnect(): void
    send(message: WebSocketMessage): void
    markAsRead(notificationId: string): void
    markAllAsRead(): void
    on(event: MessageType, callback: (data: any) => void): void
    off(event: MessageType): void
    isConnected(): boolean
    ping(): void
    handleReconnect(): void
    handleHeartbeat(): void
    handleAuth(): void
    handleNotifications(): void
    handleUserStatus(): void
    handleModeration(): void
    handleErrors(): void
}

interface WebSocketOptions {
    token: string
    url: string
}

class WebSocketServiceImpl implements WebSocketService {
    private socket: WebSocket | null = null
    private reconnectAttempts: number = 0
    private maxReconnectAttempts: number = 5
    private reconnectInterval: number = 1000 // 1 second
    private heartbeatInterval: number = 30000 // 30 seconds
    private pingInterval: any
    private eventListeners: Map<MessageType, Array<(data: any) => void>> = new Map()
    private lastPing: number = 0
    private lastPong: number = 0
    private pingTimeout: any

    constructor() {
        this.initializeWebSocket()
        this.setupHeartbeat()
    }

    private initializeWebSocket() {
        const token = localStorage.getItem('token')
        if (!token) {
            console.error('No token found')
            return
        }

        const wsUrl = `${import.meta.env.VITE_WS_URL || 'ws://localhost:8000'}/ws/notifications/?token=${token}`
        
        this.socket = new WebSocket(wsUrl)

        this.setupEventHandlers()
    }

    private setupEventHandlers() {
        if (!this.socket) return

        this.socket.onopen = () => {
            console.log('WebSocket connection established')
            this.reconnectAttempts = 0
            this.send({
                type: MessageType.CONNECT
            })
            this.setupHeartbeat()
        }

        this.socket.onmessage = (event: MessageEvent) => {
            const data = JSON.parse(event.data) as WebSocketMessage
            this.handleMessage(data)
        }

        this.socket.onclose = () => {
            console.log('WebSocket connection closed')
            this.handleReconnect()
        }

        this.socket.onerror = (error: Event) => {
            console.error('WebSocket error:', error)
            this.handleReconnect()
        }
    }

    private setupHeartbeat() {
        this.clearHeartbeat()
        this.pingInterval = setInterval(() => {
            this.ping()
        }, this.heartbeatInterval)
    }

    private clearHeartbeat() {
        if (this.pingInterval) {
            clearInterval(this.pingInterval)
        }
        if (this.pingTimeout) {
            clearTimeout(this.pingTimeout)
        }
    }

    private ping() {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.lastPing = Date.now()
            this.send({
                type: MessageType.PING
            })
            this.setupPingTimeout()
        }
    }

    private setupPingTimeout() {
        if (this.pingTimeout) {
            clearTimeout(this.pingTimeout)
        }
        this.pingTimeout = setTimeout(() => {
            console.warn('WebSocket ping timeout')
            this.disconnect()
        }, this.heartbeatInterval + 5000) // 5 seconds grace period
    }

    private connect() {
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

        this.socket.onmessage = (event: MessageEvent) => {
            const data = JSON.parse(event.data) as WebSocketMessage
            this.handleMessage(data)
        }

        this.socket.onclose = () => {
            console.log('WebSocket connection closed')
            this.reconnect()
        }

        this.socket.onerror = (error: Event) => {
            console.error('WebSocket error:', error)
            this.reconnect()
        }
    }

    private reconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++
            setTimeout(() => {
                this.connect()
            }, this.reconnectInterval * this.reconnectAttempts)
        } else {
            console.error('Max reconnect attempts reached')
        }
    }

    private handleMessage(data: WebSocketMessage) {
        const { type, data: payload } = data
        
        // Emit event to all listeners
        const listeners = this.eventListeners.get(type as MessageType)
        if (listeners) {
            listeners.forEach(listener => listener(payload))
        }

        // Handle specific message types
        switch (type) {
            case MessageType.PONG:
                this.handlePong()
                break
            case MessageType.AUTH_RESPONSE:
                this.handleAuthResponse(payload)
                break
            case MessageType.NEW_NOTIFICATION:
                this.handleNewNotification(payload as NotificationMessage)
                break
            case MessageType.READ_NOTIFICATION:
                this.handleReadNotification(payload)
                break
            case MessageType.READ_ALL_NOTIFICATIONS:
                this.handleReadAllNotifications(payload)
                break
            case MessageType.USER_ONLINE:
                this.handleUserOnline(payload as UserStatusMessage)
                break
            case MessageType.USER_OFFLINE:
                this.handleUserOffline(payload as UserStatusMessage)
                break
            case MessageType.MODERATION_ACTION:
                this.handleModerationAction(payload)
                break
            case MessageType.ERROR:
                this.handleError(payload)
                break
            default:
                console.log('Unknown message type:', type)
        }
    }

    private handlePong() {
        this.lastPong = Date.now()
        this.clearPingTimeout()
    }

    private handleAuthResponse(response: AuthResponse) {
        if (!response.success) {
            console.error('WebSocket auth failed:', response.error)
            this.disconnect()
        }
    }

    private handleNewNotification(notification: NotificationMessage) {
        store.addNotification(notification)
    }

    private handleUserOnline(status: UserStatusMessage) {
        store.updateUserStatus(status.userId, 'online')
    }

    private handleUserOffline(status: UserStatusMessage) {
        store.updateUserStatus(status.userId, 'offline')
    }

    private handleModerationAction(action: ModerationActionMessage) {
        store.handleModerationAction(action)
    }

    private handleError(error: any) {
        console.error('WebSocket error:', error)
        this.disconnect()
    }
    }

    private handleNotification(data: WebSocketMessage) {
        if (data.notification) {
            store.addNotification(data.notification)
        }
    }

    private handleReadNotification(data: WebSocketMessage) {
        if (data.notification_id) {
            store.markNotificationAsRead(data.notification_id)
        }
    }

    private handleReadAllNotifications() {
        store.markAllNotificationsAsRead()
    }

    public on(event: MessageType, callback: (data: any) => void): void {
        if (!this.eventListeners.has(event)) {
            this.eventListeners.set(event, [])
        }
        this.eventListeners.get(event)?.push(callback)
    }

    public off(event: MessageType): void {
        this.eventListeners.delete(event)
    }

    public send(message: WebSocketMessage): void {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify(message))
        }
    }

    public markAsRead(notificationId: string): void {
        this.send({
            type: MessageType.READ_NOTIFICATION,
            data: { notificationId }
        })
    }

    public markAllAsRead(): void {
        this.send({
            type: MessageType.READ_ALL_NOTIFICATIONS
        })
    }

    public isConnected(): boolean {
        return this.socket?.readyState === WebSocket.OPEN
    }

    public disconnect(): void {
        if (this.socket) {
            this.clearHeartbeat()
            this.socket.close()
            this.socket = null
        }
    }

    private handleReconnect(): void {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.error('Max reconnect attempts reached')
            return
        }

        this.reconnectAttempts++
        console.log(`Reconnecting... Attempt ${this.reconnectAttempts}`)

        setTimeout(() => {
            this.initializeWebSocket()
        }, this.reconnectInterval * this.reconnectAttempts)
    }

    public markAsRead(notificationId: string) {
        this.send('read_notification', { notification_id: notificationId })
    }

    public markAllAsRead() {
        this.send('read_all_notifications')
    }

    public disconnect() {
        if (this.socket) {
            this.socket.close()
        }
    }
}

// Export a singleton instance
export const websocket = new WebSocketServiceImpl() as WebSocketService

// Initialize the service
websocket.on(MessageType.NEW_NOTIFICATION, (notification: NotificationMessage) => {
    store.addNotification(notification)
})

websocket.on(MessageType.USER_ONLINE, (status: UserStatusMessage) => {
    store.updateUserStatus(status.userId, 'online')
})

websocket.on(MessageType.USER_OFFLINE, (status: UserStatusMessage) => {
    store.updateUserStatus(status.userId, 'offline')
})

websocket.on(MessageType.MODERATION_ACTION, (action: ModerationActionMessage) => {
    store.handleModerationAction(action)
})

websocket.on(MessageType.ERROR, (error: any) => {
    console.error('WebSocket error:', error)
    store.addSystemMessage({
        type: 'error',
        message: 'WebSocket connection error',
        timestamp: new Date().toISOString()
    })
})
