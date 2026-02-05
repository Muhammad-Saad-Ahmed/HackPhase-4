'use client';

/**
 * Message Component
 * Renders individual chat messages with user/assistant styling
 */
import React from 'react';
import {
  Message as ChatKitMessage,
  Avatar,
  MessageModel,
} from '@chatscope/chat-ui-kit-react';
import { ChatMessage } from '../../types/chat.types';

interface MessageProps {
  message: ChatMessage;
}

export const Message: React.FC<MessageProps> = ({ message }) => {
  // Determine message direction and sender info
  const direction = message.role === 'user' ? 'outgoing' : 'incoming';
  const senderName = message.role === 'user' ? 'You' : 'AI Assistant';

  // Format timestamp
  const formattedTime = new Date(message.timestamp).toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit',
  });

  // Create message model for ChatKit
  const messageModel: MessageModel = {
    message: message.content,
    sentTime: formattedTime,
    sender: senderName,
    direction,
    position: 'single',
  };

  const isError = message.role === 'assistant' && message.content.startsWith('Error:');

  return (
    <div className={isError ? 'error-message' : ''}>
      <ChatKitMessage
        model={messageModel}
        avatarPosition={direction === 'incoming' ? 'tl' : undefined}
      >
        {direction === 'incoming' && (
          <Avatar
            name="AI"
            src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='40' height='40' viewBox='0 0 40 40'%3E%3Ccircle cx='20' cy='20' r='20' fill='%237c3aed'/%3E%3Ctext x='50%25' y='52%25' dominant-baseline='middle' text-anchor='middle' fill='white' font-family='Inter,system-ui,sans-serif' font-size='15' font-weight='600'%3EAI%3C/text%3E%3C/svg%3E"
          />
        )}
        {direction === 'outgoing' && (
          <Avatar
            name="User"
            src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='40' height='40' viewBox='0 0 40 40'%3E%3Ccircle cx='20' cy='20' r='20' fill='%232563eb'/%3E%3Ctext x='50%25' y='52%25' dominant-baseline='middle' text-anchor='middle' fill='white' font-family='Inter,system-ui,sans-serif' font-size='17' font-weight='600'%3EU%3C/text%3E%3C/svg%3E"
          />
        )}
      </ChatKitMessage>
    </div>
  );
};
