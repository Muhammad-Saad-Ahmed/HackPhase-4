/**
 * ChatContainer Component
 * Main wrapper for the chat interface with MCP tool execution and event emission
 */
'use client';

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
import { eventBus, EVENTS } from '../../services/eventBus';

interface ChatContainerProps {
  hideHeader?: boolean; // Option to hide the header for sidebar mode
  onToolExecuted?: (toolName: string) => void; // Callback when MCP tool is executed
}

export const ChatContainer: React.FC<ChatContainerProps> = ({
  hideHeader = false,
  onToolExecuted
}) => {
  const { session, logout } = useAuth();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationIdState] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [lastToolCall, setLastToolCall] = useState<string | null>(null);

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

  // Auto-dismiss tool call indicator after 3 seconds
  useEffect(() => {
    if (!lastToolCall) return;
    const t = setTimeout(() => setLastToolCall(null), 3000);
    return () => clearTimeout(t);
  }, [lastToolCall]);

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
        // Backend uses MCP tools to execute task operations
        const response = await sendMessage({
          message: trimmedMessage,
          conversation_id: conversationId || undefined,
        });

        // Store conversation ID if this is a new conversation
        if (response.conversation_id && response.conversation_id !== conversationId) {
          setConversationIdState(response.conversation_id);
          setConversationId(response.conversation_id);
        }

        // Check if MCP tools were executed
        if (response.tool_calls && response.tool_calls.length > 0) {
          const toolCall = response.tool_calls[0];
          const toolName = toolCall.tool_name;

          // Show visual indicator
          setLastToolCall(toolName);

          // Emit events for todo list to refresh
          switch (toolName) {
            case 'add_task':
              eventBus.emit(EVENTS.TASK_CREATED, toolCall.result?.data);
              eventBus.emit(EVENTS.TASKS_REFRESH);
              break;
            case 'update_task':
              eventBus.emit(EVENTS.TASK_UPDATED, toolCall.result?.data);
              eventBus.emit(EVENTS.TASKS_REFRESH);
              break;
            case 'complete_task':
              eventBus.emit(EVENTS.TASK_COMPLETED, toolCall.result?.data);
              eventBus.emit(EVENTS.TASKS_REFRESH);
              break;
            case 'delete_task':
              eventBus.emit(EVENTS.TASK_DELETED, toolCall.result?.data);
              eventBus.emit(EVENTS.TASKS_REFRESH);
              break;
            case 'list_tasks':
              // List doesn't modify data, but refresh to show latest
              eventBus.emit(EVENTS.TASKS_REFRESH);
              break;
          }

          // Emit general tool executed event
          eventBus.emit(EVENTS.CHAT_TOOL_EXECUTED, { toolName, result: toolCall.result });

          // Call optional callback
          if (onToolExecuted) {
            onToolExecuted(toolName);
          }
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
    [conversationId, onToolExecuted]
  );

  // Handle starting a new conversation
  const handleNewConversation = useCallback(() => {
    clearConversationId();
    setConversationIdState(null);
    setMessages([]);
    setError(null);
    setLastToolCall(null);
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
    <div style={{ position: 'relative', height: hideHeader ? '100%' : '100vh', width: '100%' }}>
      {/* Header with new conversation button and logout button */}
      {!hideHeader && (
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
          <h2 style={{ margin: 0, fontSize: '18px', fontWeight: 600 }}>AI Task Assistant</h2>
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
      )}

      {/* MCP Tool Execution Indicator */}
      {lastToolCall && (
        <div
          style={{
            position: 'absolute',
            top: hideHeader ? '10px' : '70px',
            left: '50%',
            transform: 'translateX(-50%)',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
            padding: '10px 20px',
            borderRadius: '20px',
            boxShadow: '0 4px 12px rgba(102,126,234,0.4)',
            zIndex: 1000,
            fontSize: '13px',
            fontWeight: 600,
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            animation: 'slideDown 0.3s ease',
          }}
        >
          <span style={{ fontSize: '16px' }}>⚡</span>
          MCP: {lastToolCall.replace('_', ' ')}
        </div>
      )}

      {/* Chat container */}
      <div style={{ position: 'absolute', top: hideHeader ? 0 : '60px', bottom: 0, left: 0, right: 0 }}>
        <MainContainer>
          <ChatKitContainer>
            <MessageList
              typingIndicator={isLoading ? <TypingIndicator content="AI is processing with MCP tools..." /> : null}
            >
              {messages.map((msg) => (
                <Message key={msg.id} message={msg} />
              ))}
            </MessageList>
            <MessageInput
              placeholder="Ask me to manage your tasks..."
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
            top: hideHeader ? '20px' : '80px',
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

      {/* New Conversation Button for Sidebar Mode */}
      {hideHeader && (
        <button
          onClick={handleNewConversation}
          style={{
            position: 'absolute',
            bottom: '80px',
            right: '20px',
            padding: '10px 16px',
            background: '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '13px',
            fontWeight: 600,
            zIndex: 10,
            boxShadow: '0 2px 8px rgba(0,0,0,0.2)',
          }}
        >
          New Conversation
        </button>
      )}

      {/* Animation styles */}
      <style>{`
        @keyframes slideDown {
          from {
            opacity: 0;
            transform: translateX(-50%) translateY(-10px);
          }
          to {
            opacity: 1;
            transform: translateX(-50%) translateY(0);
          }
        }
      `}</style>
    </div>
  );
};
