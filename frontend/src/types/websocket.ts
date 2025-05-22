export interface WebSocketMessage {
    type: MessageType
    data?: any
}

export enum MessageType {
    // Connection
    CONNECT = 'connect',
    DISCONNECT = 'disconnect',
    PING = 'ping',
    PONG = 'pong',

    // Authentication
    AUTH_REQUEST = 'auth_request',
    AUTH_RESPONSE = 'auth_response',
    TOKEN_REFRESH = 'token_refresh',

    // Notifications
    NEW_NOTIFICATION = 'new_notification',
    READ_NOTIFICATION = 'read_notification',
    READ_ALL_NOTIFICATIONS = 'read_all_notifications',
    DELETE_NOTIFICATION = 'delete_notification',

    // Posts
    NEW_POST = 'new_post',
    UPDATE_POST = 'update_post',
    DELETE_POST = 'delete_post',
    LIKE_POST = 'like_post',
    UNLIKE_POST = 'unlike_post',

    // Comments
    NEW_COMMENT = 'new_comment',
    UPDATE_COMMENT = 'update_comment',
    DELETE_COMMENT = 'delete_comment',
    LIKE_COMMENT = 'like_comment',
    UNLIKE_COMMENT = 'unlike_comment',

    // User
    USER_ONLINE = 'user_online',
    USER_OFFLINE = 'user_offline',
    USER_TYPING = 'user_typing',
    USER_STATUS = 'user_status',

    // Admin
    MODERATION_ACTION = 'moderation_action',
    ROLE_ASSIGNMENT = 'role_assignment',
    SYSTEM_MESSAGE = 'system_message',

    // Error
    ERROR = 'error'
}

export interface AuthRequest {
    token: string
    userId: string
}

export interface AuthResponse {
    success: boolean
    error?: string
}

export interface NotificationMessage {
    id: string
    type: string
    content: string
    timestamp: string
    read: boolean
    data?: any
}

export interface PostMessage {
    id: string
    title: string
    content: string
    author: string
    category: string
    timestamp: string
    likes: number
    comments: number
}

export interface CommentMessage {
    id: string
    content: string
    author: string
    postId: string
    timestamp: string
    likes: number
}

export interface UserStatusMessage {
    userId: string
    status: 'online' | 'offline' | 'away' | 'dnd'
    timestamp: string
}

export interface ModerationActionMessage {
    action: string
    contentId: string
    contentType: string
    moderatorId: string
    reason?: string
    timestamp: string
}

export interface SystemMessage {
    type: string
    message: string
    timestamp: string
    level: 'info' | 'warning' | 'error'
}
