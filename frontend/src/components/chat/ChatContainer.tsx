'use client';

/**
 * ChatContainer Component
 * Main wrapper for the chat interface with state management
 */
import React, { useState, useEffect, useCallback } from 'react';
import {
  MainContainer,
  ChatContainer as ChatKitContainer,
  MessageList,
  MessageInput,
  TypingIndicator,
} from '@chatscope/chat-ui-kit-react';
import '@chatscope/chat-ui-kit-styles/dist/default/styles.min.css';

import { sendMessage } from '../../services/chatApi';
import {
  getConversationId,
  setConversationId,
  clearConversationId,
} from '../../services/conversationStorage';
import { ChatMessage } from '../../types/chat.types';
import { Message } from './Message';
import { useAuth } from '../../hooks/useAuth';

export const ChatContainer: React.FC = () => {
  const { session, logout } = useAuth();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationIdState] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Load conversation ID on mount
  useEffect(() => {
    const storedId = getConversationId();
    if (storedId) {
      setConversationIdState(storedId);
    }
  }, []);

  // Auto-dismiss error after 4 seconds
  useEffect(() => {
    if (!error) return;
    const t = setTimeout(() => setError(null), 4000);
    return () => clearTimeout(t);
  }, [error]);

  // Handle sending a message
  const handleSendMessage = useCallback(
    async (textContent: string) => {
      // Clear any previous errors
      setError(null);

      // Trim the message
      const trimmedMessage = textContent.trim();
      if (!trimmedMessage) {
        return; // Don't send empty messages
      }

      // Create user message object
      const userMessage: ChatMessage = {
        id: `user-${Date.now()}`,
        role: 'user',
        content: trimmedMessage,
        timestamp: new Date().toISOString(),
      };

      // Optimistically add user message to UI
      setMessages((prev) => [...prev, userMessage]);
      setIsLoading(true);

      try {
        // Send to API (user ID extracted from JWT token by backend)
        const response = await sendMessage({
          message: trimmedMessage,
          conversation_id: conversationId || undefined,
        });

        // Store conversation ID if this is a new conversation
        if (response.conversation_id && response.conversation_id !== conversationId) {
          setConversationIdState(response.conversation_id);
          setConversationId(response.conversation_id);
        }

        // Create assistant message object
        const assistantMessage: ChatMessage = {
          id: `assistant-${Date.now()}`,
          role: 'assistant',
          content: response.response,
          timestamp: new Date().toISOString(),
          tool_calls: response.tool_calls,
        };

        // Add assistant response to UI
        setMessages((prev) => [...prev, assistantMessage]);
      } catch (err) {
        // Handle errors
        const errorMessage =
          err instanceof Error ? err.message : 'Failed to send message. Please try again.';
        setError(errorMessage);

        // Optionally remove the optimistic user message on error
        // For better UX, we'll keep it and show an error indicator
        const errorResponse: ChatMessage = {
          id: `error-${Date.now()}`,
          role: 'assistant',
          content: `Error: ${errorMessage}`,
          timestamp: new Date().toISOString(),
        };
        setMessages((prev) => [...prev, errorResponse]);
      } finally {
        setIsLoading(false);
      }
    },
    [conversationId]
  );

  // Handle starting a new conversation
  const handleNewConversation = useCallback(() => {
    clearConversationId();
    setConversationIdState(null);
    setMessages([]);
    setError(null);
  }, []);

  // Handle logout
  const handleLogout = useCallback(async () => {
    try {
      await logout();
      // Redirect to login page after logout
      if (typeof window !== 'undefined') {
        window.location.href = '/login';
      }
    } catch (err) {
      console.error('Logout failed:', err);
    }
  }, [logout]);

  return (
    <div style={{ position: 'relative', height: '100vh', width: '100%' }}>
      {/* Header with new conversation button and logout button */}
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: '60px',
          background: '#fff',
          borderBottom: '1px solid #e0e0e0',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '0 20px',
          zIndex: 10,
        }}
      >
        <h2 style={{ margin: 0, fontSize: '18px', fontWeight: 600 }}>Chat Assistant</h2>
        <div style={{ display: 'flex', gap: '12px' }}>
          <button
            onClick={handleNewConversation}
            style={{
              padding: '8px 16px',
              background: '#007bff',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '14px',
            }}
          >
            New Conversation
          </button>
          <button
            onClick={handleLogout}
            style={{
              padding: '8px 16px',
              background: '#dc3545',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '14px',
            }}
          >
            Logout
          </button>
        </div>
      </div>

      {/* Chat container */}
      <div style={{ position: 'absolute', top: '60px', bottom: 0, left: 0, right: 0 }}>
        <MainContainer>
          <ChatKitContainer>
            <MessageList
              typingIndicator={isLoading ? <TypingIndicator content="AI is thinking..." /> : null}
            >
              {messages.map((msg) => (
                <Message key={msg.id} message={msg} />
              ))}
            </MessageList>
            <MessageInput
              placeholder="Type your message here..."
              onSend={handleSendMessage}
              disabled={isLoading}
              attachButton={false}
            />
          </ChatKitContainer>
        </MainContainer>
      </div>

      {/* Error notification */}
      {error && (
        <div
          style={{
            position: 'absolute',
            top: '80px',
            left: '50%',
            transform: 'translateX(-50%)',
            background: '#f44336',
            color: 'white',
            padding: '12px 24px',
            borderRadius: '4px',
            boxShadow: '0 2px 8px rgba(0,0,0,0.2)',
            zIndex: 1000,
          }}
        >
          {error}
        </div>
      )}
    </div>
  );
};
