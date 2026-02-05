# Research: Stateless Chat API & UI

**Feature**: 004-stateless-chat-api
**Date**: 2026-01-26
**Purpose**: Resolve technical unknowns and establish best practices for stateless chat API implementation

## Overview

This document consolidates research findings for implementing a stateless REST API with conversation persistence and ChatKit frontend integration. All technical decisions are documented with rationale and alternatives considered.

## Research Areas

### 1. Conversation ID Generation Strategy

**Decision**: Use Python's `uuid.uuid4()` for conversation ID generation

**Rationale**:
- UUID v4 provides 122 bits of entropy (2^122 possible values)
- Collision probability is negligible (<1 in 1 billion for 1 trillion IDs)
- Native Python support (no external dependencies)
- Stateless generation (no coordination between servers needed)
- Human-readable format: `conv_xxxxxxxx` where `xxxxxxxx` is first 8 chars of UUID

**Alternatives Considered**:
- **Snowflake IDs**: Requires coordination/epoch management; overkill for this scale
- **Auto-increment integers**: Not stateless; requires database round-trip
- **Timestamp-based**: Collision risk with concurrent requests
- **Full UUID (36 chars)**: Too long for URLs; truncated version sufficient

**Implementation Pattern**:
```python
import uuid

def generate_conversation_id() -> str:
    return f"conv_{str(uuid.uuid4())[:8]}"
```

---

### 2. Message Ordering and Pagination

**Decision**: Order by `timestamp ASC` with optional pagination via `limit` and `offset` parameters

**Rationale**:
- Chronological order is natural for conversation display
- Timestamp column already indexed for performance
- Pagination deferred to optimization phase (not required for MVP per spec SC-007: <1s for 50 messages)
- SQLModel/SQLAlchemy supports efficient ordering: `.order_by(ChatMessage.timestamp)`

**Alternatives Considered**:
- **Order by ID**: Timestamps provide better semantic ordering
- **Cursor-based pagination**: Complex to implement; offset-based sufficient for expected scale
- **No pagination**: Viable for MVP but document as future enhancement for 1000+ message conversations

**Best Practices**:
- Always fetch messages in chronological order (oldest first)
- Limit initial load to 50 messages for performance (per spec SC-007)
- Use database index on `(conversation_id, timestamp)` for efficient queries
- Frontend can implement infinite scroll if needed (load older messages on demand)

---

### 3. ChatKit Integration Patterns

**Decision**: Use ChatKit's `<ChatContainer>` with custom API adapter for backend integration

**Rationale**:
- ChatKit expects standard chat data model (messages, users, timestamps)
- Custom API adapter pattern allows mapping backend responses to ChatKit format
- Maintains separation between backend API contract and frontend library
- Supports future ChatKit version upgrades without backend changes

**Integration Architecture**:
```
Backend API → chatApi.ts (Axios) → ChatKit Adapter → ChatKit Components
```

**ChatKit Component Structure**:
- **ChatContainer**: Root component managing state and API calls
- **MessageList**: Renders message history with scrolling
- **MessageInput**: Text input with send button
- **Message**: Individual message bubble with user/assistant styling

**Best Practices**:
- Store conversation_id in browser localStorage for persistence across page refreshes
- Use ChatKit's built-in message formatting (markdown, code blocks)
- Implement optimistic UI updates (show user message immediately, then confirm from API)
- Handle loading states with ChatKit's loading indicators

**Alternatives Considered**:
- **Custom chat UI**: ChatKit provides production-ready components; custom UI would take 10x longer
- **Stream Connect**: Overkill for HTTP polling; ChatKit's simple mode sufficient
- **WebSocket integration**: Out of scope per spec; HTTP request-response model adequate

---

### 4. Conversation Reconstruction Logic

**Decision**: Load full conversation history in `ConversationService.get_conversation_history()` and pass to `AgentRunner` for context building

**Rationale**:
- Existing `ConversationService` already implements this pattern (from Phase III-B)
- AgentRunner expects full message array for context
- Database query is efficient with proper indexing
- Stateless architecture requires full reload each request

**Reconstruction Flow**:
1. Extract `conversation_id` from request
2. Query `ChatMessage` and `ChatResponse` tables: `WHERE conversation_id = ?`
3. Order results by `timestamp ASC`
4. Combine into single message array: `[{role, content, timestamp}, ...]`
5. Load `ConversationMetadata` for task references and context
6. Pass to `AgentRunner.run_conversation()`

**Performance Optimization**:
- Index on `(conversation_id, timestamp)` ensures <1s load time for 50 messages
- Metadata loaded separately to avoid JOIN overhead
- Future: implement pagination if conversations exceed 1000 messages

**Alternatives Considered**:
- **Incremental loading**: Requires maintaining state; violates stateless principle
- **Summary/compression**: Adds complexity; not needed for target scale
- **Caching**: Violates "database as single source of truth" principle

---

### 5. Stateless Request Cycle Design

**Decision**: Follow pure request-response cycle with no server-side state

**Architecture Pattern**:
```
Request → Load Context (DB) → Process (Agent) → Store Result (DB) → Response
```

**Key Principles**:
- No session storage (no Flask sessions, no in-memory cache)
- No global state or singletons with mutable state
- Each request is independent and self-contained
- Conversation ID is the only state identifier passed between requests

**Best Practices**:
- Validate conversation_id exists before loading history
- Return clear error if conversation not found: `{"error": "Conversation not found", "code": "NOT_FOUND"}`
- Use database transactions for atomicity (store user message + AI response together)
- Log request ID for debugging but don't store in memory

**Validation**:
- Test: Restart server between requests → conversation continues
- Test: Run multiple server instances → all see same conversations
- Test: No memory leaks from accumulated state

---

### 6. Error Handling and Edge Cases

**Decision**: Implement structured error responses with user-friendly messages

**Error Response Format**:
```json
{
  "error": "Human-readable message",
  "code": "ERROR_CODE",
  "details": {
    "field": "conversation_id",
    "message": "Conversation not found"
  }
}
```

**Edge Cases Addressed**:
1. **Invalid conversation_id**: Return 404 with clear message
2. **Empty message**: Return 400 validation error
3. **Concurrent requests**: Database isolation level handles race conditions
4. **Database unavailable**: Return 503 Service Unavailable with retry-after header
5. **Very long conversations (1000+ messages)**: Document pagination requirement in tasks

**Best Practices**:
- Use FastAPI's exception handlers for consistent error format
- Log errors with context (user_id, conversation_id, timestamp)
- Frontend displays user-friendly error messages (from error humanizer service)
- Implement circuit breaker for database failures (from Phase III-B utilities)

---

### 7. Frontend State Management

**Decision**: Use React Context + useState for chat state management

**Rationale**:
- Simple state needs (messages, loading, error)
- No complex data flow requiring Redux/MobX
- React Context provides sufficient global state for conversation_id
- Follows ChatKit's recommended patterns

**State Structure**:
```typescript
interface ChatState {
  conversationId: string | null;
  messages: Message[];
  isLoading: boolean;
  error: string | null;
}
```

**State Management Flow**:
1. On mount: Load conversation_id from localStorage
2. If exists: Load conversation history from API
3. On send message: Optimistically add to messages array, call API
4. On API response: Update with server message + conversation_id
5. On error: Display error, keep local messages

**Alternatives Considered**:
- **Redux**: Overkill for single-page chat app
- **MobX**: Adds unnecessary complexity
- **Direct prop drilling**: Context cleaner for nested components

---

## Summary of Key Decisions

| Area | Decision | Primary Rationale |
|------|----------|-------------------|
| Conversation ID | UUID v4 truncated to 8 chars | Stateless, collision-resistant, human-readable |
| Message Ordering | Timestamp ASC with optional pagination | Natural chronological order, indexed for performance |
| ChatKit Integration | Custom API adapter pattern | Separates backend contract from frontend library |
| Conversation Reconstruction | Full history reload on each request | Required for stateless architecture, efficient with indexing |
| Request Cycle | Pure request-response with DB persistence | Enforces stateless principle, enables restart resilience |
| Error Handling | Structured responses with user-friendly messages | Consistent API contract, good UX |
| Frontend State | React Context + useState | Simple, sufficient for single-page chat |

## Implementation Notes

### Backend Extensions (Minimal Changes)
- `chat_endpoint.py`: Already exists, confirm conversation_id handling
- `conversation_service.py`: Already implements history loading
- `agent_runner.py`: Already integrated from Phase III-B

### Frontend (New Code)
- Create React app with TypeScript
- Install ChatKit: `npm install @chatscope/chat-ui-kit-react`
- Implement API service layer with Axios
- Build component hierarchy following ChatKit patterns

### Testing Strategy
- Integration test: POST /chat without conversation_id → new ID generated
- Integration test: POST /chat with existing conversation_id → history loaded
- Integration test: Restart server → conversation resumes
- Frontend test: Send message → appears in UI → API called → response displayed
- E2E test: Full conversation flow from UI through backend

## References

- [ChatKit Documentation](https://chatscope.io/storybook/react/)
- [UUID RFC 4122](https://tools.ietf.org/html/rfc4122)
- [FastAPI SQLModel Integration](https://sqlmodel.tiangolo.com/)
- [React Context API](https://react.dev/reference/react/useContext)
- Phase III-B Implementation (backend/src/services/)
