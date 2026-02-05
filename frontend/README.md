# Chat Frontend

React/Next.js frontend for the stateless chat API using ChatKit UI components.

## Features

- **Real-time Chat Interface**: ChatKit-powered UI for natural conversations
- **Conversation Persistence**: Conversation ID stored in localStorage for continuity across page refreshes
- **Optimistic UI**: Messages appear instantly before API confirmation
- **Error Handling**: User-friendly error messages with automatic retry suggestions
- **Responsive Design**: Works on desktop and mobile devices
- **TypeScript**: Full type safety throughout the application

## Getting Started

### Prerequisites

- Node.js 18+ installed
- Backend API running at `http://localhost:8000` (see `../backend/README.md`)

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at http://localhost:3000

### Environment Variables

Create a `.env.local` file with:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

For production, set `NEXT_PUBLIC_API_URL` to your deployed backend URL.

## Project Structure

```
src/
├── app/                      # Next.js 13+ app directory
│   ├── chat/                 # Chat page
│   ├── layout.tsx            # Root layout
│   └── page.tsx              # Home page (redirects to chat)
├── components/
│   ├── Chat/                 # Chat components
│   │   ├── ChatContainer.tsx # Main chat wrapper with state
│   │   └── Message.tsx       # Individual message component
│   └── common/               # Shared components
│       └── LoadingSpinner.tsx
├── services/                 # API and storage services
│   ├── chatApi.ts            # Backend API client
│   └── conversationStorage.ts # localStorage management
└── types/                    # TypeScript type definitions
    └── chat.types.ts
```

## Key Components

### ChatContainer

Main component managing chat state, API calls, and localStorage persistence.

**Features:**
- Loads conversation ID from localStorage on mount
- Sends messages to backend API
- Optimistic UI updates (messages appear immediately)
- Error handling with user-friendly messages
- New conversation button to start fresh

### Message

Renders individual chat messages with:
- User/Assistant styling (different colors and avatars)
- Timestamp display
- Tool call indicators (if available)

### Services

#### chatApi.ts
- `sendMessage(userId, message)`: Send message to backend
- `checkHealth()`: Check if backend is healthy

#### conversationStorage.ts
- `getConversationId()`: Retrieve conversation ID from localStorage
- `setConversationId(id)`: Store conversation ID
- `clearConversationId()`: Clear conversation (new conversation)
- `hasConversationId()`: Check if conversation exists

## Usage

### Basic Chat Flow

1. User opens the app → Redirected to `/chat`
2. Chat loads conversation ID from localStorage (if exists)
3. User types message → Appears immediately (optimistic UI)
4. API call to backend → Response appears
5. Conversation ID stored in localStorage for future sessions

### Starting a New Conversation

Click the "New Conversation" button in the header to clear localStorage and start fresh.

### Error Handling

Network errors, API errors, and validation errors display user-friendly messages:
- Connection errors: "Unable to connect to server. Please check your connection."
- Validation errors: Specific field errors (e.g., "Message is required")
- Server errors: "An error occurred. Please try again."

## Development

### Running Tests

```bash
npm test
```

### Building for Production

```bash
npm run build
npm start
```

### Linting

```bash
npm run lint
```

## API Integration

The frontend communicates with the backend API at `${NEXT_PUBLIC_API_URL}/{user_id}/chat`.

**Request:**
```json
{
  "message": "Hello, can you help me?",
  "conversation_id": "conv_abc12345"  // Optional
}
```

**Response:**
```json
{
  "conversation_id": "conv_abc12345",
  "response": "Of course! How can I help you today?",
  "tool_calls": [],
  "reasoning_trace": {
    "intent": "general",
    "confidence": 0.85,
    "tool_selected": null,
    "response_time_ms": 1250
  }
}
```

## Troubleshooting

### Browser Access Issues

**Problem:** Cannot access the app

**Solutions:**
1. **Development**: Use `http://localhost:3000` (NOT `http://0.0.0.0:3000`)
2. **Check server is running:**
   ```bash
   npm run dev
   # Should show: ready - started server on 0.0.0.0:3000
   ```
3. **Alternative**: Try `http://127.0.0.1:3000`

### CORS Errors

**Error:** "Access to fetch at '...' has been blocked by CORS policy"

**Solution:** Ensure backend has CORS configured to allow your frontend origin:

```python
# backend/src/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",           # Development
        "https://yourdomain.com",          # Production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Messages Not Sending

**Symptoms:** Messages don't appear or show errors

**Debug steps:**
1. **Check backend is running:**
   ```bash
   curl http://localhost:8000/health
   # Should return 200 OK
   ```

2. **Check browser console** (F12 → Console tab):
   - Look for network errors
   - Check for CORS errors
   - Verify API URL is correct

3. **Check Network tab** (F12 → Network):
   - Filter by "Fetch/XHR"
   - Look for failed requests (red status)
   - Check request/response details

4. **Verify environment variable:**
   ```bash
   # Check .env.local exists and has:
   NEXT_PUBLIC_API_URL=http://localhost:8000/api
   ```

5. **Restart dev server:**
   ```bash
   # Stop server (Ctrl+C) then:
   npm run dev
   ```

### Conversation Not Persisting

**Problem:** Conversation ID lost after page refresh

**Debug:**
- Check browser's localStorage is enabled
- Open DevTools → Application → Local Storage → http://localhost:3000
- Verify `chat_conversation_id` key exists
- Try in incognito mode (rules out extension interference)

**Solution:**
```javascript
// Clear and test
localStorage.clear();
// Then send a new message and refresh
```

### ChatKit Styles Not Loading

**Problem:** Chat UI looks unstyled or broken

**Solution:** Ensure ChatKit styles are imported in `ChatContainer.tsx`:

```typescript
import '@chatscope/chat-ui-kit-styles/dist/default/styles.min.css';
```

### Build Errors

**Error:** "Module not found" during build

**Solution:**
```bash
# Clean and reinstall
rm -rf node_modules package-lock.json
npm install

# Clear Next.js cache
rm -rf .next
npm run build
```

### API URL Not Working in Production

**Problem:** Frontend can't reach backend in production

**Checklist:**
1. ✅ `NEXT_PUBLIC_API_URL` is set in deployment platform
2. ✅ Backend URL is accessible (test with curl)
3. ✅ CORS allows production frontend URL
4. ✅ Both frontend and backend use HTTPS (no mixed content)
5. ✅ Environment variable has `/api` suffix: `https://api.com/api`

### Performance Issues

**Problem:** Slow loading or laggy UI

**Solutions:**
1. **Check bundle size:**
   ```bash
   npm run build
   # Look for large chunks (>200KB)
   ```

2. **Optimize images:**
   - Use Next.js Image component
   - Enable image optimization in `next.config.js`

3. **Enable React strict mode** (check for unnecessary re-renders):
   ```typescript
   // next.config.js
   const nextConfig = {
     reactStrictMode: true,
   }
   ```

4. **Use production build locally:**
   ```bash
   npm run build
   npm start
   # Faster than dev mode
   ```

## Production Deployment

### Pre-Deployment Checklist

Before deploying to production:

1. ✅ Set `NEXT_PUBLIC_API_URL` to production backend URL
2. ✅ Build the production bundle (`npm run build`)
3. ✅ Test the production build locally (`npm start`)
4. ✅ Enable authentication (future phase)
5. ✅ Configure rate limiting on backend
6. ✅ Set up monitoring and error tracking
7. ✅ Enable HTTPS/TLS
8. ✅ Configure CDN for static assets

### Deployment Options

#### Option 1: Vercel (Recommended for Next.js)

**Automatic Deployment via GitHub:**

1. Push your code to GitHub
2. Go to [Vercel Dashboard](https://vercel.com/new)
3. Import your repository
4. Configure:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`
5. Add environment variable:
   - `NEXT_PUBLIC_API_URL`: Your production backend URL (e.g., `https://api.yourdomain.com/api`)
6. Click "Deploy"

**Manual Deployment via CLI:**

```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy from frontend directory
cd frontend
vercel --prod

# Set environment variable
vercel env add NEXT_PUBLIC_API_URL
# Enter your backend URL when prompted
```

**Custom Domain:**
- Go to your project settings in Vercel
- Add your custom domain
- Update DNS records as instructed

#### Option 2: Netlify

1. Install Netlify CLI:
```bash
npm install -g netlify-cli
```

2. Build and deploy:
```bash
cd frontend
npm run build

# Deploy
netlify deploy --prod --dir=.next
```

3. Set environment variables in Netlify dashboard:
   - `NEXT_PUBLIC_API_URL`: Your backend URL

**Or use Netlify UI:**
1. Connect GitHub repository
2. Set build settings:
   - **Base directory**: `frontend`
   - **Build command**: `npm run build`
   - **Publish directory**: `.next`
3. Add environment variables

#### Option 3: Docker + Cloud Platform

**Create `frontend/Dockerfile`:**

```dockerfile
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci

# Copy source code
COPY . .

# Build the application
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
RUN npm run build

# Production image
FROM node:18-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production

# Copy built files
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/package*.json ./
COPY --from=builder /app/node_modules ./node_modules

EXPOSE 3000

CMD ["npm", "start"]
```

**Build and run:**

```bash
# Build
docker build -t chat-frontend \
  --build-arg NEXT_PUBLIC_API_URL=https://api.yourdomain.com/api \
  ./frontend

# Run
docker run -p 3000:3000 chat-frontend
```

**Deploy to cloud platforms:**
- **Railway**: `railway up`
- **Render**: Connect GitHub repo with `render.yaml`
- **Google Cloud Run**: `gcloud run deploy`
- **AWS ECS/Fargate**: Use Docker image

#### Option 4: Static Export + CDN

If you don't need server-side features:

1. Update `next.config.js`:
```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  images: {
    unoptimized: true,
  },
}

module.exports = nextConfig
```

2. Build static files:
```bash
npm run build
```

3. Deploy `out/` folder to:
   - **AWS S3 + CloudFront**
   - **Google Cloud Storage + CDN**
   - **Azure Static Web Apps**
   - **GitHub Pages**
   - **Cloudflare Pages**

### Environment Variables by Platform

| Platform | Method |
|----------|--------|
| Vercel | Dashboard → Project → Settings → Environment Variables |
| Netlify | Dashboard → Site Settings → Environment Variables |
| Railway | Dashboard → Variables tab |
| Render | Dashboard → Environment tab |
| Docker | `--build-arg` flag or `.env` file |

### CORS Configuration

Ensure your backend allows your production frontend URL:

```python
# backend/src/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",           # Development
        "https://yourdomain.com",          # Production
        "https://your-app.vercel.app",    # Vercel preview
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Post-Deployment Verification

1. **Test health endpoint:**
```bash
curl https://yourdomain.com
```

2. **Test chat functionality:**
   - Send a message
   - Refresh page → Verify conversation persists
   - Start new conversation

3. **Check browser console:**
   - No CORS errors
   - No 404s for assets
   - API calls succeed

4. **Performance testing:**
   - Run Lighthouse audit (Chrome DevTools)
   - Check Core Web Vitals
   - Optimize images and bundle size if needed

### Monitoring & Analytics

**Error Tracking:**
```bash
# Install Sentry
npm install @sentry/nextjs

# Initialize
npx @sentry/wizard -i nextjs
```

**Analytics:**
- Vercel Analytics (built-in)
- Google Analytics
- Plausible Analytics
- PostHog

### Rollback Strategy

**Vercel:**
- Dashboard → Deployments → Select previous → Promote to Production

**Netlify:**
- Dashboard → Deploys → Select previous → Publish deploy

**Docker:**
```bash
# Tag versions
docker tag chat-frontend:latest chat-frontend:v1.2.3

# Rollback
docker run -p 3000:3000 chat-frontend:v1.2.2
```

## Dependencies

- **Next.js 16+**: React framework with App Router
- **React 19**: UI library
- **ChatKit**: Chat UI components (@chatscope/chat-ui-kit-react)
- **Axios**: HTTP client for API requests
- **TypeScript**: Type safety

## License

Proprietary - Part of Hackathon Phase 3
