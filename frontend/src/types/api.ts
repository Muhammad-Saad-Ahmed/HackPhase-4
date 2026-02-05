/**
 * API Request/Response Types
 * Defines interfaces for backend API communication
 */

export interface ReasoningStep {
  step: number;
  action: string;
  input: Record<string, any>;
  output: Record<string, any>;
  confidence: number;
  timestamp: string;
}

export interface OrchestratorRequest {
  request: string;
  user_id: string;
  conversation_id?: string;
  application_domain: string;
}

export interface OrchestratorResponse {
  execution_id: string;
  intent: {
    type: string;
    confidence: number;
  };
  entities: Array<{
    type: string;
    value: string;
    attributes?: Record<string, any>;
  }>;
  selected_tool?: {
    tool_name: string;
    confidence: number;
    parameters: Record<string, any>;
  };
  tool_result?: Record<string, any>;
  reasoning_trace: ReasoningStep[];
  status: 'success' | 'clarification_needed' | 'failure';
  clarification?: {
    question: string;
    confidence: number;
  };
}

export interface ConversationsListResponse {
  conversations: Array<{
    conversation_id: string;
    user_id: string;
    title: string;
    created_at: string;
    updated_at: string;
  }>;
}

export interface ConversationCreateRequest {
  title: string;
}

export interface ConversationCreateResponse {
  conversation_id: string;
  user_id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface MessagesListResponse {
  messages: Array<{
    message_id: string;
    conversation_id: string;
    role: 'user' | 'agent';
    content: string;
    timestamp: string;
    tool_calls?: Array<{
      tool_name: string;
      parameters: Record<string, any>;
      result?: Record<string, any>;
      error?: string;
      status: 'success' | 'failure';
    }>;
  }>;
}

export type ApiErrorCode =
  | 'NETWORK_ERROR'
  | 'TIMEOUT'
  | 'UNAUTHORIZED'
  | 'FORBIDDEN'
  | 'NOT_FOUND'
  | 'SERVER_ERROR'
  | 'VALIDATION_ERROR';

export interface ApiError {
  message: string;
  code: ApiErrorCode;
  details?: Record<string, any>;
}
