# Research & Architecture Decisions: ChatKit Frontend

**Feature**: 003-chatkit-frontend
**Date**: 2026-01-16
**Status**: Complete

## Overview

This document captures technical decisions for implementing a production-ready ChatKit frontend with Better Auth, focusing on Next.js architecture, deployment strategy, and API integration patterns.

## Decision 1: Frontend Framework - Next.js vs Alternatives

**Context**: Need modern React framework for ChatKit integration with SSR/SSG capabilities and production deployment.

**Options Considered**:

| Option | Description | Pros | Cons |
|--------|-------------|------|------|
| A. Next.js 14 App Router | React framework with server components | Built-in routing, SSR/SSG, optimized builds, Vercel deployment | Learning curve for App Router |
| B. Create React App (CRA) | Simple React SPA | Simple setup | No SSR, deprecated, poor performance |
| C. Vite + React Router | Modern build tool | Fast dev server | Manual routing, no built-in SSR |

**Decision**: **Option A - Next.js 14 with App Router**

**Rationale**:
- Constitution-aligned: ChatKit supports Next.js officially
- App Router provides better performance with React Server Components
- Built-in API routes for middleware (auth checks, CORS handling)
- Vercel deployment is seamless (one-click)
- Image optimization, automatic code splitting, font optimization built-in
- Better Auth has Next.js integration examples

## Decision 2: State Management Approach

**Context**: Need state management for auth, conversations, messages, and API data.

**Options Considered**:

| Option | Description | Pros | Cons |
|--------|-------------|------|------|
| A. React Context + Hooks | Built-in React state | No dependencies, simple | Can cause re-renders, verbose |
| B. Redux Toolkit | Global state library | Predictable, dev tools | Boilerplate, overkill for this app |
| C. SWR (stale-while-revalidate) | Data fetching library | Caching, revalidation, optimistic UI | Not for local state |

**Decision**: **Option C (SWR) + Option A (Context for auth)**

**Rationale**:
- SWR handles server state (conversations, messages) with automatic caching
- React Context for client state (auth session, current conversation)
- No Redux needed - app is simple (5 pages, limited local state)
- SWR provides built-in error retry, loading states, optimistic updates
- Aligns with FR-025 (retry logic for failed API requests)

## Decision 3: Better Auth Integration Strategy

**Context**: Need email/password authentication with session management per Constitution XII.

**Options Considered**:

| Option | Description | Pros | Cons |
|--------|-------------|------|------|
| A. Better Auth client-side only | Auth logic in frontend | Simple integration | Security risk (token in localStorage) |
| B. Better Auth with Next.js middleware | Server-side session validation | Secure (HTTP-only cookies) | More complex setup |
| C. Custom auth implementation | Build from scratch | Full control | Violates Constitution XII |

**Decision**: **Option B - Better Auth with Next.js middleware**

**Rationale**:
- Meets Constitution XII requirement (Better Auth mandate)
- HTTP-only cookies for session tokens (FR-005, SC-010)
- Next.js middleware validates auth on every request
- Session persists across refreshes (SC-007)
- Handles 401 responses automatically (FR-017)

**Implementation Pattern**:
```typescript
// middleware.ts - runs on every request
export function middleware(request: NextRequest) {
  const session = await verifySession(request);
  if (!session && !isPublicRoute(request.pathname)) {
    return NextResponse.redirect('/login');
  }
  return NextResponse.next();
}
```

## Decision 4: API Client Architecture

**Context**: Need service layer to communicate with backend orchestrator API from 001-reusable-agents.

**Options Considered**:

| Option | Description | Pros | Cons |
|--------|-------------|------|------|
| A. Direct fetch calls | Use fetch() in components | No dependencies | Verbose, no interceptors |
| B. Axios with interceptors | HTTP client library | Request/response interceptors | Extra dependency |
| C. Custom API client wrapper | Abstraction over fetch | Type-safe, consistent errors | Need to build |

**Decision**: **Option C - Custom API client wrapper over fetch**

**Rationale**:
- No extra dependencies (fetch is built-in)
- Centralized error handling (FR-008, FR-024)
- Auth header injection (FR-007)
- Retry logic (FR-025: max 3 retries, exponential backoff)
- Type-safe with TypeScript generics

**API Client Structure**:
```typescript
class ApiClient {
  async post<T>(endpoint: string, data: any): Promise<T> {
    return this.request<T>(endpoint, { method: 'POST', body: JSON.stringify(data) });
  }

  private async request<T>(endpoint: string, options: RequestInit): Promise<T> {
    // Add auth header
    // Implement retry logic
    // Handle errors uniformly
    // Log for debugging
  }
}
```

## Decision 5: Conversation Data Model - Frontend vs Backend Storage

**Context**: Need to decide where conversation history is stored and how it's synchronized.

**Options Considered**:

| Option | Description | Pros | Cons |
|--------|-------------|------|------|
| A. Frontend-only (localStorage) | Store conversations in browser | No backend changes | Not synced across devices, limited storage |
| B. Backend database | Store in PostgreSQL via new API endpoints | Synced across devices, unlimited storage | Requires backend changes |
| C. Hybrid | Cache in frontend, sync to backend | Best UX | Complex sync logic |

**Decision**: **Option B - Backend database storage**

**Rationale**:
- Aligns with Constitution V (Database as Single Source of Truth)
- Enables multi-device access (user logs in on different computer)
- Unlimited conversation history
- Backend already has database and models infrastructure
- Simple API endpoints needed (`GET /conversations`, `POST /conversations/{id}/messages`)

**Backend Changes**:
- Add `Conversation` and `ConversationMessage` models (already exist in 001-reusable-agents data model)
- Add API endpoints in `backend/src/api/routes.py`

## Decision 6: Tool Call Visualization Format

**Context**: FR-004 requires showing tool name, parameters, and results in chat interface.

**Options Considered**:

| Option | Description | Pros | Cons |
|--------|-------------|------|------|
| A. Inline JSON code blocks | Display JSON in ```json``` blocks | Simple | Not user-friendly for large objects |
| B. Collapsible JSON tree viewer | react-json-view or similar | Interactive, readable | Extra dependency |
| C. Custom card UI | Purpose-built component | Tailored UX | More dev work |

**Decision**: **Option C - Custom card UI with expandable sections**

**Rationale**:
- Best user experience (FR-004, FR-020)
- Control over styling (match ChatKit design)
- Can show summary view (tool name, status) with expand for details
- Avoids dependency on JSON viewer library

**Tool Call Card Layout**:
```
┌─────────────────────────────────┐
│ 🛠️ add_task                     │
│ Status: ✅ Success              │
│ ▼ Show details                  │
│   Parameters:                   │
│   • title: "Buy groceries"      │
│   • description: "..."          │
│   Result:                       │
│   • task_id: 123                │
│   • created_at: "..."           │
└─────────────────────────────────┘
```

## Decision 7: Deployment Platform - Vercel vs GitHub Pages

**Context**: User specified "Deploy to Vercel or GitHub Pages" with domain allowlist and secure key injection.

**Options Considered**:

| Option | Description | Pros | Cons |
|--------|-------------|------|------|
| A. Vercel | Next.js-optimized hosting | Zero-config, env vars, HTTPS, previews | Requires account |
| B. GitHub Pages | Free static hosting | Free, simple | No SSR, no env vars (build-time only) |
| C. Netlify | Alternative static hosting | Similar to Vercel | Another account |

**Decision**: **Option A - Vercel**

**Rationale**:
- Next.js is developed by Vercel (best integration)
- Supports SSR and API routes (GitHub Pages doesn't)
- Environment variables injected securely at runtime (not build-time)
- Automatic HTTPS with custom domains
- Preview deployments for branches
- Domain allowlist via Vercel dashboard
- Free tier sufficient for MVP

**Deployment Configuration**:
- Set `NEXT_PUBLIC_API_URL` environment variable in Vercel dashboard
- Set `BETTER_AUTH_SECRET` for session encryption
- Configure custom domain with DNS
- Enable branch previews for testing

## Decision 8: ChatKit Integration Pattern

**Context**: Constitution XI mandates ChatKit for chat UI. Need integration strategy.

**Options Considered**:

| Option | Description | Pros | Cons |
|--------|-------------|------|------|
| A. ChatKit wrapper components | Wrap ChatKit components in custom React components | Flexibility, custom styling | More code |
| B. Direct ChatKit usage | Use ChatKit components directly | Less code, official patterns | Tightly coupled |
| C. Hybrid approach | Direct for simple, wrapped for complex | Balanced | Need clear guidelines |

**Decision**: **Option C - Hybrid approach**

**Rationale**:
- Use ChatKit directly for standard components (MessageBubble, MessageInput)
- Wrap for custom features (ToolCallCard, reasoning traces)
- Maintains ChatKit design consistency
- Allows extension for tool visualization (FR-004, FR-020, FR-021)

## Decision 9: Mobile Responsiveness Strategy

**Context**: SC-008 requires responsive design for 320px-1920px viewports.

**Options Considered**:

| Option | Description | Pros | Cons |
|--------|-------------|------|------|
| A. Mobile-first CSS | Start with 320px, scale up | Better mobile UX | Desktop as afterthought |
| B. Desktop-first CSS | Start with 1920px, scale down | Better desktop UX | Mobile as afterthought |
| C. Container queries | CSS container queries | Modern, component-scoped | Browser support ~2023+ |

**Decision**: **Option A - Mobile-first with Tailwind CSS**

**Rationale**:
- Mobile traffic dominates web usage
- Tailwind provides mobile-first utility classes (`sm:`, `md:`, `lg:`)
- Easier to enhance for desktop than restrict for mobile
- ChatKit components are responsive by default

**Breakpoints**:
- `sm:` 640px (large phones, small tablets)
- `md:` 768px (tablets)
- `lg:` 1024px (laptops)
- `xl:` 1280px (desktops)

## Decision 10: Environment Configuration Management

**Context**: User specified "Environment-based configuration" for flexibility.

**Options Considered**:

| Option | Description | Pros | Cons |
|--------|-------------|------|------|
| A. .env files only | Standard .env approach | Simple | Hard to manage multiple environments |
| B. Config service | Centralized config with fallbacks | Flexible | Overkill |
| C. .env + validation | .env with Zod/schema validation | Type-safe, catches errors early | Need validation layer |

**Decision**: **Option C - .env files with TypeScript schema validation**

**Rationale**:
- Type-safe configuration at build time
- Validates required env vars early (fails fast)
- Clear error messages for missing config
- Supports multiple environments (.env.local, .env.production)

**Config Schema**:
```typescript
// lib/api-config.ts
const envSchema = z.object({
  NEXT_PUBLIC_API_URL: z.string().url(),
  BETTER_AUTH_SECRET: z.string().min(32),
});

export const config = envSchema.parse(process.env);
```

## Architecture Summary

### Component Hierarchy

```
App Layout (auth check)
├── Login Page (public)
├── Signup Page (public)
└── Dashboard Layout (authenticated)
    ├── Navbar (logout, profile)
    ├── Sidebar (conversation list)
    └── Chat Page
        ├── Message List
        │   ├── Message Bubble (user/agent)
        │   └── Tool Call Card (expandable)
        ├── Message Input
        └── Loading Indicator
```

### Data Flow

```
User Types Message
→ MessageInput component
→ useChat hook
→ chat-service.ts (API client)
→ POST /api/v1/agents/orchestrator/invoke (backend)
→ Orchestrator Agent (001-reusable-agents)
→ Response with tool calls
→ SWR cache updates
→ MessageList re-renders
→ Tool Call Cards appear
```

### Authentication Flow

```
User Lands on App
→ Next.js middleware checks session
→ No session? Redirect to /login
→ User submits credentials
→ auth-service.ts calls Better Auth
→ Better Auth returns session token (HTTP-only cookie)
→ Middleware allows access to /chat
→ Session persists across refreshes
→ Session expires after 7 days or manual logout
```

## Open Questions & Future Work

**Resolved - No open questions remain.**

All technical decisions documented above. Ready for Phase 1 (data-model.md, contracts/, quickstart.md).

## References

- Feature spec: [spec.md](spec.md)
- Constitution: [.specify/memory/constitution.md](../../.specify/memory/constitution.md)
- Backend docs (001-reusable-agents): [backend/docs/](../../backend/docs/)
- Next.js documentation: https://nextjs.org/docs
- ChatKit documentation: https://chatkit.io/docs (assumed)
- Better Auth documentation: https://better-auth.com/docs (assumed)
