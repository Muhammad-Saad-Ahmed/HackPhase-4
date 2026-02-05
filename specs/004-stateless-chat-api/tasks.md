# Tasks: Stateless Chat API & UI

**Input**: Design documents from `/specs/004-stateless-chat-api/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅, quickstart.md ✅

**Tests**: Not explicitly requested in specification. Focus on implementation and manual testing per quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story (MVP-first approach).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Project type**: Web application (backend + frontend)
- **Backend root**: `backend/src/`
- **Frontend root**: `frontend/src/`
- All tasks use absolute paths from repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize frontend project and verify backend readiness

**Duration Estimate**: ~1 hour

- [X] T001 Verify existing backend structure at backend/src/ contains models/, services/, api/, core/ from Phase III-B
- [X] T002 Verify ChatMessage, ChatResponse, ConversationMetadata models exist in backend/src/models/
- [X] T003 Verify AgentRunner service exists at backend/src/services/agent_runner.py
- [X] T004 Verify ConversationService exists at backend/src/services/conversation_service.py
- [X] T005 Verify chat endpoint exists at backend/src/api/chat_endpoint.py with POST /{user_id}/chat route
- [X] T006 Initialize React app with TypeScript: npx create-react-app frontend --template typescript (Next.js already set up)
- [X] T007 [P] Install frontend dependencies: npm install @chatscope/chat-ui-kit-react @chatscope/chat-ui-kit-styles axios
- [X] T008 [P] Create frontend directory structure: mkdir -p frontend/src/{components/Chat,services,types}
- [X] T009 Configure CORS in backend/src/main.py to allow http://localhost:3000 origin

**Checkpoint**: Environment ready - backend verified functional, frontend initialized

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Verify core infrastructure from Phase III-B is functional

**⚠️ CRITICAL**: These verifications must pass before user story implementation begins

- [ ] T010 Test backend server starts successfully: uv run uvicorn src.main:app --reload
- [ ] T011 Verify Swagger UI accessible at http://localhost:8000/docs shows chat endpoint
- [ ] T012 Test database connectivity by querying existing chat_message table
- [ ] T013 Verify conversation_id generation works (UUID v4 format) in conversation_service.py
- [ ] T014 Test AgentRunner processes simple message: "Hello" returns AI response
- [ ] T015 Verify conversation history loading retrieves messages ordered by timestamp ASC

**Checkpoint**: Foundation verified - all Phase III-B components functional

---

## Phase 3: User Story 1 - Resume Conversation After Server Restart (Priority: P1) 🎯 MVP

**Goal**: Enable conversations to survive server restarts with full context preservation

**Independent Test**: Start conversation, record conversation_id, restart server, send new message with same ID, verify AI maintains context

### Implementation for User Story 1

- [ ] T016 [P] [US1] Verify conversation_id handling in chat_endpoint.py accepts optional conversation_id parameter
- [ ] T017 [P] [US1] Verify conversation history loading in conversation_service.py loads all messages for given conversation_id
- [ ] T018 [P] [US1] Verify ConversationMetadata loading in conversation_service.py retrieves task_references
- [ ] T019 [US1] Test conversation persistence: Send 5 messages, verify all stored in database
- [ ] T020 [US1] Test restart resilience: Restart server via Ctrl+C and restart, verify conversations resume
- [ ] T021 [US1] Test metadata persistence: Create task references, restart server, verify references preserved
- [ ] T022 [US1] Add integration test script at backend/tests/integration/test_restart_resilience.sh

**Acceptance Validation**:
- conversation with 5 messages → restart server → send message #6 → AI demonstrates awareness of all 5 previous messages
- conversation from yesterday → multiple restarts → send new message → history loads correctly
- conversation with task references → restart between messages → task reference resolves correctly

**Checkpoint**: Restart resilience proven - conversations survive server restarts

---

## Phase 4: User Story 2 - Start New Conversation (Priority: P1) 🎯 MVP

**Goal**: Enable users to start fresh conversations without previous context

**Independent Test**: POST /chat without conversation_id, verify new ID generated and message stored

### Implementation for User Story 2

- [ ] T023 [P] [US2] Verify conversation_id generation in conversation_service.py when conversation_id is None
- [ ] T024 [P] [US2] Verify new conversation creates first ChatMessage row with generated conversation_id
- [ ] T025 [P] [US2] Verify new conversation creates first ChatResponse row with same conversation_id
- [ ] T026 [US2] Verify response returns generated conversation_id in JSON response
- [ ] T027 [US2] Test new conversation creation via curl: POST without conversation_id
- [ ] T028 [US2] Verify database contains both ChatMessage and ChatResponse rows for new conversation
- [ ] T029 [US2] Test conversation_id format validation: conv_[8 hex chars]

**Acceptance Validation**:
- POST without conversation_id → new conversation_id generated (format: conv_xxxxxxxx)
- new conversation → both user message and AI response stored with correct roles
- generated conversation_id → can be used in subsequent requests

**Checkpoint**: New conversation creation functional - users can start fresh chats

---

## Phase 5: User Story 3 - Continue Existing Conversation (Priority: P1) 🎯 MVP

**Goal**: Enable multi-turn conversations with context awareness

**Independent Test**: Create conversation, extract ID, send additional messages with ID, verify chronological order and context

### Implementation for User Story 3

- [ ] T030 [P] [US3] Verify conversation_id validation in chat_endpoint.py returns 404 for invalid IDs
- [ ] T031 [P] [US3] Verify message appending: new ChatMessage added to existing conversation
- [ ] T032 [P] [US3] Verify context loading: AgentRunner receives full conversation history
- [ ] T033 [US3] Verify AI maintains context: Response references earlier messages
- [ ] T034 [US3] Test continuing conversation: POST with existing conversation_id
- [ ] T035 [US3] Test invalid conversation_id: POST with non-existent ID returns 404
- [ ] T036 [US3] Test context awareness: Send "add task", then "what tasks", verify AI remembers
- [ ] T037 [US3] Verify message ordering: Query database shows messages in timestamp ASC order

**Acceptance Validation**:
- existing conversation_id → message appended to thread
- conversation with 10 messages → send #11 → AI reflects context from earlier messages
- invalid conversation_id → returns NOT_FOUND error with clear message

**Checkpoint**: Multi-turn conversations functional - users can continue existing chats with context

---

## Phase 6: User Story 4 - ChatKit Frontend Integration (Priority: P2)

**Goal**: Provide web-based chat UI for natural user interactions

**Independent Test**: Open UI, send messages, verify instant display, conversation_id management, and loading states

### Implementation for User Story 4

#### API Service Layer

- [X] T038 [P] [US4] Create chatApi.ts at frontend/src/services/chatApi.ts with sendMessage function using Axios
- [X] T039 [P] [US4] Create conversationStorage.ts at frontend/src/services/conversationStorage.ts for localStorage management
- [X] T040 [P] [US4] Create chat.types.ts at frontend/src/types/chat.types.ts with ChatMessage, ChatResponse interfaces

#### React Components

- [X] T041 [P] [US4] Create ChatContainer.tsx at frontend/src/components/Chat/ChatContainer.tsx (main wrapper)
- [X] T042 [P] [US4] Create MessageList.tsx (ChatKit built-in component used)
- [X] T043 [P] [US4] Create MessageInput.tsx (ChatKit built-in component used)
- [X] T044 [P] [US4] Create Message.tsx at frontend/src/components/Chat/Message.tsx (individual bubble)
- [X] T045 [P] [US4] Create LoadingSpinner.tsx at frontend/src/components/common/LoadingSpinner.tsx

#### State Management & Integration

- [X] T046 [US4] Implement React Context for conversation state in ChatContainer.tsx (useState used instead - simpler)
- [X] T047 [US4] Implement localStorage persistence: save/load conversation_id on mount/unmount
- [X] T048 [US4] Implement optimistic UI updates: show user message immediately before API call
- [X] T049 [US4] Implement error handling: display user-friendly messages for API errors
- [X] T050 [US4] Implement loading states: show typing indicator while waiting for AI response

#### App Integration

- [X] T051 [US4] Update App.tsx (Next.js: created chat page at src/app/chat/page.tsx)
- [X] T052 [US4] Import ChatKit styles in ChatContainer.tsx: @chatscope/chat-ui-kit-styles/dist/default/styles.min.css
- [X] T053 [US4] Configure Axios base URL in chatApi.ts: http://localhost:8000/api (via env var)
- [X] T054 [US4] Add user_id configuration (hardcode "demo-user" for MVP)

#### Testing & Polish

- [ ] T055 [US4] Test frontend starts successfully: npm start opens http://localhost:3000
- [ ] T056 [US4] Test message sending: type message, click send, verify appears in UI
- [ ] T057 [US4] Test AI response display: verify response appears after API call completes
- [ ] T058 [US4] Test conversation persistence: refresh page (F5), verify conversation_id loaded from localStorage
- [ ] T059 [US4] Test error handling: disconnect backend, send message, verify error message displayed
- [ ] T060 [US4] Style chat UI with ChatKit themes for user/assistant message distinction

**Acceptance Validation**:
- ChatKit UI loads → type message → click send → message appears with loading indicator
- AI response received → appears in chat with assistant avatar and formatting
- close browser → reopen → conversation history loaded and displayed
- type message → press Enter or click Send → API called with correct conversation_id and user_id

**Checkpoint**: ChatKit frontend functional - users can interact via web UI

---

## Phase 7: Integration & End-to-End Testing

**Purpose**: Verify full stack integration and edge case handling

- [ ] T061 Test complete flow: Open frontend → send "Hello" → verify response → send "add task" → verify task created
- [ ] T062 Test restart during conversation: Start conversation in UI → restart backend → continue in UI → verify context preserved
- [ ] T063 Test concurrent requests: Open 2 browser tabs → send messages from both → verify no data corruption
- [ ] T064 Test empty message validation: Try sending empty message → verify frontend prevents or backend returns 400
- [ ] T065 Test long message handling: Send 10,000 character message → verify accepted and displayed
- [ ] T066 Test conversation_id format validation: Send invalid ID via curl → verify 404 with clear error
- [ ] T067 Test database unavailable scenario: Stop database → send message → verify 503 error with retry message
- [ ] T068 Test network timeout: Simulate slow API → verify frontend shows appropriate loading state
- [ ] T069 Verify CORS working: Check browser console for CORS errors (should be none)
- [ ] T070 Verify localStorage quota: Create 100 conversations → verify only conversation_id stored (not full history)

**Checkpoint**: Full integration verified - all user stories working end-to-end

---

## Phase 8: Documentation & Polish

**Purpose**: Finalize documentation and production readiness

- [ ] T071 Update quickstart.md with any implementation changes or gotchas discovered
- [ ] T072 Add comments to complex frontend components (ChatContainer, API adapter)
- [ ] T073 Add JSDoc to chatApi.ts functions with parameter descriptions
- [ ] T074 Verify all error messages are user-friendly (no stack traces or technical jargon)
- [X] T075 Add README.md in frontend/ directory with setup instructions
- [ ] T076 Document localStorage schema in conversationStorage.ts comments
- [ ] T077 Add inline comments for conversation_id generation logic in conversation_service.py
- [ ] T078 Create production deployment checklist in specs/004-stateless-chat-api/deployment.md
- [ ] T079 Verify all frontend components have proper TypeScript types (no `any` types)
- [ ] T080 Run final integration test following quickstart.md instructions

**Checkpoint**: Documentation complete - feature ready for handoff

---

## Dependencies Between User Stories

**Visualization**:
```
Setup (Phase 1)
  ↓
Foundational (Phase 2: Verification)
  ↓
  ├─→ User Story 1 (Resume After Restart) ────────┐
  ├─→ User Story 2 (Start New Conversation) ──────┤─→ Can execute in parallel (independent)
  └─→ User Story 3 (Continue Conversation) ───────┘
       ↓
  User Story 4 (ChatKit Frontend)
       ↓
  Integration & End-to-End Testing (Phase 7)
```

**Story Dependencies**:
- **User Story 1** (Resume): No dependencies on other stories. Tests restart resilience.
- **User Story 2** (Start New): No dependencies on other stories. Tests conversation creation.
- **User Story 3** (Continue): No dependencies on other stories. Tests multi-turn context.
- **User Story 4** (Frontend): No dependencies on other stories. Tests UI integration independently.

**Implementation Order**: US1/US2/US3 (parallel) → US4 → Integration

---

## Parallel Execution Examples

### Scenario 1: Single Developer (Sequential MVP)
1. Complete Phase 1-2 (Setup + Verification)
2. Test User Story 1 (Restart Resilience) - **Core MVP** ✅
3. Test User Story 2 (New Conversation) - **Core MVP** ✅
4. Test User Story 3 (Continue Conversation) - **Core MVP** ✅
5. Implement User Story 4 (ChatKit Frontend) - **UI Layer** ✅
6. Complete Phase 7-8 (Integration + Documentation)

### Scenario 2: Team of 4 Developers (Parallel)
After Phase 2 completes:
- Dev 1: User Story 1 (T016-T022) - Restart resilience testing
- Dev 2: User Story 2 (T023-T029) - New conversation testing
- Dev 3: User Story 3 (T030-T037) - Continue conversation testing
- Dev 4: User Story 4 (T038-T060) - Frontend implementation

All stories can run in parallel since they test different aspects of the same backend. Frontend (US4) can start after backend verification completes.

### Scenario 3: Two-Phase Delivery
**Phase A (Backend MVP)**: Test US1 + US2 + US3 via curl → Verify API functional
**Phase B (Frontend)**: Implement US4 → Deploy full-stack application

---

## Implementation Strategy

### MVP-First Approach (Recommended)

**MVP Definition**: User Story 1 + User Story 2 + User Story 3 (Backend API verification)

**Rationale**:
- US1 proves core value prop (restart resilience)
- US2 proves conversation creation works
- US3 proves multi-turn context works
- US4 (Frontend) is enhancement on top of working API
- Together they provide complete stateless API validation

**MVP Task Sequence**:
1. Phase 1: Setup (T001-T009) - ~1 hour
2. Phase 2: Foundational (T010-T015) - ~30 minutes
3. Phase 3: User Story 1 (T016-T022) - ~1 hour
4. Phase 4: User Story 2 (T023-T029) - ~30 minutes
5. Phase 5: User Story 3 (T030-T037) - ~1 hour
6. Phase 6: User Story 4 (T038-T060) - ~4 hours
7. Phase 7-8: Integration (T061-T080) - ~2 hours

**Total MVP Tasks**: 80 tasks
**Estimated MVP Duration**: 1-2 days for experienced developer

### Incremental Delivery

After MVP deployment, enhance with:
- **Iteration 2**: Performance optimization (pagination for long conversations)
- **Iteration 3**: Advanced error handling (retry logic, circuit breakers)
- **Iteration 4**: Production features (authentication, rate limiting, monitoring)

Each iteration is independently testable and deployable.

---

## Task Summary

**Total Tasks**: 80 tasks
- Phase 1 (Setup): 9 tasks
- Phase 2 (Foundational): 6 tasks
- Phase 3 (User Story 1 - P1): 7 tasks
- Phase 4 (User Story 2 - P1): 7 tasks
- Phase 5 (User Story 3 - P1): 8 tasks
- Phase 6 (User Story 4 - P2): 23 tasks
- Phase 7 (Integration): 10 tasks
- Phase 8 (Documentation): 10 tasks

**Parallel Opportunities**: 40 tasks marked with [P] can run in parallel

**Story Distribution**:
- User Story 1 (Resume After Restart): 7 verification/test tasks
- User Story 2 (Start New Conversation): 7 verification/test tasks
- User Story 3 (Continue Conversation): 8 verification/test tasks
- User Story 4 (ChatKit Frontend): 23 implementation tasks

**Independent Test Criteria** (per story):
- US1: Start conversation, restart server, continue conversation, verify context preserved
- US2: POST without conversation_id, verify new ID generated and messages stored
- US3: POST with existing conversation_id, verify message appended and context maintained
- US4: Open UI, send messages, verify display/persistence/error handling

**MVP Scope**: User Story 1 + User Story 2 + User Story 3 + User Story 4 (Backend verification + Frontend implementation = 45 core tasks)

---

## Validation Checklist

Before marking feature complete, verify:

- [ ] Backend server starts without errors
- [ ] Swagger UI shows chat endpoint documentation
- [ ] Database contains ChatMessage, ChatResponse, ConversationMetadata tables
- [ ] New conversation generates unique conversation_id (format: conv_xxxxxxxx)
- [ ] Existing conversation loads full history ordered by timestamp
- [ ] Restart server → conversation continues without data loss
- [ ] ConversationMetadata preserves task_references across restarts
- [ ] Frontend displays at http://localhost:3000
- [ ] User messages appear instantly in UI
- [ ] AI responses appear after API call completes
- [ ] Refresh page preserves conversation_id in localStorage
- [ ] Invalid conversation_id returns 404 with clear error message
- [ ] Empty message validation works (frontend or backend)
- [ ] CORS configured correctly (no console errors)
- [ ] Error handling displays user-friendly messages
- [ ] All TypeScript types defined (no `any` types)
- [ ] All critical functions have JSDoc comments
- [ ] quickstart.md instructions work end-to-end
- [ ] Performance meets targets (<3s new conversation, <1s history load)
- [ ] 100+ concurrent requests handled without corruption

---

## Notes

- **Backend already functional**: Most backend code exists from Phase III-B; this phase focuses on verification and frontend
- **No new database schema**: All tables (ChatMessage, ChatResponse, ConversationMetadata) already exist
- **Frontend is new work**: React + ChatKit integration is the primary development effort
- **Stateless architecture**: Proven by restart resilience testing
- **Manual testing focus**: No automated test suite requested; use quickstart.md for validation
- **localStorage for persistence**: Simple, effective for MVP (no backend session management)
- **UUID v4 for conversation_id**: Collision-resistant, stateless generation
- **ChatKit for UI**: Production-ready components, minimal custom styling needed

---

**Generated**: 2026-01-26
**Branch**: `004-stateless-chat-api`
**Ready for**: `/sp.implement` (task execution)
