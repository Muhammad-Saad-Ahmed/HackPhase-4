# MCP-Based Todo Chatbot Integration Flow

## 🎯 Overview

The MCP (Model Context Protocol) chatbot is fully integrated into the Todo App dashboard as an **optional sidebar feature**. It uses MCP server tools to perform task operations through natural language, with real-time synchronization to the todo list UI.

---

## 🔐 Authentication Flow

### Auth Token Management

```
┌─────────────┐
│   User      │
│   Login     │
└──────┬──────┘
       │
       ├─ POST /api/auth/login
       │  (email, password)
       │
       ▼
┌──────────────────────┐
│  Auth Service        │
│  (Backend)           │
└──────┬───────────────┘
       │
       ├─ Generates JWT Token
       │  {user_id, email, exp}
       │
       ▼
┌──────────────────────┐
│  sessionStorage      │
│  session_token: JWT  │
└──────────────────────┘
       │
       ├─ Stored in browser
       │
       ▼
┌──────────────────────┐
│  apiClient           │
│  Auto-injects token  │
│  in Authorization:   │
│  Bearer <token>      │
└──────────────────────┘
```

**Key Points:**
- ✅ JWT token stored in `sessionStorage`
- ✅ `apiClient` automatically injects token in all API requests
- ✅ Backend extracts `user_id` from JWT for all operations
- ✅ Same auth token used for both REST API and Chat API

---

## 💬 Chat → MCP Tool Execution Flow

### Complete Request/Response Cycle

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    FRONTEND (Dashboard)                                  │
│                                                                           │
│  ┌──────────────────┐              ┌─────────────────────────────────┐ │
│  │   Todo List UI   │◄─────────────┤  ChatContainer (Sidebar)        │ │
│  │   (60% width)    │  Event Bus   │  (40% width)                    │ │
│  │                  │  Sync        │                                  │ │
│  │  - Add Task Form │              │  User types:                     │ │
│  │  - Task Items    │              │  "add task to buy groceries"     │ │
│  │  - Filter Tabs   │              │                                  │ │
│  └────┬─────────────┘              └───────────┬──────────────────────┘ │
│       │                                        │                         │
│       │                                        │ sendMessage()           │
│       │                                        ▼                         │
│       │                            ┌────────────────────────────┐       │
│       │                            │  chatApi.ts                │       │
│       │                            │  - apiClient.post()        │       │
│       │                            │  - Auto-injects JWT token  │       │
│       │                            └─────────┬──────────────────┘       │
└───────┼──────────────────────────────────────┼──────────────────────────┘
        │                                      │
        │                                      │ POST /api/v1/chat
        │                                      │ Authorization: Bearer <JWT>
        │                                      │ { message, conversation_id }
        │                                      │
        │                                      ▼
┌───────┼──────────────────────────────────────────────────────────────────┐
│       │                BACKEND (Python/FastAPI)                          │
│       │                                                                   │
│       │                      ┌─────────────────────────────────┐        │
│       │                      │  chat_endpoint.py               │        │
│       │                      │  - Validates JWT token          │        │
│       │                      │  - Extracts user_id from token  │        │
│       │                      └────────┬────────────────────────┘        │
│       │                               │                                  │
│       │                               │ run_conversation()               │
│       │                               ▼                                  │
│       │                      ┌─────────────────────────────────┐        │
│       │                      │  AgentRunner                    │        │
│       │                      │  (agent_runner.py)              │        │
│       │                      │                                 │        │
│       │                      │  1. Intent Recognition          │        │
│       │                      │     "add task" → create intent  │        │
│       │                      │                                 │        │
│       │                      │  2. Tool Selection              │        │
│       │                      │     create → add_task tool      │        │
│       │                      └────────┬────────────────────────┘        │
│       │                               │                                  │
│       │                               │ execute_tool()                   │
│       │                               ▼                                  │
│       │                      ┌─────────────────────────────────┐        │
│       │                      │  MCPTaskExecutor                │        │
│       │                      │  (mcp_client_direct.py)         │        │
│       │                      │  - Direct MCP tool execution    │        │
│       │                      │  - No HTTP overhead             │        │
│       │                      └────────┬────────────────────────┘        │
│       │                               │                                  │
│       │                               │ execute(title="buy groceries")   │
│       │                               ▼                                  │
│       │                      ┌─────────────────────────────────┐        │
│       │                      │  AddTaskTool                    │        │
│       │                      │  (add_task_tool.py)             │        │
│       │                      └────────┬────────────────────────┘        │
│       │                               │                                  │
│       │                               │ create_task()                    │
│       │                               ▼                                  │
│       │                      ┌─────────────────────────────────┐        │
│       │◄─────────────────────┤  TaskService                    │        │
│       │  Database write      │  (task_service.py)              │        │
│       │                      │  - SHARED by REST & MCP         │        │
│       │                      │  - Single source of truth       │        │
│       │                      └─────────────────────────────────┘        │
│       │                                                                   │
└───────┼───────────────────────────────────────────────────────────────────┘
        │
        │ Response flows back:
        │ {
        │   conversation_id: "abc123",
        │   response: "Task created successfully: buy groceries",
        │   tool_calls: [{
        │     tool_name: "add_task",
        │     parameters: { title: "buy groceries" },
        │     result: { success: true, data: {...} }
        │   }]
        │ }
        │
        ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                    FRONTEND (Dashboard)                                   │
│                                                                            │
│  ┌─────────────────────────────────┐    ┌─────────────────────────────┐ │
│  │  ChatContainer                  │    │  TodoList                   │ │
│  │                                 │    │                             │ │
│  │  1. Receives response           │    │  1. Listening for events    │ │
│  │  2. Detects tool_call          │    │     (eventBus.on)           │ │
│  │  3. Shows indicator: ⚡ MCP     │    │                             │ │
│  │  4. Emits event:               │───►│  2. Receives TASKS_REFRESH  │ │
│  │     EVENTS.TASKS_REFRESH        │    │  3. Shows: ⚡ Syncing...    │ │
│  │  5. Displays: "Task created"   │    │  4. Calls fetchTasks()      │ │
│  │                                 │    │  5. UI updates with new task│ │
│  └─────────────────────────────────┘    └─────────────────────────────┘ │
│                                                                            │
│  Result: BOTH UI and Chat are in sync! ✅                                │
└───────────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Real-Time Synchronization

### Event-Based Architecture

```javascript
// When chat executes MCP tool:
ChatContainer.tsx:
  response.tool_calls → detects "add_task"
  ├─ setLastToolCall("add_task")  // Visual indicator
  ├─ eventBus.emit(EVENTS.TASK_CREATED)
  └─ eventBus.emit(EVENTS.TASKS_REFRESH)

// TodoList auto-refreshes:
TodoList.tsx:
  eventBus.on(EVENTS.TASKS_REFRESH, () => {
    setSyncIndicator("Syncing with chat...")
    fetchTasks()  // GET /api/v1/tasks
  })
```

**Supported Events:**
- `TASK_CREATED` - New task added via chat
- `TASK_UPDATED` - Task edited via chat
- `TASK_COMPLETED` - Task marked done via chat
- `TASK_DELETED` - Task removed via chat
- `TASKS_REFRESH` - Trigger todo list reload

---

## 🛠️ MCP Tools Available

### 1. add_task
```json
Request:  { "title": "buy groceries", "description": "milk and bread" }
Response: { "success": true, "data": { "id": 1, "title": "buy groceries", ... } }
Event:    TASKS_REFRESH → Todo list reloads
```

### 2. list_tasks
```json
Request:  { "status": "pending" }
Response: { "success": true, "data": [{...}, {...}] }
Event:    TASKS_REFRESH → Todo list shows same data
```

### 3. update_task
```json
Request:  { "task_id": 1, "title": "buy groceries and eggs" }
Response: { "success": true, "data": {...} }
Event:    TASKS_REFRESH → Todo list updates task
```

### 4. complete_task
```json
Request:  { "task_id": 1 }
Response: { "success": true, "data": { "id": 1, "status": "completed", ... } }
Event:    TASKS_REFRESH → Todo list shows completed status
```

### 5. delete_task
```json
Request:  { "task_id": 1 }
Response: { "success": true }
Event:    TASKS_REFRESH → Todo list removes task
```

---

## 🎨 Visual Indicators

### Chat MCP Indicator
```
┌────────────────────────────┐
│  ⚡ MCP: add task          │  ← Purple gradient badge
└────────────────────────────┘
```
- Appears when MCP tool is executed
- Auto-dismisses after 3 seconds
- Shows which tool was called

### Todo List Sync Indicator
```
┌────────────────────────────┐
│  ⚡ Syncing with chat...    │  ← Purple gradient banner
└────────────────────────────┘
```
- Appears when chat modifies tasks
- Auto-dismisses after 2 seconds
- Shows loading animation

---

## 🔒 Security & Auth

### Token Flow

1. **Login:**
   ```
   User → Login Form → POST /api/auth/login
   Backend → Validates credentials → Returns JWT
   Frontend → Stores in sessionStorage
   ```

2. **API Requests:**
   ```javascript
   // apiClient automatically adds header:
   headers: {
     'Authorization': 'Bearer eyJhbGciOiJIUzI1...'
   }
   ```

3. **Backend Validation:**
   ```python
   # auth_middleware.py
   token = request.headers.get('Authorization')
   payload = jwt.decode(token)
   user_id = payload['user_id']  # Used for all operations
   ```

4. **MCP Tool Execution:**
   ```python
   # Backend extracts user_id from JWT
   # TaskService uses user_id for data isolation
   # (Currently global tasks, but user_id available for future scoping)
   ```

**Security Features:**
- ✅ JWT-based authentication
- ✅ Token auto-injection via apiClient
- ✅ Backend validates all requests
- ✅ User ID extracted from token (no client trust)
- ✅ Same auth for REST and Chat APIs

---

## 🚀 Complete User Journey

### Scenario: User adds task via chat

```
1. User clicks "Show AI Assistant"
   └─ Chat sidebar appears (40% width)

2. User types: "add a task to buy milk"
   ├─ Message appears in chat
   └─ Shows: "AI is processing with MCP tools..."

3. Frontend sends to backend:
   POST /api/v1/chat
   Authorization: Bearer <JWT>
   {
     "message": "add a task to buy milk",
     "conversation_id": "abc123"
   }

4. Backend processes:
   ├─ Validates JWT token
   ├─ Extracts user_id
   ├─ AgentRunner recognizes "create" intent
   ├─ Selects "add_task" MCP tool
   ├─ MCPTaskExecutor calls AddTaskTool
   └─ TaskService creates task in database

5. Backend responds:
   {
     "conversation_id": "abc123",
     "response": "Task created successfully: buy milk",
     "tool_calls": [{
       "tool_name": "add_task",
       "result": { "success": true, "data": {...} }
     }]
   }

6. Frontend receives response:
   ├─ ChatContainer shows response message
   ├─ Detects tool_call: "add_task"
   ├─ Shows indicator: "⚡ MCP: add task"
   └─ Emits: EVENTS.TASKS_REFRESH

7. TodoList responds to event:
   ├─ Shows: "⚡ Syncing with chat..."
   ├─ Calls GET /api/v1/tasks
   ├─ Receives updated task list
   └─ Re-renders with new task

8. Result:
   ✅ Chat shows confirmation
   ✅ Todo list shows new task
   ✅ Both UIs in perfect sync
   ✅ User sees seamless experience
```

---

## ✅ Integration Checklist

### ✅ **Auth Token Reuse**
- [x] Same JWT token for REST and Chat APIs
- [x] apiClient auto-injects token in all requests
- [x] Backend validates token and extracts user_id
- [x] No duplicate auth needed

### ✅ **Chatbot as Sidebar**
- [x] Chat appears in dashboard (40% width)
- [x] Toggle button to show/hide chat
- [x] Floating button for mobile
- [x] Todo list remains visible (60% width)

### ✅ **MCP Tool Execution**
- [x] Backend uses 5 MCP tools (add, list, update, complete, delete)
- [x] Direct execution (no HTTP overhead)
- [x] Shared TaskService (same as REST API)
- [x] Proper error handling

### ✅ **Real-Time Sync**
- [x] Event bus for component communication
- [x] Chat emits events when tools execute
- [x] TodoList listens and refreshes
- [x] Visual indicators for both components

### ✅ **UI Preservation**
- [x] Login → Dashboard flow preserved
- [x] Todo CRUD UI fully functional
- [x] No routing controlled by chatbot
- [x] No visibility toggling by chatbot

### ✅ **No Breaking Changes**
- [x] Existing REST API still works
- [x] Todo list can operate independently
- [x] Chat is completely optional
- [x] Backward compatible

---

## 🎯 Key Takeaways

1. **Chatbot is a Feature**: Not the main app, embedded as optional sidebar
2. **MCP Tools**: Backend uses 5 tools for all task operations
3. **Shared Service**: TaskService used by both REST API and MCP tools
4. **Event-Based Sync**: Real-time updates via event bus
5. **Auth Reuse**: Same JWT token for all API calls
6. **Visual Feedback**: Indicators show when MCP tools execute
7. **No UI Control**: Chatbot NEVER controls routing or visibility
8. **Preserved Flow**: Login → Dashboard → See todos immediately

---

**Integration Status:** ✅ **COMPLETE AND WORKING**
