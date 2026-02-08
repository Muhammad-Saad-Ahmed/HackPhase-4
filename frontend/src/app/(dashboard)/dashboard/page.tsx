'use client';

/**
 * Dashboard Page
 * Main dashboard with todo list and optional chat sidebar
 * The MCP chatbot is a FEATURE, not the main application
 */
import React, { useState } from 'react';
import { TodoList } from '../../../components/todo/TodoList';
import { ChatContainer } from '../../../components/chat/ChatContainer';
import { useAuth } from '../../../hooks/useAuth';

export default function DashboardPage() {
  const [chatVisible, setChatVisible] = useState(false);
  const { logout } = useAuth();

  const handleLogout = async () => {
    try {
      await logout();
      if (typeof window !== 'undefined') {
        window.location.href = '/login';
      }
    } catch (err) {
      console.error('Logout failed:', err);
    }
  };

  return (
    <div style={{ minHeight: '100vh', background: '#f5f5f5' }}>
      {/* Top Navigation Bar */}
      <div
        style={{
          background: '#fff',
          borderBottom: '2px solid #e0e0e0',
          padding: '0 20px',
          height: '64px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          position: 'sticky',
          top: 0,
          zIndex: 100,
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '24px' }}>
          <h1
            style={{
              margin: 0,
              fontSize: '24px',
              fontWeight: 700,
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }}
          >
            Todo App
          </h1>
          <nav style={{ display: 'flex', gap: '16px' }}>
            <a
              href="/dashboard"
              style={{
                color: '#007bff',
                textDecoration: 'none',
                fontWeight: 600,
                fontSize: '14px',
                padding: '8px 16px',
                borderRadius: '4px',
                background: '#e7f3ff',
              }}
            >
              Dashboard
            </a>
            <a
              href="/chat"
              style={{
                color: '#6c757d',
                textDecoration: 'none',
                fontWeight: 500,
                fontSize: '14px',
                padding: '8px 16px',
              }}
            >
              Chat Only
            </a>
          </nav>
        </div>

        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
          {/* Chat Toggle Button */}
          <button
            onClick={() => setChatVisible(!chatVisible)}
            style={{
              padding: '10px 20px',
              background: chatVisible ? '#28a745' : '#007bff',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: 600,
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
            }}
          >
            <span style={{ fontSize: '18px' }}>💬</span>
            {chatVisible ? 'Hide AI Assistant' : 'Show AI Assistant'}
          </button>

          {/* Logout Button */}
          <button
            onClick={handleLogout}
            style={{
              padding: '10px 20px',
              background: '#dc3545',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: 600,
            }}
          >
            Logout
          </button>
        </div>
      </div>

      {/* Main Content Area */}
      <div style={{ display: 'flex', height: 'calc(100vh - 64px)' }}>
        {/* Todo List - Main Content */}
        <div
          style={{
            flex: chatVisible ? '0 0 60%' : '1 1 100%',
            overflowY: 'auto',
            transition: 'flex 0.3s ease',
          }}
        >
          <TodoList />
        </div>

        {/* Chat Sidebar - Feature */}
        {chatVisible && (
          <div
            style={{
              flex: '0 0 40%',
              borderLeft: '2px solid #e0e0e0',
              background: '#fff',
              display: 'flex',
              flexDirection: 'column',
              height: '100%',
            }}
          >
            {/* Chat Header */}
            <div
              style={{
                padding: '16px 20px',
                borderBottom: '1px solid #e0e0e0',
                background: '#f8f9fa',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
              }}
            >
              <div>
                <h2 style={{ margin: '0 0 4px 0', fontSize: '18px', fontWeight: 600 }}>
                  AI Assistant
                </h2>
                <p style={{ margin: 0, fontSize: '12px', color: '#6c757d' }}>
                  Chat with your task assistant
                </p>
              </div>
              <button
                onClick={() => setChatVisible(false)}
                style={{
                  padding: '6px 12px',
                  background: '#e0e0e0',
                  color: '#212529',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  fontSize: '14px',
                  fontWeight: 600,
                }}
              >
                ✕
              </button>
            </div>

            {/* Chat Container */}
            <div style={{ flex: 1, overflow: 'hidden' }}>
              <ChatContainer hideHeader={true} />
            </div>
          </div>
        )}
      </div>

      {/* Floating Chat Button for Mobile/Small Screens */}
      {!chatVisible && (
        <button
          onClick={() => setChatVisible(true)}
          style={{
            position: 'fixed',
            bottom: '24px',
            right: '24px',
            width: '56px',
            height: '56px',
            borderRadius: '50%',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
            border: 'none',
            cursor: 'pointer',
            fontSize: '24px',
            boxShadow: '0 4px 12px rgba(0,0,0,0.3)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000,
          }}
          title="Open AI Assistant"
        >
          💬
        </button>
      )}
    </div>
  );
}
