# Quickstart: Stateless Chat API & UI

**Feature**: 004-stateless-chat-api
**Last Updated**: 2026-01-26
**Time to Complete**: 10 minutes

## Purpose

Get the stateless chat API and ChatKit frontend running locally in under 10 minutes. This guide assumes you have completed Phase III-A (MCP Task Tools) and Phase III-B (AI Agent Orchestration).

## Prerequisites

### Required Software

- **Python 3.11+**: Backend runtime
- **Node.js 18+**: Frontend runtime
- **PostgreSQL** (Neon): Database already set up from Phase III-A
- **UV**: Python package manager (already installed)
- **npm/yarn**: Node package manager

### Required Environment Setup

Your `.env` file should already contain (from previous phases):

```bash
# Database (from Phase III-A)
DATABASE_URL=postgresql://user:pass@host/db

# OpenAI API (from Phase III-B)
OPENAI_API_KEY=sk-...

# Server
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
```

## Step 1: Verify Backend (2 minutes)

The backend is already functional from Phase III-B. We just need to verify the chat endpoint exists.

```bash
# Navigate to backend
cd backend

# Confirm chat endpoint exists
cat src/api/chat_endpoint.py | grep "@router.post"
# Should output: @router.post("/{user_id}/chat"...

# Start the server
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**Verify**: Open http://localhost:8000/docs and confirm `/api/{user_id}/chat` endpoint exists in Swagger UI.

## Step 2: Test API with curl (3 minutes)

### Test 1: Start New Conversation

```bash
curl -X POST "http://localhost:8000/api/test-user/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, I need help with my tasks"}'
```

**Expected Response**:
```json
{
  "conversation_id": "conv_abc12345",
  "response": "Hello! I can help you manage your tasks...",
  "tool_calls": [],
  "reasoning_trace": {...}
}
```

**Save the conversation_id** from the response for the next test.

### Test 2: Continue Conversation

```bash
curl -X POST "http://localhost:8000/api/test-user/chat" \
  -H "Content-Type": application/json" \
  -d '{
    "message": "Add a task to buy groceries",
    "conversation_id": "conv_abc12345"
  }'
```

**Expected Response**:
```json
{
  "conversation_id": "conv_abc12345",
  "response": "I've added 'buy groceries' to your tasks...",
  "tool_calls": [
    {
      "tool_name": "add_task",
      "parameters": {"title": "buy groceries"},
      "result": {"success": true, "data": {...}}
    }
  ]
}
```

### Test 3: Verify Restart Resilience

```bash
# Stop the server (Ctrl+C in terminal)

# Restart the server
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Continue the conversation with the SAME conversation_id
curl -X POST "http://localhost:8000/api/test-user/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What tasks do I have?",
    "conversation_id": "conv_abc12345"
  }'
```

**Expected**: The AI responds with awareness of the "buy groceries" task created before the restart.

## Step 3: Set Up Frontend (5 minutes)

### Create React App with ChatKit

```bash
# Navigate to project root
cd ..

# Create React app
npx create-react-app frontend --template typescript
cd frontend

# Install dependencies
npm install @chatscope/chat-ui-kit-react axios
npm install @chatscope/chat-ui-kit-styles

# Create directory structure
mkdir -p src/components/Chat
mkdir -p src/services
mkdir -p src/types
```

### Create API Service

Create `src/services/chatApi.ts`:

```typescript
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

export interface ChatMessage {
  message: string;
  conversation_id?: string;
}

export interface ChatResponse {
  conversation_id: string;
  response: string;
  tool_calls: any[];
  reasoning_trace?: any;
}

export const sendMessage = async (
  userId: string,
  message: ChatMessage
): Promise<ChatResponse> => {
  const response = await axios.post(
    `${API_BASE_URL}/${userId}/chat`,
    message
  );
  return response.data;
};
```

### Create Basic Chat Component

Create `src/components/Chat/ChatContainer.tsx`:

```typescript
import React, { useState, useEffect } from 'react';
import {
  MainContainer,
  ChatContainer,
  MessageList,
  Message,
  MessageInput,
  TypingIndicator
} from '@chatscope/chat-ui-kit-react';
import '@chatscope/chat-ui-kit-styles/dist/default/styles.min.css';
import { sendMessage, ChatResponse } from '../../services/chatApi';

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export const Chat: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);

  const userId = 'demo-user'; // In production, get from auth

  useEffect(() => {
    // Load conversation_id from localStorage
    const storedId = localStorage.getItem('conversation_id');
    if (storedId) {
      setConversationId(storedId);
      // Optionally: load conversation history here
    }
  }, []);

  const handleSendMessage = async (text: string) => {
    // Add user message to UI immediately (optimistic update)
    const userMessage: ChatMessage = {
      role: 'user',
      content: text,
      timestamp: new Date().toISOString()
    };
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // Send to API
      const response: ChatResponse = await sendMessage(userId, {
        message: text,
        conversation_id: conversationId || undefined
      });

      // Store conversation_id
      setConversationId(response.conversation_id);
      localStorage.setItem('conversation_id', response.conversation_id);

      // Add assistant response to UI
      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: response.response,
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, assistantMessage]);

    } catch (error) {
      console.error('Failed to send message:', error);
      alert('Failed to send message. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ height: '100vh', width: '100%' }}>
      <MainContainer>
        <ChatContainer>
          <MessageList
            typingIndicator={isLoading && <TypingIndicator content="AI is thinking..." />}
          >
            {messages.map((msg, idx) => (
              <Message
                key={idx}
                model={{
                  message: msg.content,
                  sentTime: msg.timestamp,
                  sender: msg.role === 'user' ? 'You' : 'AI Assistant',
                  direction: msg.role === 'user' ? 'outgoing' : 'incoming',
                  position: 'single'
                }}
              />
            ))}
          </MessageList>
          <MessageInput
            placeholder="Type your message here..."
            onSend={handleSendMessage}
            disabled={isLoading}
          />
        </ChatContainer>
      </MainContainer>
    </div>
  );
};
```

### Update App.tsx

Replace `src/App.tsx`:

```typescript
import React from 'react';
import { Chat } from './components/Chat/ChatContainer';

function App() {
  return (
    <div className="App">
      <Chat />
    </div>
  );
}

export default App;
```

### Start Frontend

```bash
npm start
```

**Browser**: Opens at http://localhost:3000 with the chat interface.

## Step 4: Test End-to-End (2 minutes)

### Test Flow:

1. **Open browser** at http://localhost:3000
2. **Type message**: "Hello, I need help managing my tasks"
3. **Click Send** or press Enter
4. **Observe**:
   - Your message appears immediately
   - Loading indicator shows
   - AI response appears after 1-3 seconds
5. **Type follow-up**: "Add a task to call dentist"
6. **Observe**: AI acknowledges and adds the task
7. **Refresh page** (F5)
8. **Type**: "What tasks do I have?"
9. **Observe**: AI lists the task you created (conversation_id persisted in localStorage)

### Test Restart Resilience:

1. Stop backend server (Ctrl+C)
2. Restart backend server
3. In browser (no refresh needed), type: "Show me my tasks"
4. **Observe**: AI responds with tasks from before restart

## Expected Result

✅ Backend API responds to chat requests
✅ Frontend displays messages in chat UI
✅ Conversations persist across page refreshes (localStorage)
✅ Conversations survive server restarts (database persistence)
✅ AI maintains context across multi-turn conversations

## Troubleshooting

### Backend Issues

**Error: "Port 8000 already in use"**
```bash
# Find process using port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill the process or use different port
uv run uvicorn src.main:app --reload --port 8001
```

**Error: "Database connection failed"**
- Verify DATABASE_URL in `.env`
- Confirm Neon database is accessible
- Check network connectivity

**Error: "OPENAI_API_KEY not found"**
- Add to `.env`: `OPENAI_API_KEY=sk-...`
- Restart server after adding

### Frontend Issues

**Error: "CORS policy blocked"**
Add CORS middleware to backend `main.py`:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Error: "Cannot read property 'conversation_id'"**
- Check backend response format in Network tab
- Verify API endpoint returns correct structure

**Messages not displaying**
- Open browser DevTools console
- Check for JavaScript errors
- Verify axios request succeeds (Network tab)

## Next Steps

- **Test with real tasks**: Try "add task", "list tasks", "complete task 1"
- **Test error cases**: Send empty message, very long message
- **Customize UI**: Modify ChatKit components, add avatars, timestamps
- **Add features**: Message editing, conversation history, user profiles

## Development Tips

### Hot Reload

Both backend and frontend support hot reload:
- **Backend**: `--reload` flag automatically restarts on code changes
- **Frontend**: Create React App automatically refreshes browser

### API Testing

Use Swagger UI at http://localhost:8000/docs for interactive API testing.

### Database Inspection

```bash
# Connect to database
psql $DATABASE_URL

# View conversations
SELECT conversation_id, COUNT(*) as message_count
FROM chat_message
GROUP BY conversation_id;

# View recent messages
SELECT conversation_id, message, timestamp
FROM chat_message
ORDER BY timestamp DESC
LIMIT 10;
```

## Production Checklist

Before deploying to production:

- [ ] Set CORS origins to production frontend domain
- [ ] Use environment-specific DATABASE_URL
- [ ] Secure OPENAI_API_KEY (use secrets manager)
- [ ] Add rate limiting to chat endpoint
- [ ] Implement proper user authentication
- [ ] Enable HTTPS (TLS/SSL)
- [ ] Add monitoring and logging
- [ ] Set up database backups
- [ ] Configure CDN for frontend static files
- [ ] Test with production-scale load

## References

- [ChatKit Documentation](https://chatscope.io/storybook/react/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- Phase III-B Implementation: `backend/src/api/chat_endpoint.py`
