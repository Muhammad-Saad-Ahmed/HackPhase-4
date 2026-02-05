# Data Model: ChatKit Frontend

**Feature**: 003-chatkit-frontend
**Date**: 2026-01-16
**Status**: Complete

## Overview

This document defines TypeScript types and interfaces for the frontend application. These mirror backend entities but are optimized for frontend display and interaction.

## Frontend Types

### User Session (Auth State)

**Type**: Client-side authentication state

```typescript
interface UserSession {
  user_id: string;
  email: string;
  session_token: string; // Stored in HTTP-only cookie
  expires_at: string; // ISO 8601 timestamp
  is_authenticated: boolean;
}
```

**Usage**: Managed by useAuth hook, stored in React Context

### Conversation

**Type**: Chat conversation metadata

```typescript
interface Conversation {
  conversation_id: string;
  user_id: string;
  title: string; // Auto-generated from first message or user-set
  created_at: string; // ISO 8601
  updated_at: string; // ISO 8601
  message_count: number; // For UI display
  last_message_preview?: string; // First 100 chars of last message
}
```

**Usage**: List view in sidebar, conversation switching

### Message

**Type**: Single message in conversation

```typescript
interface Message {
  message_id: string;
  conversation_id: string;
  role: 'user' | 'agent';
  content: string; // Markdown text for agent, plain text for user
  timestamp: string; // ISO 8601
  tool_calls?: ToolCall[]; // Present for agent messages with tool invocations
}
```

**Usage**: MessageBubble component, MessageList rendering

### Tool Call

**Type**: Agent tool invocation details

```typescript
interface ToolCall {
  tool_name: string;
  parameters: Record<string, any>; // JSON object
  result?: Record<string, any>; // Success result (JSON)
  error?: string; // Error message if failed
  confidence?: number; // 0-1 confidence score
  status: 'success' | 'failure';
}
```

**Usage**: ToolCallCard component for visualization (FR-004)

### API Request/Response Types

**Orchestrator Invocation Request**:
```typescript
interface OrchestratorRequest {
  request: string; // User message text
  user_id: string;
  conversation_id?: string; // Optional, for continuing conversation
  application_domain: string; // Default "todo"
}
```

**Orchestrator Invocation Response**:
```typescript
interface OrchestratorResponse {
  execution_id: string;
  intent: {
    type: string; // "create", "list", etc.
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

interface ReasoningStep {
  step: number;
  action: string;
  input: Record<string, any>;
  output: Record<string, any>;
  confidence: number;
  timestamp: string;
}
```

**Usage**: API client response parsing, type-safe backend integration

## State Management

### React Context State

**Auth Context**:
```typescript
interface AuthContextValue {
  session: UserSession | null;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  isLoading: boolean;
  error: string | null;
}
```

**Chat Context**:
```typescript
interface ChatContextValue {
  currentConversation: Conversation | null;
  messages: Message[];
  sendMessage: (content: string) => Promise<void>;
  isTyping: boolean; // AI is generating response
  error: string | null;
}
```

### SWR Data Fetching

**Conversations List**:
```typescript
// Hook: useConversations()
const { data, error, isLoading, mutate } = useSWR<Conversation[]>(
  '/api/conversations',
  fetcher
);
```

**Messages for Conversation**:
```typescript
// Hook: useMessages(conversationId)
const { data, error, isLoading } = useSWR<Message[]>(
  `/api/conversations/${conversationId}/messages`,
  fetcher
);
```

## Component Props

### MessageBubble Props

```typescript
interface MessageBubbleProps {
  message: Message;
  showAvatar: boolean;
  showTimestamp: boolean;
}
```

### ToolCallCard Props

```typescript
interface ToolCallCardProps {
  toolCall: ToolCall;
  isExpanded: boolean;
  onToggle: () => void;
}
```

### MessageInput Props

```typescript
interface MessageInputProps {
  onSend: (message: string) => void;
  disabled: boolean; // When isTyping or error
  placeholder?: string;
}
```

## Validation Rules

**Message Validation**:
- Min length: 1 character (non-empty)
- Max length: 5000 characters
- No HTML tags allowed (sanitized before send)

**Email Validation** (Better Auth handles):
- Valid email format (RFC 5322)
- Max length: 254 characters

**Password Validation** (Better Auth handles):
- Min length: 8 characters
- Must include: uppercase, lowercase, number

## Error Types

```typescript
type ApiErrorCode =
  | 'NETWORK_ERROR'
  | 'TIMEOUT'
  | 'UNAUTHORIZED' // 401
  | 'FORBIDDEN' // 403
  | 'NOT_FOUND' // 404
  | 'SERVER_ERROR' // 500
  | 'VALIDATION_ERROR'; // 400

interface ApiError {
  message: string;
  code: ApiErrorCode;
  details?: Record<string, any>;
}
```

## Backend Model Extensions Required

**New Models in backend/src/models/conversation.py**:

```python
class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: str = Field(primary_key=True)
    user_id: str = Field(index=True)
    title: str = Field(max_length=255)
    created_at: datetime
    updated_at: datetime

class ConversationMessage(SQLModel, table=True):
    __tablename__ = "conversation_messages"

    id: str = Field(primary_key=True)
    conversation_id: str = Field(foreign_key="conversations.id")
    role: str = Field(max_length=10)  # "user" or "agent"
    content: str
    timestamp: datetime
    tool_calls: Optional[str] = Field(default=None)  # JSON string
```

## References

- Feature spec: [spec.md](spec.md)
- Research decisions: [research.md](research.md)
- TypeScript handbook: https://www.typescriptlang.org/docs/
- Backend data models (001): [backend/src/models/](../../backend/src/models/)
