/**
 * Chat Types
 * TypeScript interfaces for chat components and data structures
 */

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string; // ISO 8601 format
  tool_calls?: ToolCall[];
}

export interface ToolCall {
  tool_name: string;
  parameters: Record<string, any>;
  result: any;
}

export interface Conversation {
  conversation_id: string;
  messages: ChatMessage[];
}

export interface ChatState {
  conversationId: string | null;
  messages: ChatMessage[];
  isLoading: boolean;
  error: string | null;
}

export interface ReasoningTrace {
  intent: string;
  confidence: number;
  tool_selected: string | null;
  response_time_ms: number;
}

export interface ApiChatResponse {
  conversation_id: string;
  response: string;
  tool_calls: ToolCall[];
  reasoning_trace?: ReasoningTrace;
}
