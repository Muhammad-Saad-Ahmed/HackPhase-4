# Implementation Tasks: ChatKit Frontend

**Feature**: 003-chatkit-frontend | **Branch**: `003-chatkit-frontend` | **Date**: 2026-01-16

**Input**: Specification from [spec.md](spec.md), architecture from [plan.md](plan.md)

## Task Organization

Tasks organized by user story priority (P1-P5) with dependencies. Each task includes:
- **TaskID**: Unique identifier
- **Priority**: P1 (Critical) to P5 (Enhancement)
- **Story**: User story reference (US1-US5)
- **Description**: What to do and which file

## Phase 1: Setup & Initialization (Blocking Prerequisites)

- [X] [T001] [P1] [US1] Create Next.js project with TypeScript, Tailwind, and App Router at `frontend/`
  - Test: `npx create-next-app@latest frontend --typescript --tailwind --app` succeeds

- [X] [T002] [P1] [US1] Install core dependencies: ChatKit, Better Auth, SWR, axios
  - Test: `package.json` contains `@chatkit/react`, `better-auth`, `swr`, `axios`

- [X] [T003] [P1] [US1] Configure TypeScript in `tsconfig.json` with strict mode and path aliases
  - Test: `@/components`, `@/services` imports work without errors

- [X] [T004] [P1] [US1] Setup Tailwind CSS in `tailwind.config.js` with custom theme colors
  - Test: Tailwind utility classes work in components

- [X] [T005] [P1] [US1] Create environment variable template at `.env.example`
  - Test: Contains `NEXT_PUBLIC_API_URL`, `BETTER_AUTH_SECRET`, `BETTER_AUTH_URL`

- [X] [T006] [P1] [US1] Create `.env.local` with development configuration
  - Test: `NEXT_PUBLIC_API_URL=http://localhost:8000`, secrets not committed

- [X] [T007] [P1] [US1] Setup project directory structure: `src/{app,components,services,hooks,types,lib,styles}`
  - Test: All directories exist and are empty

## Phase 2: Foundational (Type System & API Layer)

- [X] [T008] [P1] [US1] Define TypeScript types for User Session in `src/types/auth.ts`
  - Test: `UserSession` interface has `user_id`, `email`, `session_token`, `expires_at`, `is_authenticated`

- [X] [T009] [P2] [US2] Define TypeScript types for Conversation in `src/types/chat.ts`
  - Test: `Conversation` interface matches data-model.md specification

- [X] [T010] [P2] [US2] Define TypeScript types for Message in `src/types/chat.ts`
  - Test: `Message` interface has `message_id`, `conversation_id`, `role`, `content`, `timestamp`, `tool_calls?`

- [X] [T011] [P4] [US4] Define TypeScript types for ToolCall in `src/types/chat.ts`
  - Test: `ToolCall` interface has `tool_name`, `parameters`, `result?`, `error?`, `confidence?`, `status`

- [X] [T012] [P2] [US2] Define TypeScript types for API requests/responses in `src/types/api.ts`
  - Test: `OrchestratorRequest` and `OrchestratorResponse` match contracts/frontend-api.yaml

- [X] [T013] [P5] [US5] Create API client wrapper in `src/services/api-client.ts`
  - Test: `ApiClient` class with `get()`, `post()`, `put()`, `delete()` methods

- [X] [T014] [P5] [US5] Implement auth header injection in API client
  - Test: All requests include `Authorization: Bearer ${token}` header (FR-007)

- [X] [T015] [P5] [US5] Implement retry logic in API client (max 3 retries, exponential backoff)
  - Test: Failed request retries 3 times before throwing error (FR-025)

- [X] [T016] [P5] [US5] Implement error handling in API client with typed error responses
  - Test: API errors return `ApiError` with `message`, `code`, `details` (FR-008)

- [X] [T017] [P1] [US1] Configure Better Auth in `src/lib/auth-config.ts`
  - Test: Better Auth configured with email/password provider, secret from env

- [X] [T018] [P1] [US1] Create environment config validator in `src/lib/api-config.ts`
  - Test: Missing `NEXT_PUBLIC_API_URL` throws error at build time

## Phase 3: User Story 1 - Authentication (P1)

- [X] [T019] [P1] [US1] Create Next.js middleware for session validation at `src/middleware.ts`
  - Test: Unauthenticated requests to `/chat` redirect to `/login` (FR-005, FR-017)

- [X] [T020] [P1] [US1] Create AuthContext provider in `src/hooks/useAuth.tsx`
  - Test: `AuthContextValue` has `session`, `login()`, `signup()`, `logout()`, `isLoading`, `error`

- [X] [T021] [P1] [US1] Implement `login()` function in auth service at `src/services/auth-service.ts`
  - Test: Successful login sets HTTP-only cookie and updates context (SC-001)

- [X] [T022] [P1] [US1] Implement `signup()` function in auth service
  - Test: Successful signup creates user and auto-logs in

- [X] [T023] [P1] [US1] Implement `logout()` function in auth service
  - Test: Logout clears session cookie and redirects to `/login` (FR-016)

- [X] [T024] [P1] [US1] Create LoginForm component at `src/components/auth/LoginForm.tsx`
  - Test: Form has email, password inputs and submit button with validation (FR-001)

- [X] [T025] [P1] [US1] Create SignupForm component at `src/components/auth/SignupForm.tsx`
  - Test: Form has email, password, confirm password inputs with validation

- [X] [T026] [P1] [US1] Create AuthGuard component at `src/components/auth/AuthGuard.tsx`
  - Test: Wraps dashboard pages, redirects to login if not authenticated

- [X] [T027] [P1] [US1] Create login page at `src/app/(auth)/login/page.tsx`
  - Test: Login page renders LoginForm, redirects to `/chat` on success

- [X] [T028] [P1] [US1] Create signup page at `src/app/(auth)/signup/page.tsx`
  - Test: Signup page renders SignupForm, redirects to `/chat` on success

- [X] [T029] [P1] [US1] Create root layout at `src/app/layout.tsx` with AuthContext provider
  - Test: All pages have access to auth context

- [X] [T030] [P1] [US1] Implement session persistence across refreshes
  - Test: Refreshing `/chat` page does not redirect to login if session valid (SC-007)

## Phase 4: User Story 2 - Chat Interface (P2)

- [ ] [T031] [P2] [US2] Create ChatContext provider in `src/hooks/useChat.ts`
  - Test: `ChatContextValue` has `currentConversation`, `messages`, `sendMessage()`, `isTyping`, `error`

- [ ] [T032] [P2] [US2] Create chat service at `src/services/chat-service.ts` with `sendMessage()` function
  - Test: `sendMessage()` calls `POST /api/v1/agents/orchestrator/invoke` (FR-006)

- [ ] [T033] [P2] [US2] Implement MessageBubble component at `src/components/chat/MessageBubble.tsx`
  - Test: Displays user/agent messages with avatar, timestamp, and styled differently (FR-015, FR-014)

- [ ] [T034] [P2] [US2] Implement MessageInput component at `src/components/chat/MessageInput.tsx`
  - Test: Text input with Send button, validates non-empty, max 5000 chars (FR-013)

- [ ] [T035] [P2] [US2] Implement MessageList component at `src/components/chat/MessageList.tsx`
  - Test: Renders list of MessageBubble components in chronological order (FR-003)

- [ ] [T036] [P2] [US2] Implement LoadingIndicator component at `src/components/chat/LoadingIndicator.tsx`
  - Test: Shows "AI is typing..." when `isTyping` is true (FR-011)

- [ ] [T037] [P2] [US2] Create chat page at `src/app/(dashboard)/chat/page.tsx`
  - Test: Renders MessageList, MessageInput, LoadingIndicator with ChatContext

- [ ] [T038] [P2] [US2] Implement markdown rendering in MessageBubble for AI responses
  - Test: AI messages render bold, italic, lists, code blocks correctly (FR-019)

- [ ] [T039] [P2] [US2] Implement optimistic UI updates in `sendMessage()`
  - Test: User message appears immediately in MessageList before API response (SC-002)

- [ ] [T040] [P2] [US2] Implement error handling in chat with user-friendly messages
  - Test: Network errors show "Connection failed, please retry" (FR-008)

- [ ] [T041] [P2] [US2] Implement auto-scroll to bottom when new messages arrive
  - Test: MessageList scrolls to latest message on send/receive

## Phase 5: User Story 3 - Conversation History (P3)

- [ ] [T042] [P3] [US3] Create conversation service at `src/services/conversation-service.ts`
  - Test: `getConversations()`, `createConversation()`, `getMessages()` functions implemented

- [ ] [T043] [P3] [US3] Create useConversation hook at `src/hooks/useConversation.ts` with SWR
  - Test: Hook fetches conversations with SWR, returns `data`, `error`, `isLoading`

- [ ] [T044] [P3] [US3] Create Sidebar component at `src/components/layout/Sidebar.tsx`
  - Test: Renders list of conversations with titles and timestamps (FR-010)

- [ ] [T045] [P3] [US3] Implement conversation switching in Sidebar
  - Test: Clicking conversation loads its messages in chat interface (FR-010)

- [ ] [T046] [P3] [US3] Implement "New Conversation" button in Sidebar
  - Test: Creates new conversation and switches to it (FR-010)

- [ ] [T047] [P3] [US3] Implement conversation history loading on login
  - Test: Conversations load within 2 seconds of login (SC-004, FR-009)

- [ ] [T048] [P3] [US3] Create Navbar component at `src/components/layout/Navbar.tsx`
  - Test: Shows user email and logout button

- [ ] [T049] [P3] [US3] Create dashboard layout at `src/app/(dashboard)/layout.tsx`
  - Test: Layout renders Navbar, Sidebar, and page content with AuthGuard

## Phase 6: User Story 4 - Tool Visualization (P4)

- [ ] [T050] [P4] [US4] Create ToolCallCard component at `src/components/chat/ToolCallCard.tsx`
  - Test: Displays tool name, status icon (✅/❌), expandable details section (FR-004)

- [ ] [T051] [P4] [US4] Implement collapsible UI for tool parameters and results
  - Test: Clicking "Show details" expands parameters and result (FR-020)

- [ ] [T052] [P4] [US4] Implement tool call rendering in MessageBubble
  - Test: Agent messages with `tool_calls` render ToolCallCard components (SC-006)

- [ ] [T053] [P4] [US4] Implement JSON formatting for tool parameters and results
  - Test: Large JSON objects display formatted with indentation

- [ ] [T054] [P4] [US4] Implement reasoning trace display in ToolCallCard
  - Test: Shows intent, entities, confidence from `reasoning_trace` (FR-021)

- [ ] [T055] [P4] [US4] Add timestamp to ToolCallCard
  - Test: Tool calls show execution timestamp (FR-014)

## Phase 7: User Story 5 - API Security (P5)

- [ ] [T056] [P5] [US5] Configure HTTPS-only mode in Next.js config
  - Test: Production build enforces HTTPS for all requests (FR-018, SC-005)

- [ ] [T057] [P5] [US5] Implement CORS handling in API client
  - Test: API requests include correct CORS headers (FR-023)

- [ ] [T058] [P5] [US5] Implement client-side error logging (without exposing to users)
  - Test: Errors logged to console in dev, sent to error service in prod (FR-024)

- [ ] [T059] [P5] [US5] Implement session expiration detection
  - Test: 401 responses clear session and redirect to login (FR-017)

- [ ] [T060] [P5] [US5] Remove console.log statements and sensitive data from production build
  - Test: Zero passwords/tokens in browser console, network tab, localStorage (SC-010)

## Phase 8: Polish & Cross-Cutting Concerns

- [ ] [T061] [P2] [US2] Implement mobile-responsive design with Tailwind breakpoints
  - Test: Chat interface works on 320px-1920px viewports (SC-008, FR-022)

- [ ] [T062] [P2] [US2] Add loading states for conversation switching
  - Test: Shows spinner while loading messages for selected conversation

- [ ] [T063] [P3] [US3] Implement auto-generated conversation titles from first message
  - Test: New conversation titled from first 50 chars of user message

- [ ] [T064] [P5] [US5] Add retry UI for failed messages
  - Test: Failed messages show "Retry" button (SC-009)

- [ ] [T065] [P1] [US1] Create landing page at `src/app/page.tsx`
  - Test: Redirects to `/chat` if authenticated, `/login` if not

- [ ] [T066] [P2] [US2] Add empty state UI for new conversations
  - Test: Empty chat shows "Start a conversation..." placeholder

- [ ] [T067] [P3] [US3] Add empty state UI for conversation list
  - Test: No conversations shows "No conversations yet. Start chatting!"

- [ ] [T068] [P5] [US5] Configure environment variables for Vercel deployment
  - Test: Vercel dashboard has `NEXT_PUBLIC_API_URL`, `BETTER_AUTH_SECRET` set

- [ ] [T069] [P5] [US5] Create deployment script at `scripts/deploy.sh`
  - Test: `vercel deploy --prod` succeeds and frontend is accessible via HTTPS

- [ ] [T070] [P5] [US5] Update frontend README.md with setup and deployment instructions
  - Test: Following README.md from scratch completes setup successfully

## Backend Extensions Required (Separate Feature)

**Note**: These backend tasks extend 001-reusable-agents and should be in a separate feature/branch:

- [ ] [T071] [P3] [US3] Create Conversation model in `backend/src/models/conversation.py`
  - Test: SQLModel table with `id`, `user_id`, `title`, `created_at`, `updated_at`

- [ ] [T072] [P3] [US3] Create ConversationMessage model in `backend/src/models/conversation.py`
  - Test: SQLModel table with `id`, `conversation_id`, `role`, `content`, `timestamp`, `tool_calls`

- [ ] [T073] [P3] [US3] Add `GET /api/v1/conversations` endpoint in `backend/src/api/routes.py`
  - Test: Returns list of conversations for authenticated user

- [ ] [T074] [P3] [US3] Add `POST /api/v1/conversations` endpoint in `backend/src/api/routes.py`
  - Test: Creates new conversation, returns conversation object

- [ ] [T075] [P3] [US3] Add `GET /api/v1/conversations/{id}/messages` endpoint in `backend/src/api/routes.py`
  - Test: Returns messages for conversation ID

## Testing Tasks

- [ ] [T076] [P2] [US2] Write unit tests for API client retry logic
  - Test: `api-client.test.ts` covers retry, timeout, error scenarios

- [ ] [T077] [P1] [US1] Write unit tests for auth service
  - Test: `auth-service.test.ts` covers login, signup, logout, session validation

- [ ] [T078] [P2] [US2] Write component tests for MessageBubble
  - Test: React Testing Library tests for user/agent message rendering

- [ ] [T079] [P4] [US4] Write component tests for ToolCallCard
  - Test: Tests for expand/collapse, success/failure states

- [ ] [T080] [P1] [US1] Write E2E test for login flow
  - Test: Playwright test: login → chat page → logout → login page

- [ ] [T081] [P2] [US2] Write E2E test for sending message
  - Test: Playwright test: type message → click send → see response

- [ ] [T082] [P3] [US3] Write E2E test for conversation switching
  - Test: Playwright test: create conversation → switch → messages load

## Task Summary

- **Total Tasks**: 82 (70 frontend + 5 backend + 7 tests)
- **P1 (Critical)**: 19 tasks (Authentication, Core Setup)
- **P2 (High)**: 15 tasks (Chat Interface, UI)
- **P3 (Medium)**: 12 tasks (Conversation History)
- **P4 (Low)**: 6 tasks (Tool Visualization)
- **P5 (Enhancement)**: 9 tasks (Security, Deployment)
- **Testing**: 7 tasks
- **Backend Extensions**: 5 tasks (separate feature recommended)

## Parallel Opportunities

**Phase 1 (Setup)**: Tasks T001-T007 can run sequentially (dependencies)

**Phase 2 (Foundational)**:
- Parallel Group A: T008, T009, T010, T011, T012 (type definitions - independent)
- Parallel Group B: T013-T016 (API client - depends on types)
- Parallel Group C: T017, T018 (config - independent)

**Phase 3 (Authentication)**:
- Parallel Group A: T019, T020, T021-T023 (auth logic - T019 blocks others)
- Parallel Group B: T024, T025, T026 (components - depends on auth logic)
- Parallel Group C: T027, T028, T029, T030 (pages - depends on components)

**Phase 4 (Chat Interface)**:
- Parallel Group A: T031, T032 (chat service)
- Parallel Group B: T033, T034, T035, T036 (components - independent)
- Sequential: T037-T041 (integration)

**Phase 5 (Conversation History)**:
- Sequential: T042 → T043 → T044-T046 (service → hook → UI)
- Parallel: T047, T048, T049 (independent features)

**Phase 6 (Tool Visualization)**:
- Sequential: T050 → T051 → T052 (component → features → integration)
- Parallel: T053, T054, T055 (independent enhancements)

**Phase 7 (Security)**:
- Parallel: T056, T057, T058, T059, T060 (all independent)

**Phase 8 (Polish)**:
- Parallel: T061, T062, T063, T064, T065, T066, T067 (UI tasks)
- Sequential: T068 → T069 → T070 (deployment)

**Testing**:
- All test tasks (T076-T082) can run in parallel after implementation

## MVP Scope Recommendation

**Minimum Viable Product (MVP)** - Phases 1-3 only:
- Tasks T001-T030 (30 tasks)
- Delivers: Authentication + Project Setup
- Success Criteria: SC-001, SC-007 (login in <30s, session persists)
- Time Estimate: Foundational work for subsequent features

**MVP + Core Chat** - Phases 1-4:
- Tasks T001-T041 (41 tasks)
- Delivers: Authentication + Chat Interface
- Success Criteria: SC-001, SC-002, SC-003, SC-007 (all core UX metrics)

**Feature Complete** - Phases 1-6:
- Tasks T001-T055 (55 tasks)
- Delivers: Authentication + Chat + History + Tool Visualization
- Success Criteria: SC-001 through SC-006 (all functional requirements)

**Production Ready** - All Phases:
- All 82 tasks
- Delivers: Full feature with security, testing, deployment
- Success Criteria: All SC-001 through SC-010

## Next Steps

1. Review tasks with stakeholders for priority adjustments
2. Begin Phase 1 (Setup) with `/sp.implement` workflow
3. Complete MVP (Phases 1-3) before expanding to chat interface
4. Create separate backend feature for T071-T075 (conversation models/endpoints)
5. Run `/sp.adr` for significant architectural decisions from research.md

## Acceptance Criteria

- [ ] All tasks have clear descriptions with file paths
- [ ] All tasks reference functional requirements (FR-XXX) or success criteria (SC-XXX)
- [ ] All tasks include testable acceptance tests
- [ ] Dependencies between tasks are documented
- [ ] Parallel opportunities are identified for efficiency
- [ ] MVP scope is clearly defined for incremental delivery
