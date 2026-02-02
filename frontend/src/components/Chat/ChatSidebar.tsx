import React from 'react';
import { Plus, MessageSquare, Trash2, Clock } from 'lucide-react';
import type { ChatSession } from '../../types';
import './ChatSidebar.css';

interface ChatSidebarProps {
    sessions: ChatSession[];
    activeSessionId: string | undefined;
    onSessionSelect: (sessionId: string) => void;
    onNewChat: () => void;
    onDeleteChat: (sessionId: string) => void;
    isLoading?: boolean;
}

export const ChatSidebar: React.FC<ChatSidebarProps> = ({
    sessions,
    activeSessionId,
    onSessionSelect,
    onNewChat,
    onDeleteChat,
    isLoading = false
}) => {
    const formatTimestamp = (dateString: string) => {
        const date = new Date(dateString);
        const now = new Date();
        const diffMs = now.getTime() - date.getTime();
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);

        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins}m ago`;
        if (diffHours < 24) return `${diffHours}h ago`;
        if (diffDays < 7) return `${diffDays}d ago`;
        return date.toLocaleDateString();
    };

    return (
        <div className="chat-sidebar">
            <div className="sidebar-header">
                <button className="new-chat-button" onClick={onNewChat}>
                    <Plus size={18} />
                    <span>New Chat</span>
                </button>
            </div>

            <div className="sessions-list">
                {isLoading ? (
                    <div className="sessions-loading">
                        <p>Loading chats...</p>
                    </div>
                ) : sessions.length === 0 ? (
                    <div className="sessions-empty">
                        <MessageSquare size={32} opacity={0.3} />
                        <p>No chats yet</p>
                    </div>
                ) : (
                    sessions.map((session) => (
                        <div
                            key={session.id}
                            className={`session-item ${activeSessionId === session.id ? 'active' : ''}`}
                            onClick={() => onSessionSelect(session.id)}
                        >
                            <div className="session-content">
                                <div className="session-icon">
                                    <MessageSquare size={16} />
                                </div>
                                <div className="session-info">
                                    <div className="session-title">{session.title}</div>
                                    <div className="session-timestamp">
                                        <Clock size={12} />
                                        <span>{formatTimestamp(session.updated_at)}</span>
                                    </div>
                                </div>
                            </div>
                            <button
                                className="delete-session-button"
                                onClick={(e) => {
                                    e.stopPropagation();
                                    onDeleteChat(session.id);
                                }}
                                title="Delete chat"
                            >
                                <Trash2 size={14} />
                            </button>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
};
