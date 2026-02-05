---
id: 002
title: stateless-chat-api-plan
stage: plan
date: 2026-01-26
surface: agent
model: claude-sonnet-4-5
feature: 004-stateless-chat-api
branch: 004-stateless-chat-api
user: developer
command: /sp.plan
labels: ["architecture", "planning", "design", "api"]
links:
  spec: specs/004-stateless-chat-api/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/004-stateless-chat-api/plan.md
 - specs/004-stateless-chat-api/research.md
 - specs/004-stateless-chat-api/data-model.md
 - specs/004-stateless-chat-api/contracts/README.md
 - specs/004-stateless-chat-api/quickstart.md
tests:
 - none (planning phase)
---

## Prompt

/sp.plan Phase III-C Plan

Create:
- Chat endpoint request/response flow
- Conversation reconstruction logic
- ChatKit frontend wiring

Decisions:
- Conversation ID generation strategy
- Message ordering and pagination

Validation:
- Restart server → conversation continues
- ChatKit UI works end-to-end

## Response snapshot

Created comprehensive architectural plan for stateless chat API with ChatKit frontend integration:

**Phase 0: Research** (research.md)
- Conversation ID generation: UUID v4 truncated to 8 chars (conv_xxxxxxxx)
- Message ordering: Timestamp ASC with optional pagination
- ChatKit integration: Custom API adapter pattern
- Conversation reconstruction: Full history reload per request
- Stateless design: Pure request-response with DB persistence
- Frontend state: React Context + useState

**Phase 1: Design & Contracts**
- data-model.md: All entities already exist from Phase III-B (ChatMessage, ChatResponse, ConversationMetadata)
- contracts/README.md: POST /api/{user_id}/chat contract with examples
- quickstart.md: 10-minute setup guide with curl tests and React integration

**Constitution Check**: ✅ ALL PASS (15/16 applicable)
- Principle XII (Better Auth) deferred per spec (auth out of scope)
- All other principles satisfied (stateless, DB persistence, MCP tools, FastAPI, SQLModel, ChatKit)

**Architecture Decisions**:
1. UUID v4 with conv_ prefix → 4.3B unique IDs, stateless
2. Separate ChatMessage/ChatResponse tables → already exists, no migration
3. Full history loading → meets <1s target for 50 messages
4. React Context + useState → simple, sufficient for chat
5. ChatKit adapter layer → decouples backend from frontend library
6. localStorage persistence → survives page refreshes

**Implementation Strategy**:
- Backend: Minimal changes (verify existing functionality)
- Frontend: New React app with ChatKit + TypeScript
- Total: ~20 tasks (setup, verification, components, integration)
- MVP Timeline: 2-3 days

**Key Insights**:
- Backend already 90% complete from Phase III-B
- This phase primarily frontend development
- No database schema changes needed
- Existing chat endpoint confirmed functional
- Focus on ChatKit integration and stateless validation

## Outcome

- ✅ Impact: Complete architectural plan ready for task generation
- 🧪 Tests: Validation strategy defined (restart resilience, performance benchmarks)
- 📁 Files: 5 files created (plan.md, research.md, data-model.md, contracts/README.md, quickstart.md)
- 🔁 Next prompts: /sp.tasks (generate detailed task breakdown), /sp.implement (execute tasks)
- 🧠 Reflection: Planning phase successfully leveraged existing Phase III-B infrastructure. Minimal backend changes required - primary effort is frontend ChatKit integration. All architecture decisions documented with rationale and alternatives.

## Evaluation notes (flywheel)

- Failure modes observed: None - existing infrastructure well-documented and functional
- Graders run and results (PASS/FAIL): Constitution check - 15/16 PASS (1 deferred per spec)
- Prompt variant (if applicable): Standard /sp.plan workflow
- Next experiment (smallest change to try): None needed - plan complete and ready for tasks
