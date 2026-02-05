# API Contracts: Stateless Chat API

**Feature**: 004-stateless-chat-api
**Date**: 2026-01-26
**API Version**: v1

## Overview

This directory contains API contract specifications for the stateless chat API. The API follows REST principles with JSON payloads.

## Contents

- `chat-api.yaml` - OpenAPI 3.0 specification for chat endpoint
- `api-examples.md` - Request/response examples with edge cases
- This README - Contract overview and integration guidelines

## Base URL

**Development**: `http://localhost:8000/api`
**Production**: `https://{domain}/api`

## Authentication

**Status**: Out of scope for Phase III-C

The `user_id` path parameter serves as the user identifier. Authentication is handled upstream by the calling system.

## API Endpoints

### POST /api/{user_id}/chat

**Purpose**: Send a message to the AI assistant and receive a response

**Path Parameters**:
- `user_id` (string, required): Unique identifier for the user (1-100 characters)

**Request Body**:
```json
{
  "message": "string (1-10,000 characters, required)",
  "conversation_id": "string (optional, format: conv_xxxxxxxx)"
}
```

**Success Response** (200 OK):
```json
{
  "conversation_id": "conv_abc12345",
  "response": "AI-generated response text",
  "tool_calls": [
    {
      "tool_name": "add_task",
      "parameters": {
        "title": "Buy groceries",
        "description": null
      },
      "result": {
        "success": true,
        "data": {
          "id": 42,
          "title": "Buy groceries",
          "status": "pending",
          "created_at": "2026-01-26T10:30:00Z"
        }
      }
    }
  ],
  "reasoning_trace": {
    "intent": "create",
    "confidence": 0.95,
    "tool_selected": "add_task",
    "response_time_ms": 1250
  }
}
```

**Error Responses**:

**400 Bad Request** - Validation error:
```json
{
  "error": "Validation failed",
  "code": "VALIDATION_ERROR",
  "details": {
    "field": "message",
    "message": "Message is required and must be between 1 and 10000 characters"
  }
}
```

**404 Not Found** - Conversation doesn't exist:
```json
{
  "error": "Conversation not found",
  "code": "NOT_FOUND",
  "details": {
    "field": "conversation_id",
    "message": "The specified conversation does not exist"
  }
}
```

**500 Internal Server Error** - Server error:
```json
{
  "error": "Internal server error",
  "code": "INTERNAL_ERROR",
  "details": {
    "message": "An error occurred while processing your request"
  }
}
```

## Request/Response Flow

### New Conversation Flow

```
Client                                Server
  |                                     |
  |--- POST /api/user123/chat -------->|
  |    { message: "hello" }            |
  |                                    |
  |                                    [Generate conversation_id]
  |                                    [Store user message]
  |                                    [Process with AgentRunner]
  |                                    [Store AI response]
  |                                     |
  |<-- 200 OK --------------------------
  |    {
  |      conversation_id: "conv_abc12345",
  |      response: "Hello! ...",
  |      tool_calls: []
  |    }
  |
  [Client stores conversation_id in localStorage]
```

### Continuing Conversation Flow

```
Client                                Server
  |                                     |
  |--- POST /api/user123/chat -------->|
  |    {                                |
  |      message: "add task",          |
  |      conversation_id: "conv_abc12345"
  |    }                                |
  |                                    |
  |                                    [Load conversation history]
  |                                    [Load metadata]
  |                                    [Rebuild agent context]
  |                                    [Store user message]
  |                                    [Process with AgentRunner]
  |                                    [Store AI response]
  |                                    [Update metadata]
  |                                     |
  |<-- 200 OK --------------------------
  |    {
  |      conversation_id: "conv_abc12345",
  |      response: "I've added ...",
  |      tool_calls: [{...}]
  |    }
```

### Server Restart Scenario

```
Client                                Server
  |                                     |
  |--- POST /api/user123/chat -------->|
  |    { message: "show my tasks",     |
  |      conversation_id: "conv_abc12345" }
  |                                    |
  |                                    [Load full conversation history from DB]
  |                                    [Load metadata from DB]
  |                                    [No server state exists - all from DB]
  |                                    [Process with full context]
  |                                     |
  |<-- 200 OK --------------------------
  |    {
  |      conversation_id: "conv_abc12345",
  |      response: "Here are your tasks ...",
  |      tool_calls: [{tool_name: "list_tasks", ...}]
  |    }
```

## Validation Rules

### Request Validation

| Field | Type | Required | Min Length | Max Length | Pattern |
|-------|------|----------|------------|------------|---------|
| user_id | string | Yes | 1 | 100 | Any non-empty |
| message | string | Yes | 1 | 10,000 | Any text |
| conversation_id | string | No | 13 | 13 | `^conv_[a-f0-9]{8}$` |

### Response Guarantees

- `conversation_id` will ALWAYS be present in response
- `response` will ALWAYS contain AI-generated text (1-10,000 characters)
- `tool_calls` will be empty array `[]` if no tools were called
- `reasoning_trace` will be present for debugging (may be excluded in production)

## Error Handling

### Client-Side Error Handling

```typescript
try {
  const response = await fetch(`/api/${userId}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, conversation_id })
  });

  if (!response.ok) {
    const error = await response.json();
    // Display error.details.message to user
    console.error(`Error ${error.code}:`, error.details.message);
    return;
  }

  const data = await response.json();
  // Store conversation_id and display response
  localStorage.setItem('conversation_id', data.conversation_id);
  displayMessage(data.response);

} catch (error) {
  // Network error or JSON parse error
  console.error('Failed to send message:', error);
  displayError('Unable to connect to server. Please try again.');
}
```

### Error Codes

| Code | HTTP Status | Description | Retry? |
|------|-------------|-------------|--------|
| VALIDATION_ERROR | 400 | Invalid request parameters | No - Fix input |
| NOT_FOUND | 404 | Conversation doesn't exist | No - Start new conversation |
| INTERNAL_ERROR | 500 | Server-side processing error | Yes - After delay |
| DATABASE_ERROR | 500 | Database connectivity issue | Yes - After delay |

## Rate Limiting

**Status**: Not implemented in Phase III-C

Future phases may implement rate limiting. Response will include:
```json
{
  "error": "Too many requests",
  "code": "RATE_LIMIT_EXCEEDED",
  "details": {
    "retry_after": 60,
    "message": "Too many requests. Please wait 60 seconds."
  }
}
```

## Versioning

**Current Version**: v1 (implicit)

The API currently has no explicit versioning. Future versions will use URL path versioning:
- `/api/v1/{user_id}/chat`
- `/api/v2/{user_id}/chat`

## CORS Configuration

**Development**: Allow all origins (`*`)
**Production**: Restrict to frontend domain

```python
# FastAPI CORS middleware
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://frontend.example.com"],  # Or ["*"] for dev
    allow_credentials=True,
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["*"],
)
```

## Integration Guidelines

### Frontend Integration Checklist

- [ ] Install HTTP client (Axios or Fetch)
- [ ] Create chatApi.ts service module
- [ ] Implement conversation_id localStorage persistence
- [ ] Handle all error codes (VALIDATION_ERROR, NOT_FOUND, INTERNAL_ERROR)
- [ ] Display loading state while waiting for response
- [ ] Implement retry logic for 500 errors
- [ ] Show user-friendly error messages
- [ ] Test conversation continuation across page refreshes
- [ ] Verify stateless operation (restart server, continue conversation)

### Backend Integration Notes

- Endpoint already exists at `backend/src/api/chat_endpoint.py`
- Already integrated with AgentRunner from Phase III-B
- Already stores messages in ChatMessage and ChatResponse tables
- This phase focuses on ensuring conversation_id handling and frontend integration

## Testing

### Manual Test Scenarios

1. **New Conversation**:
   - POST without conversation_id
   - Verify new ID generated
   - Verify message stored

2. **Continue Conversation**:
   - POST with existing conversation_id
   - Verify history loaded
   - Verify context maintained

3. **Restart Resilience**:
   - Start conversation
   - Restart server
   - Continue conversation with same ID
   - Verify context preserved

4. **Error Cases**:
   - POST with invalid conversation_id → 404
   - POST with empty message → 400
   - POST with message >10,000 chars → 400
   - POST with invalid user_id format → 400

### Automated Test Examples

See `api-examples.md` for complete request/response examples with curl commands.

## References

- [OpenAPI 3.0 Specification](https://swagger.io/specification/)
- [REST API Best Practices](https://restfulapi.net/)
- [HTTP Status Codes](https://httpstatuses.com/)
- Phase III-B Implementation: `backend/src/api/chat_endpoint.py`
