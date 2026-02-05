/**
 * Chat Page
 * Main chat interface with AI assistant
 * Phase III-C: Auth disabled for MVP (will be enabled in future phase)
 */

import { ChatContainer } from '@/components/chat/ChatContainer';

export default function ChatPage() {
  return <ChatContainer />;
}

export const metadata = {
  title: 'Chat - AI Assistant',
  description: 'Chat with your AI task assistant',
};
