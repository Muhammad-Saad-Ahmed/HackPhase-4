# Implementation Plan: Stateless Chat API & UI

**Branch**: `004-stateless-chat-api` | **Date**: 2026-01-26 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-stateless-chat-api/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

**Primary Requirement**: Expose a stateless REST API at `POST /api/{user_id}/chat` that persists conversation history to PostgreSQL and reconstructs conversation context on each request, enabling conversations to survive server restarts. Integrate with ChatKit-based frontend for real-time chat UI.

**Technical Approach**:
- Extend existing FastAPI chat endpoint (already present from Phase III-B) to handle conversation persistence
- Leverage existing ChatMessage, ChatResponse, and ConversationMetadata models
- Use AgentRunner service (Phase III-B) for AI message processing
- Implement conversation ID generation using UUID v4 for collision resistance
- Load full conversation history from database on each request to rebuild agent context
- Build React + ChatKit frontend with localStorage for conversation ID management
- Ensure zero server-side session state - all context reconstructed from database

## Technical Context

**Language/Version**: Python 3.11+ (backend), JavaScript/TypeScript (frontend)
**Primary Dependencies**:
- Backend: FastAPI, SQLModel, uvicorn, OpenAI Agents SDK (already integrated in Phase III-B)
- Frontend: React 18+, ChatKit, Axios/Fetch
**Storage**: Neon PostgreSQL (existing schema: ChatMessage, ChatResponse, ConversationMetadata tables)
**Testing**: pytest (backend), Jest/React Testing Library (frontend)
**Target Platform**: Linux server (backend), Modern web browsers (frontend)
**Project Type**: Web application (backend + frontend)
**Performance Goals**:
- <3s response time for new conversations under normal load
- <1s to load conversation history with 50 messages
- Support 100+ concurrent conversation requests
- <100ms frontend message rendering latency
**Constraints**:
- Zero server-side session state (stateless architecture per Constitution Principle IV)
- Database as single source of truth (Constitution Principle V)
- All agent interactions via MCP tools (Constitution Principle VI)
- Conversation history must persist across server restarts (Constitution Principle XV)
**Scale/Scope**:
- Support conversations with 1000+ messages
- Handle 10,000+ conversations per day
- Single-page React frontend with ChatKit integration
- Reuse existing backend/src structure from Phases III-A and III-B

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Compliance Analysis

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. Spec-Driven Development | ✅ PASS | Complete spec.md exists with requirements, user stories, success criteria |
| II. AI-Generated Code Only | ✅ PASS | All code will be AI-generated through specified workflows |
| III. Reusable Intelligence | ✅ PASS | Reuses AgentRunner from Phase III-B, extensible chat endpoint pattern |
| IV. Stateless Backend Architecture | ✅ PASS | No server-side sessions; conversation rebuilt from DB each request |
| V. Database as Single Source of Truth | ✅ PASS | All state (messages, metadata) in Neon PostgreSQL |
| VI. MCP-Only Agent Interactions | ✅ PASS | AgentRunner uses MCPTaskExecutor for all tool calls |
| VII. Official MCP SDK Mandate | ✅ PASS | Existing Phase III-A implementation uses official MCP SDK |
| VIII. OpenAI Agents SDK Requirement | ✅ PASS | Phase III-B integrated OpenAI Agents SDK |
| IX. FastAPI Backend Framework | ✅ PASS | Existing FastAPI backend extended with chat endpoint |
| X. SQLModel ORM Requirement | ✅ PASS | ChatMessage, ChatResponse models use SQLModel |
| XI. ChatKit Frontend Framework | ✅ PASS | Frontend will use ChatKit for chat UI components |
| XII. Better Auth Authentication | ⚠️ DEFERRED | Auth explicitly out of scope per spec; user_id provided by caller |
| XIII. Tool Chaining Support | ✅ PASS | AgentRunner supports multi-turn flows with task references |
| XIV. Graceful Error Handling | ✅ PASS | Spec requires structured error responses, frontend error handling |
| XV. Restart Resilience | ✅ PASS | Core requirement - conversations survive restarts |
| XVI. No Hardcoded Business Logic | ✅ PASS | Agent-driven logic via AgentRunner, no hardcoded responses |

### Gate Decision

**STATUS**: ✅ **PASS** - All applicable principles satisfied

**Justification for XII (Better Auth Deferred)**:
Per spec FR-019 and "Out of Scope" section, authentication is explicitly excluded from this phase. The user_id parameter is provided by the calling system (authenticated upstream). Better Auth integration is planned for future phase but not required for Phase III-C MVP.

**No constitution violations** - proceed to Phase 0 research.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/                      # SQLModel entities (EXISTING)
│   │   ├── chat_message.py         # User messages (EXISTING)
│   │   ├── chat_response.py        # AI responses (EXISTING)
│   │   ├── conversation_metadata.py # Task references, context (EXISTING)
│   │   └── task.py                 # Task entity (EXISTING)
│   ├── services/                   # Business logic services (EXISTING)
│   │   ├── agent_runner.py         # AI orchestration (EXISTING from Phase III-B)
│   │   ├── conversation_service.py # Conversation CRUD (EXISTING)
│   │   └── [other existing services]
│   ├── api/                        # FastAPI endpoints (EXISTING)
│   │   ├── chat_endpoint.py        # POST /api/{user_id}/chat (EXISTING, will extend)
│   │   └── [other existing endpoints]
│   ├── core/                       # Core utilities (EXISTING)
│   │   ├── config.py               # Settings (EXISTING)
│   │   ├── database.py             # DB connection (EXISTING)
│   │   └── logging.py              # Logging setup (EXISTING)
│   └── main.py                     # FastAPI app entry (EXISTING)
└── tests/
    ├── integration/                # API integration tests (NEW)
    │   └── test_chat_persistence.py
    └── unit/                       # Unit tests (EXISTING)

frontend/                           # NEW - Phase III-C addition
├── public/
│   └── index.html
├── src/
│   ├── components/                 # React components
│   │   ├── Chat/
│   │   │   ├── ChatContainer.tsx   # Main chat wrapper
│   │   │   ├── MessageList.tsx     # Message history display
│   │   │   ├── MessageInput.tsx    # Input field + send button
│   │   │   └── Message.tsx         # Individual message bubble
│   │   └── common/
│   │       └── LoadingSpinner.tsx
│   ├── services/                   # API communication
│   │   ├── chatApi.ts              # Axios/Fetch chat API calls
│   │   └── conversationStorage.ts  # localStorage for conversation_id
│   ├── types/                      # TypeScript types
│   │   └── chat.types.ts
│   ├── App.tsx                     # Root component
│   └── index.tsx                   # React entry point
├── package.json
└── tsconfig.json
```

**Structure Decision**: Web application structure (Option 2) selected. Backend structure already exists from Phases III-A and III-B - this phase adds frontend/ directory and extends existing chat_endpoint.py. No backend restructuring needed; all changes are additions or extensions to existing files.

## Complexity Tracking

> **No violations detected** - this section is not applicable.

All constitution principles are satisfied. No complexity justification required.

## Architecture Decisions

### Decision 1: Conversation ID Generation Strategy

**Choice**: UUID v4 with conv_ prefix, truncated to 8 hex characters

**Rationale**: Provides 4.3 billion unique IDs, stateless generation, negligible collision probability

**Alternatives**: Full UUID (too long), auto-increment (not stateless), timestamp-based (collision risk)

### Decision 2: Frontend State Management

**Choice**: React Context API + useState

**Rationale**: Simple state needs, no Redux boilerplate, sufficient for chat app

**Alternatives**: Redux (overkill), MobX (unnecessary complexity)

### Decision 3: ChatKit Integration Pattern

**Choice**: Custom API adapter layer between backend and ChatKit

**Rationale**: Decouples backend from frontend library, flexible for changes

**Alternatives**: Direct binding (tight coupling)

## Implementation Strategy

**Backend Changes**: Minimal - verify existing functionality
**Frontend Development**: New React app with ChatKit integration
**Total Tasks**: ~20 tasks (setup, verification, components, integration)

## Validation Strategy

**Acceptance Tests**:
- Resume conversation after server restart
- Start new conversation without conversation_id
- Continue existing conversation with context
- ChatKit UI displays messages correctly

**Performance Tests**:
- Conversation history loads <1s for 50 messages
- Frontend renders user messages <100ms
- Support 100+ concurrent requests

## Status

**Planning**: Complete
**Ready for**: /sp.tasks command
**Estimated Complexity**: Low-Medium
**Estimated Timeline**: 2-3 days for MVP
