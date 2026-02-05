# Quick Start Guide: ChatKit Frontend

**Feature**: 003-chatkit-frontend
**Date**: 2026-01-16
**Prerequisites**: Backend from 001-reusable-agents running, Node.js 18+

## Setup

### 1. Create Frontend Project

```bash
# From repository root
npx create-next-app@latest frontend --typescript --tailwind --app
cd frontend
```

### 2. Install Dependencies

```bash
npm install @chatkit/react better-auth axios swr
npm install -D @types/node @types/react jest @testing-library/react playwright
```

### 3. Configure Environment

Create `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
BETTER_AUTH_SECRET=your-secret-key-min-32-chars
BETTER_AUTH_URL=http://localhost:3000
```

### 4. Project Structure

```bash
mkdir -p src/app/\(auth\)/{login,signup}
mkdir -p src/app/\(dashboard\)/{chat,conversations,profile}
mkdir -p src/{components/{chat,auth,layout},services,hooks,types,lib}
```

### 5. Run Development Server

```bash
npm run dev
# Opens http://localhost:3000
```

## Implementation Checklist

- [ ] Setup Next.js project with TypeScript
- [ ] Install ChatKit and Better Auth
- [ ] Create API client service (`services/api-client.ts`)
- [ ] Implement Better Auth middleware (`middleware.ts`)
- [ ] Create auth pages (login, signup)
- [ ] Build chat interface components
- [ ] Implement conversation history
- [ ] Add tool call visualization
- [ ] Configure Vercel deployment
- [ ] Test end-to-end flows

## Testing

```bash
# Unit tests
npm run test

# E2E tests
npm run test:e2e

# Build for production
npm run build
```

## Deployment to Vercel

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
cd frontend
vercel

# Set environment variables in Vercel dashboard
# - NEXT_PUBLIC_API_URL
# - BETTER_AUTH_SECRET
```

## References

- [plan.md](plan.md) - Implementation plan
- [research.md](research.md) - Architecture decisions
- [data-model.md](data-model.md) - TypeScript types
- [contracts/frontend-api.yaml](contracts/frontend-api.yaml) - API interface
