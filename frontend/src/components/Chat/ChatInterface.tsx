import React, { useState, useRef, useEffect } from 'react';
import { api } from '../../services/api';
import type { ChatMessage, ToolResult } from '../../types';
import { SubmissionResult } from './ToolOutputs/SubmissionResult';
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
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSendMessage = async (e?: React.FormEvent) => {
        e?.preventDefault();

        if ((!inputText.trim() && !selectedImage) || isLoading) return;

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

        try {
            const response = await api.sendChatMessage(userMsg.content, userMsg.image, threadId);

            if (response.thread_id) {
                setThreadId(response.thread_id);
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

    const handleImageSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            setSelectedImage(e.target.files[0]);
        }
    };

    const renderToolResult = (result: ToolResult) => {
        if (result.name === 'submit_solution') {
            return <SubmissionResult key={result.name} result={result.result} />;
        }
        if (result.name === 'extract_problem_from_image' || result.name === 'extract_text_from_problem_image') {
            // We could render extracted problem nicely, but text is fine for now
            // Or maybe a small "Problem Extracted" badge
            return null;
        }
        return null;
    };

    return (
        <div className="chat-interface">
            <div className="chat-messages">
                {messages.map(msg => (
                    <div key={msg.id} className={`message ${msg.role}`}>
                        <div className="message-bubble">
                            {msg.imageUrl && (
                                <img src={msg.imageUrl} alt="Uploaded content" className="message-image" />
                            )}
                            <div className="message-text">{msg.content}</div>

                            {msg.toolResults && msg.toolResults.map((toolResult, idx) => (
                                <div key={idx}>
                                    {renderToolResult(toolResult)}
                                </div>
                            ))}
                        </div>
                    </div>
                ))}
                {isLoading && (
                    <div className="message assistant">
                        <div className="message-bubble typing-indicator">
                            <span>.</span><span>.</span><span>.</span>
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            <form className="chat-input-area" onSubmit={handleSendMessage}>
                <button
                    type="button"
                    className="attach-btn"
                    onClick={() => fileInputRef.current?.click()}
                >
                    📎
                </button>
                <input
                    type="file"
                    ref={fileInputRef}
                    style={{ display: 'none' }}
                    accept="image/*"
                    onChange={handleImageSelect}
                />

                {selectedImage && (
                    <div className="image-preview-badge">
                        {selectedImage.name}
                        <span onClick={() => setSelectedImage(null)}>×</span>
                    </div>
                )}

                <input
                    type="text"
                    value={inputText}
                    onChange={e => setInputText(e.target.value)}
                    placeholder="Type a message..."
                    disabled={isLoading}
                />
                <button type="submit" disabled={isLoading || (!inputText && !selectedImage)}>
                    Send
                </button>
            </form>
        </div>
    );
};
