---
id: 002
title: ChatKit Frontend Planning
stage: plan
date: 2026-01-16
surface: agent
model: claude-sonnet-4-5
feature: 003-chatkit-frontend
branch: 003-chatkit-frontend
user: Admin
command: /sp.plan
labels: ["planning", "chatkit", "nextjs", "better-auth", "frontend-architecture", "deployment"]
links:
  spec: specs/003-chatkit-frontend/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/003-chatkit-frontend/plan.md
  - specs/003-chatkit-frontend/research.md
  - specs/003-chatkit-frontend/data-model.md
  - specs/003-chatkit-frontend/quickstart.md
  - specs/003-chatkit-frontend/contracts/frontend-api.yaml
tests:
  - No tests (planning phase)
---

## Prompt

```
/sp.plan

Frontend architecture:
- Next.js application
- ChatKit UI layer
- API service abstraction
- Auth wrapper
- Environment-based configuration

Deployment plan:
- Deploy to Vercel or GitHub Pages
- Configure domain allowlist
- Inject domain key securely
```

## Response snapshot

Created comprehensive implementation plan for ChatKit Frontend with Better Auth, documenting Next.js architecture, deployment strategy, and API integration patterns.

**Planning Artifacts Generated:**

1. **plan.md**: Implementation plan with technical context, constitution check (16/16 PASS), project structure showing new `frontend/` directory with Next.js App Router layout

2. **research.md**: 10 major architecture decisions:
   - Decision 1: Next.js 14 App Router (vs CRA, Vite)
   - Decision 2: SWR + React Context for state management (vs Redux)
   - Decision 3: Better Auth with Next.js middleware (server-side validation)
   - Decision 4: Custom API client wrapper over fetch (type-safe, retry logic)
   - Decision 5: Backend database storage for conversations (vs frontend-only)
   - Decision 6: Custom tool call card UI (vs JSON viewer library)
   - Decision 7: Vercel deployment (vs GitHub Pages) - supports SSR, env vars
   - Decision 8: Hybrid ChatKit integration (direct + wrapped components)
   - Decision 9: Mobile-first responsive design with Tailwind
   - Decision 10: .env files with TypeScript schema validation

3. **data-model.md**: TypeScript types and interfaces:
   - UserSession, Conversation, Message, ToolCall types
   - API request/response interfaces (OrchestratorRequest/Response)
   - React Context state types (AuthContextValue, ChatContextValue)
   - Component prop interfaces
   - Validation rules and error types
   - Backend model extensions needed (Conversation, ConversationMessage in PostgreSQL)

4. **contracts/frontend-api.yaml**: OpenAPI 3.1 spec for frontend-backend API:
   - POST /api/v1/agents/orchestrator/invoke (send messages)
   - GET /api/v1/conversations (list conversations)
   - POST /api/v1/conversations (create conversation)
   - GET /api/v1/conversations/{id}/messages (get messages)
   - All endpoints require bearer token authentication

5. **quickstart.md**: Developer setup guide:
   - Create Next.js project with TypeScript and Tailwind
   - Install ChatKit, Better Auth, axios, swr
   - Configure environment variables
   - Project structure setup commands
   - Testing and deployment instructions

**Technical Context:**
- Language: TypeScript 5.0+, Node.js 18+
- Primary Dependencies: Next.js 14, ChatKit, Better Auth, React 18, Tailwind CSS 3.4, SWR
- Project Type: Web frontend (separate from backend)
- Performance Goals: Page load <2s, message display <100ms, API rendering <3s, mobile responsive 320px-1920px
- Constraints: HTTPS only, auth in headers (not URLs), zero sensitive data exposure, 90% error recovery
- Deployment: Vercel (zero-config, env vars, HTTPS, SSR support)

**Constitution Check:** 16/16 PASS
- XI. ChatKit Frontend Framework ✅ (mandated, using ChatKit React components)
- XII. Better Auth Authentication ✅ (mandated, using Better Auth with Next.js middleware)
- All other principles satisfied (frontend as presentation layer, backend handles MCP/agents/database)

**Key Architecture Decisions:**
- Next.js App Router (not Pages Router) for better performance with React Server Components
- SWR for server state caching + React Context for client state (auth, current conversation)
- Better Auth with Next.js middleware for server-side session validation (HTTP-only cookies)
- Custom API client wrapper (fetch-based, type-safe, retry logic, error handling)
- Backend database storage for conversations (enables multi-device sync)
- Custom tool call card UI (better UX than generic JSON viewer)
- Vercel deployment (superior to GitHub Pages: SSR, API routes, runtime env vars, HTTPS)
- Mobile-first responsive design with Tailwind CSS utility classes
- TypeScript schema validation for environment variables (fail-fast on missing config)

**Project Structure:**
New `frontend/` directory with Next.js App Router layout:
- `app/(auth)/` - Public auth pages (login, signup)
- `app/(dashboard)/` - Authenticated pages (chat, conversations, profile)
- `components/` - Reusable UI components (chat, auth, layout)
- `services/` - API integration layer (api-client, auth-service, chat-service)
- `hooks/` - Custom React hooks (useAuth, useChat, useConversation)
- `types/` - TypeScript type definitions
- `lib/` - Utility functions and configuration

Backend extensions needed:
- New models: `Conversation`, `ConversationMessage` in `backend/src/models/conversation.py`
- New endpoints in `backend/src/api/routes.py`: conversation CRUD, message retrieval

**Deployment Strategy:**
- Platform: Vercel (Next.js-optimized)
- Environment variables: `NEXT_PUBLIC_API_URL`, `BETTER_AUTH_SECRET`
- HTTPS: Automatic with custom domains
- Domain allowlist: Configured in Vercel dashboard
- Branch previews: Enabled for testing

## Outcome

- ✅ Impact: Complete implementation plan for production-ready ChatKit frontend with Next.js 14, Better Auth, and Vercel deployment. Plan addresses all 25 functional requirements and 10 success criteria from spec. Architecture decisions documented for Next.js App Router, SWR state management, server-side auth, and custom API client.
- 🧪 Tests: No tests (planning phase). Test strategy defined: Jest for unit, React Testing Library for components, Playwright for E2E.
- 📁 Files: 5 files created (plan.md, research.md, data-model.md, quickstart.md, frontend-api.yaml contract)
- 🔁 Next prompts: `/sp.tasks` to generate implementation tasks for Next.js setup, ChatKit integration, Better Auth configuration, API client, chat components, tool visualization, and Vercel deployment
- 🧠 Reflection: Plan successfully addresses Constitution mandates (XI: ChatKit, XII: Better Auth) while maintaining frontend-backend separation. Next.js App Router provides performance benefits over Pages Router. SWR handles server state elegantly with caching/revalidation. Better Auth with middleware ensures server-side session security (HTTP-only cookies). Custom API client enables type-safe backend integration with retry logic. Vercel deployment superior to GitHub Pages due to SSR, API routes, and runtime env vars. Mobile-first Tailwind CSS approach ensures responsive design. Backend conversation storage enables multi-device sync. Ready for task generation and implementation.

## Evaluation notes (flywheel)

- Failure modes observed: None. Planning succeeded without blockers.
- Graders run and results (PASS/FAIL): Constitution Check - PASS (16/16 principles satisfied)
- Prompt variant (if applicable): Standard /sp.plan with frontend architecture and deployment requirements
- Next experiment (smallest change to try): During implementation, consider Server Components vs Client Components split in Next.js App Router (research.md Decision 1 mentions App Router but doesn't detail component strategy)
