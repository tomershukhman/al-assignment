import React, { useState, useRef, useEffect } from 'react';
import { Send, Paperclip, X, Calculator, Bot, User } from 'lucide-react';
import { api } from '../../services/api';
import type { ChatMessage, ChatSession } from '../../types';
import { SubmissionResult } from './ToolOutputs/SubmissionResult';
import { LatexRenderer } from '../LatexRenderer';
import { ChatSidebar } from './ChatSidebar';
import './ChatInterface.css';

export const ChatInterface: React.FC = () => {
    const [messages, setMessages] = useState<ChatMessage[]>([
        {
            id: 'init-1',
            role: 'assistant',
            content: "Hello! I'm your math tutor. You can upload a problem image to get started, or just ask me a math question!"
        }
    ]);
    const [inputText, setInputText] = useState('');
    const [selectedImage, setSelectedImage] = useState<File | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [threadId, setThreadId] = useState<string | undefined>(undefined);
    const [isRestoring, setIsRestoring] = useState(false);

    // Session management state
    const [sessions, setSessions] = useState<ChatSession[]>([]);
    const [isLoadingSessions, setIsLoadingSessions] = useState(true);

    const messagesEndRef = useRef<HTMLDivElement>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    // Auto-scroll to bottom
    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, isLoading, isRestoring]);

    // Load chat sessions on mount
    useEffect(() => {
        loadChatSessions();
    }, []);

    // Restore active session on mount
    useEffect(() => {
        const storedThreadId = localStorage.getItem('chat_session_id');
        if (storedThreadId) {
            console.log('Restoring chat session:', storedThreadId);
            setThreadId(storedThreadId);
            loadChatHistory(storedThreadId);
        }
    }, []);

    const loadChatSessions = async () => {
        try {
            setIsLoadingSessions(true);
            const fetchedSessions = await api.getChatSessions();
            setSessions(fetchedSessions);
        } catch (error) {
            console.error('Failed to load chat sessions:', error);
        } finally {
            setIsLoadingSessions(false);
        }
    };

    const loadChatHistory = async (sessionId: string) => {
        try {
            setIsRestoring(true);
            const history = await api.getChatHistory(sessionId);
            if (history && history.length > 0) {
                setMessages(history);
            }
        } catch (error) {
            console.error('Failed to restore history:', error);
        } finally {
            setIsRestoring(false);
        }
    };

    const handleNewChat = () => {
        // Reset state for new chat
        setMessages([{
            id: 'init-1',
            role: 'assistant',
            content: "Hello! I'm your math tutor. You can upload a problem image to get started, or just ask me a math question!"
        }]);
        setThreadId(undefined);
        setInputText('');
        setSelectedImage(null);
        localStorage.removeItem('chat_session_id');
    };

    const handleSessionSelect = async (sessionId: string) => {
        if (sessionId === threadId) return; // Already selected

        setThreadId(sessionId);
        localStorage.setItem('chat_session_id', sessionId);
        await loadChatHistory(sessionId);
    };

    const handleDeleteSession = async (sessionId: string) => {
        try {
            await api.deleteChatSession(sessionId);
            // Remove from local state
            setSessions(prev => prev.filter(s => s.id !== sessionId));

            // If deleting active session, start new chat
            if (sessionId === threadId) {
                handleNewChat();
            }
        } catch (error) {
            console.error('Failed to delete session:', error);
        }
    };

    // Handle initial image selection
    const handleImageSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            setSelectedImage(e.target.files[0]);
        }
    };

    // Auto-resize textarea
    useEffect(() => {
        if (textareaRef.current) {
            textareaRef.current.style.height = 'auto';
            textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px';
        }
    }, [inputText]);

    const handleSendMessage = async (e?: React.FormEvent) => {
        e?.preventDefault();

        if (!inputText.trim() && !selectedImage) return;

        const userMsg: ChatMessage = {
            id: Date.now().toString(),
            role: 'user',
            content: inputText,
            image: selectedImage || undefined,
            imageUrl: selectedImage ? URL.createObjectURL(selectedImage) : undefined
        };

        setMessages(prev => [...prev, userMsg]);
        setInputText('');
        setSelectedImage(null);
        setIsLoading(true);

        if (textareaRef.current) {
            textareaRef.current.style.height = 'auto';
        }

        try {
            const response = await api.sendChatMessage(userMsg.content, userMsg.image, threadId);

            if (response.thread_id) {
                setThreadId(response.thread_id);
                localStorage.setItem('chat_session_id', response.thread_id);

                // Reload sessions to get the newly created session
                if (!threadId) {
                    await loadChatSessions();
                }
            }

            const assistantMsg: ChatMessage = {
                id: Date.now().toString() + '-ai',
                role: 'assistant',
                content: response.response,
                toolResults: response.tool_results
            };

            setMessages(prev => [...prev, assistantMsg]);
        } catch (error) {
            console.error(error);
            const errorMsg: ChatMessage = {
                id: Date.now().toString() + '-err',
                role: 'assistant',
                content: "Sorry, I encountered an error processing your message."
            };
            setMessages(prev => [...prev, errorMsg]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    };

    return (
        <div className="chat-layout">
            {/* Sidebar */}
            <ChatSidebar
                sessions={sessions}
                activeSessionId={threadId}
                onSessionSelect={handleSessionSelect}
                onNewChat={handleNewChat}
                onDeleteChat={handleDeleteSession}
                isLoading={isLoadingSessions}
            />

            {/* Main Chat Area */}
            <div className="chat-container">
                {/* Header */}
                <header className="chat-header">
                    <div className="chat-header-icon">
                        <Calculator size={24} />
                    </div>
                    <div className="chat-header-info">
                        <h1>Math Tutor</h1>
                        <p>Powered by AI</p>
                    </div>
                </header>

                {/* Messages Area */}
                <div className="message-list">
                    {messages.map((msg) => (
                        <div key={msg.id} className={`message-wrapper ${msg.role}`}>
                            <div className="message-avatar">
                                {msg.role === 'user' ? <User size={18} /> : <Bot size={18} />}
                            </div>
                            <div className="message-bubble">
                                {/* Uploaded Image Preview in Stream */}
                                {msg.imageUrl && (
                                    <img
                                        src={msg.imageUrl}
                                        alt="Uploaded problem"
                                        className="message-image"
                                    />
                                )}

                                {/* Text Content */}
                                {msg.content && <LatexRenderer text={msg.content} />}

                                {/* Tool Results (Grading Cards, etc.) */}
                                {msg.toolResults && msg.toolResults.length > 0 && (
                                    <div className="tool-results">
                                        {msg.toolResults.map((tool, idx) => (
                                            tool.name === 'submit_solution' && (
                                                <div key={idx} style={{ marginTop: '1rem' }}>
                                                    <SubmissionResult result={tool.result} variant="chat" />
                                                </div>
                                            )
                                        ))}
                                    </div>
                                )}
                            </div>
                        </div>
                    ))}

                    {isLoading && (
                        <div className="typing-indicator">
                            <div className="typing-dot"></div>
                            <div className="typing-dot"></div>
                            <div className="typing-dot"></div>
                        </div>
                    )}

                    <div ref={messagesEndRef} />
                </div>

                {/* Input Area */}
                <div className="input-area">
                    <input
                        type="file"
                        ref={fileInputRef}
                        style={{ display: 'none' }}
                        accept="image/*"
                        onChange={handleImageSelect}
                    />

                    <button
                        className={`attach-button ${selectedImage ? 'has-file' : ''}`}
                        onClick={() => fileInputRef.current?.click()}
                        title="Attach image"
                    >
                        <Paperclip size={20} />
                    </button>

                    <div className="input-wrapper">
                        {selectedImage && (
                            <div className="file-preview">
                                <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                                    <Paperclip size={14} />
                                    {selectedImage.name}
                                </span>
                                <button
                                    onClick={() => setSelectedImage(null)}
                                    style={{ border: 'none', background: 'none', cursor: 'pointer', padding: 0 }}
                                >
                                    <X size={14} color="#ef4444" />
                                </button>
                            </div>
                        )}

                        <textarea
                            ref={textareaRef}
                            className="chat-input"
                            placeholder="Type a message or paste a problem..."
                            value={inputText}
                            onChange={(e) => setInputText(e.target.value)}
                            onKeyDown={handleKeyDown}
                            rows={1}
                        />
                    </div>

                    <button
                        className="send-button"
                        onClick={() => handleSendMessage()}
                        disabled={!inputText.trim() && !selectedImage && !isLoading}
                    >
                        <Send size={20} />
                    </button>
                </div>
            </div>
        </div>
    );
};
