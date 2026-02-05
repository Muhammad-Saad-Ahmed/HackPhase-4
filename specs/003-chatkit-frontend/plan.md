# Implementation Plan: ChatKit Frontend with Better Auth

**Branch**: `003-chatkit-frontend` | **Date**: 2026-01-16 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/003-chatkit-frontend/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Deploy a production-ready ChatKit frontend with Better Auth authentication, conversation history persistence, tool call visualization, and secure API integration. The frontend is a Next.js application using ChatKit UI components, connecting to the backend orchestrator agent API from 001-reusable-agents, with Better Auth for session management.

**Technical Approach**: Build a Next.js application with App Router, ChatKit React components for chat interface, Better Auth wrapper for authentication, API service layer for backend communication, and environment-based configuration for deployment flexibility. Deploy to Vercel with domain allowlisting and secure environment variable injection.

## Technical Context

**Language/Version**: TypeScript 5.0+, Node.js 18+ (LTS)
**Primary Dependencies**:
- Next.js 14+ (React framework with App Router)
- ChatKit (React UI components for chat interface)
- Better Auth (authentication library)
- React 18+ (UI framework)
- TypeScript 5.0+ (type safety)
- Tailwind CSS 3.4+ (styling)
- Axios or fetch (HTTP client for API requests)
- SWR or React Query (data fetching and caching)

**Storage**: Browser sessionStorage/localStorage for session tokens (HTTP-only cookies preferred), backend database for conversation data
**Testing**: Jest for unit tests, React Testing Library for component tests, Playwright or Cypress for E2E tests
**Target Platform**: Web browsers (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+), mobile browsers (iOS Safari 14+, Android Chrome 90+)
**Project Type**: Web frontend (Next.js application)
**Performance Goals**:
- Initial page load <2 seconds (SC-004)
- Message display <100ms (SC-002)
- API response rendering <3 seconds (SC-003)
- Mobile responsive 320px-1920px (SC-008)

**Constraints**:
- HTTPS only in production (SC-005, FR-018)
- Auth tokens in headers, never in URLs (FR-007)
- Zero sensitive data exposure in console/localStorage (SC-010)
- Session persistence across refreshes (SC-007)
- 90% error recovery success rate (SC-009)

**Scale/Scope**:
- 5 pages (login, signup, chat, conversation list, profile/logout)
- 25 functional requirements (FR-001 to FR-025)
- 10 success criteria (SC-001 to SC-010)
- 4 key entities (User Session, Conversation, Message, Tool Call)
- Single domain deployment (Vercel or GitHub Pages)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Spec-Driven Development | ✅ PASS | spec.md complete, plan.md in progress, tasks.md follows |
| II. AI-Generated Code Only | ✅ PASS | All code generated via /sp.implement workflow |
| III. Reusable Intelligence | ✅ PASS | Frontend consumes reusable agents via API (001-reusable-agents) |
| IV. Stateless Backend Architecture | ✅ PASS | Frontend is stateless (session in cookies), backend already stateless |
| V. Database as Single Source of Truth | ✅ PASS | Conversation data in backend database, frontend is presentation layer |
| VI. MCP-Only Agent Interactions | ✅ PASS | Frontend calls orchestrator API, which uses MCP internally |
| VII. Official MCP SDK Mandate | ✅ PASS | Frontend doesn't interact with MCP directly (backend handles) |
| VIII. OpenAI Agents SDK Requirement | ✅ PASS | Backend uses OpenAI Agents SDK (001), frontend consumes results |
| IX. FastAPI Backend Framework | ✅ PASS | Backend uses FastAPI (001), frontend calls FastAPI endpoints |
| X. SQLModel ORM Requirement | ✅ PASS | Backend uses SQLModel (001), frontend receives JSON responses |
| XI. ChatKit Frontend Framework | ✅ PASS | Using ChatKit as mandated for chat UI components |
| XII. Better Auth Authentication | ✅ PASS | Using Better Auth as mandated for authentication |
| XIII. Tool Chaining Support | ✅ PASS | Frontend visualizes tool chains from orchestrator responses |
| XIV. Graceful Error Handling | ✅ PASS | FR-008, FR-017, FR-024, FR-025 define error handling requirements |
| XV. Restart Resilience | ✅ PASS | Frontend session persists via cookies, survives page refreshes |
| XVI. No Hardcoded Business Logic | ✅ PASS | Frontend is presentation layer, business logic in backend |

**Summary**: 16/16 PASS. All constitution principles satisfied. ChatKit (XI) and Better Auth (XII) requirements met.

## Project Structure

### Documentation (this feature)

```text
specs/003-chatkit-frontend/
├── plan.md              # This file (/sp.plan command output)
├── spec.md              # Feature specification (already complete)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
│   ├── api-client.yaml  # Frontend API client interface
│   └── component-props.yaml  # ChatKit component prop types
├── checklists/          # Quality validation
│   └── requirements.md  # Spec quality checklist (already complete)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

New `frontend/` directory created:

```text
frontend/
├── src/
│   ├── app/                    # Next.js App Router pages
│   │   ├── (auth)/            # Auth layout group
│   │   │   ├── login/         # Login page
│   │   │   └── signup/        # Signup page
│   │   ├── (dashboard)/       # Authenticated layout group
│   │   │   ├── chat/          # Main chat interface
│   │   │   ├── conversations/ # Conversation list
│   │   │   └── profile/       # User profile/logout
│   │   ├── layout.tsx         # Root layout
│   │   └── page.tsx           # Landing page (redirects to login/chat)
│   ├── components/
│   │   ├── chat/              # Chat interface components
│   │   │   ├── MessageList.tsx
│   │   │   ├── MessageBubble.tsx
│   │   │   ├── MessageInput.tsx
│   │   │   ├── ToolCallCard.tsx
│   │   │   └── LoadingIndicator.tsx
│   │   ├── auth/              # Authentication components
│   │   │   ├── LoginForm.tsx
│   │   │   ├── SignupForm.tsx
│   │   │   └── AuthGuard.tsx
│   │   └── layout/            # Layout components
│   │       ├── Navbar.tsx
│   │       └── Sidebar.tsx
│   ├── services/              # API service layer
│   │   ├── api-client.ts      # HTTP client wrapper
│   │   ├── auth-service.ts    # Better Auth integration
│   │   ├── chat-service.ts    # Chat API calls
│   │   └── conversation-service.ts  # Conversation history API
│   ├── hooks/                 # React custom hooks
│   │   ├── useAuth.ts         # Authentication hook
│   │   ├── useChat.ts         # Chat state hook
│   │   └── useConversation.ts # Conversation hook
│   ├── types/                 # TypeScript types
│   │   ├── api.ts             # API response types
│   │   ├── auth.ts            # Auth types
│   │   └── chat.ts            # Chat/message types
│   ├── lib/                   # Utility functions
│   │   ├── auth-config.ts     # Better Auth configuration
│   │   └── api-config.ts      # API base URL configuration
│   └── styles/
│       └── globals.css        # Global styles (Tailwind)
├── public/
│   └── assets/                # Static assets
├── tests/
│   ├── unit/                  # Unit tests (Jest)
│   ├── integration/           # Integration tests
│   └── e2e/                   # E2E tests (Playwright)
├── .env.example               # Environment variables template
├── .env.local                 # Local development env (gitignored)
├── next.config.js             # Next.js configuration
├── tailwind.config.js         # Tailwind CSS configuration
├── tsconfig.json              # TypeScript configuration
├── package.json               # Dependencies
└── README.md                  # Frontend setup instructions

backend/  # Existing from 001 and 002
├── src/
│   ├── models/
│   │   └── conversation.py    # NEW: Conversation and Message models
│   ├── api/
│   │   └── routes.py          # EXTEND: Add conversation endpoints
│   └── ...
```

**Structure Decision**: Web application structure (Option 2) selected. Frontend is separate Next.js project in `frontend/` directory alongside existing `backend/`. This separation enables independent deployment (frontend to Vercel, backend to server) and follows modern JAMstack architecture. Frontend uses Next.js App Router (not Pages Router) for better performance and developer experience.

## Complexity Tracking

No complexity violations requiring justification. All design decisions align with constitution principles.
