# Todo AI Chatbot (Reusable Intelligence + MCP)

A stateless chat backend that connects reusable agents to MCP tools using an external LLM provider. The system follows a conversation flow: load conversation, store user message, run agent, execute MCP tools, store assistant response, and return result.

## Features

- **Reusable Intelligence**: Agents and skills designed as reusable intelligence units that can be composed, chained, and applied across multiple contexts without modification
- **MCP Integration**: Connects to Model Context Protocol (MCP) tools for extended functionality
- **LLM Provider Agnostic**: Supports multiple LLM providers (OpenAI, Anthropic, etc.) through configuration
- **Stateless Architecture**: Completely stateless backend with all state persisted in Neon PostgreSQL
- **FastAPI Backend**: Built with FastAPI for high performance and automatic OpenAPI documentation
- **SQLModel ORM**: Uses SQLModel for type-safe database interactions
- **Chat UI (Phase III-C)**: ChatKit-powered web interface for natural conversations with conversation persistence across server restarts

## Tech Stack

- **Backend Framework**: FastAPI (Python 3.11+)
- **ORM**: SQLModel
- **Database**: Neon PostgreSQL
- **MCP SDK**: Official MCP SDK
- **Frontend Framework**: Next.js 16+ with React 19
- **Chat UI**: ChatKit (@chatscope/chat-ui-kit-react)
- **HTTP Client**: Axios
- **Authentication**: Better Auth (planned for future phase)

## Prerequisites

- Python 3.11+
- UV or Poetry (Python dependency manager)
- Node.js 18+ (for frontend)
- Neon PostgreSQL account and database
- Access to an LLM provider (OpenAI, Anthropic, etc.)

## Setup Instructions

Choose one of the following methods to run the application:

---

## 🌐 Method 1: Run in Browser (Development Mode)

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd Hackathon-Phase-3
```

### Step 2: Configure Environment Variables

**Backend Configuration:**

Create `backend/.env` file:

```env
# Database (remove SSL parameters - handled in code)
database_url=postgresql+asyncpg://username:password@ep-xxx.us-east-1.aws.neon.tech/dbname

# LLM Provider
llm_provider=openai  # or anthropic, google, openrouter, etc.
llm_model=gpt-4o  # or claude-3-opus, gemini-pro, etc.
llm_base_url=https://api.openai.com/v1  # Adjust for your provider
llm_api_key=sk-xxx  # Your LLM provider API key

# Server
server_host=0.0.0.0  # Bind to all interfaces
server_port=8000
log_level=INFO
```

**Frontend Configuration:**

Create `frontend/.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
BETTER_AUTH_SECRET=dev-secret-key-minimum-32-characters-long-for-development
BETTER_AUTH_URL=http://localhost:3000
```

**Important Notes:**
- For **Neon PostgreSQL**: SSL is configured automatically via `connect_args` in the code
- The application uses both `asyncpg` (async operations) and `psycopg` (sync MCP tools)
- The `database_url` should NOT include `sslmode` or `channel_binding` parameters

### Step 3: Install Backend Dependencies

```bash
cd backend
pip install -e .
pip install psycopg[binary]
```

### Step 4: Install Frontend Dependencies

```bash
cd ../frontend
npm install
```

### Step 5: Start Backend Server

Open **Terminal 1**:

```bash
cd backend

```uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

**Backend URLs:**
- API: http://localhost:8000
- Swagger Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

⚠️ **Important:** Access using `localhost:8000`, NOT `0.0.0.0:8000`

### Step 6: Start Frontend Server

Open **Terminal 2**:

```bash
cd frontend
npm run dev
```

**Frontend URLs:**
- App: http://localhost:3000
- Login: http://localhost:3000/login
- Chat: http://localhost:3000/chat

### Step 7: Test the Application

1. Open browser: http://localhost:3000/login
2. Login with any credentials (mock auth):
   - Email: `test@example.com`
   - Password: `password123`
3. You'll be redirected to the chat interface

---

## 🐳 Method 2: Run with Docker

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd Hackathon-Phase-3
```

### Step 2: Configure Environment Variables

Create `backend/.env` file (same as Method 1):

```env
database_url=postgresql+asyncpg://username:password@ep-xxx.us-east-1.aws.neon.tech/dbname
llm_provider=openai
llm_model=gpt-4o
llm_base_url=https://api.openai.com/v1
llm_api_key=sk-xxx
server_host=0.0.0.0
server_port=8000
log_level=INFO
```

### Step 3: Build and Run with Docker Compose

```bash
# Build and start all services
docker-compose up --build

# Or run in detached mode
docker-compose up -d --build
```

### Step 4: Access the Application

**Frontend:**
- App: http://localhost:3000
- Login: http://localhost:3000/login

**Backend:**
- API: http://localhost:8000
- Docs: http://localhost:8000/docs

### Docker Management Commands

```bash
# View logs
docker-compose logs -f

# View backend logs only
docker-compose logs -f backend

# View frontend logs only
docker-compose logs -f frontend

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Rebuild after code changes
docker-compose up --build
```

### Step 5: Test the Application

1. Open browser: http://localhost:3000/login
2. Login with any credentials:
   - Email: `test@example.com`
   - Password: `password123`
3. Start chatting!

---

## API Usage

### Sending a Message

Send a POST request to the chat endpoint:

```bash
curl -X POST "http://localhost:8000/api/user123/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, can you help me create a task?"
  }'
```

### Continuing a Conversation

To continue an existing conversation, include the conversation_id:

```bash
curl -X POST "http://localhost:8000/api/user123/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "conv-abc123xyz",
    "message": "Can you update that task?"
  }'
```

### Expected Response Format

The API returns responses in the following format:

```json
{
  "conversation_id": "conv-abc123xyz",
  "response": "Sure, I've created a task called 'buy groceries' for you.",
  "tool_calls": [
    {
      "tool_name": "add_task",
      "arguments": {
        "title": "buy groceries",
        "description": "Get milk, eggs, and bread"
      },
      "result": {
        "success": true,
        "data": {
          "id": 123,
          "title": "buy groceries",
          "description": "Get milk, eggs, and bread",
          "status": "pending",
          "created_at": "2023-10-05T14:48:00.000Z"
        },
        "message": "Task created successfully"
      }
    }
  ]
}
```

## Architecture Components

### LLM Client
The provider-agnostic LLM client handles communication with external LLM providers using configuration from environment variables. It supports multiple providers through a unified interface.

### MCP Client
The MCP client integrates with the Official MCP SDK to execute tools exposed by various services. It handles tool discovery, execution, and result processing.

### Agent Runner
The AgentRunner abstraction manages the complete conversation flow:
1. Load conversation context
2. Store user message
3. Run agent with LLM
4. Execute MCP tools if identified
5. Store assistant response
6. Return result to user

### Conversation Service
Handles conversation state management while maintaining statelessness at the server level. Uses conversation_id to track context across exchanges.

## Development

### Running Tests

```bash
cd backend
poetry run pytest
```

### Adding New LLM Providers

To add support for a new LLM provider:
1. Extend the provider-agnostic LLM client interface
2. Implement the provider-specific adapter
3. Add configuration options to handle provider-specific settings

### Adding New MCP Tools

To integrate new MCP tools:
1. Register the tool with the MCP client
2. Ensure the LLM is trained to recognize when to use the tool
3. Handle the tool's response format in the conversation flow

## Deployment

### Production Environment Variables

For production deployments, ensure all environment variables are properly set:

```env
# Database - Use your production Neon connection string
database_url=postgresql+asyncpg://user:password@production-host/dbname

# LLM Provider
llm_provider=openai
llm_model=gpt-4o
llm_base_url=https://api.openai.com/v1
llm_api_key=sk-prod-xxx

# Server
server_host=0.0.0.0
server_port=8000
log_level=INFO

# Frontend (if deploying separately)
NEXT_PUBLIC_API_URL=https://your-backend-domain.com
```

### Docker Deployment

#### 1. Create Dockerfile for Backend

Create `backend/Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml ./
COPY src ./src

# Install Python dependencies
RUN pip install --no-cache-dir -e .
RUN pip install --no-cache-dir psycopg[binary]

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 2. Create docker-compose.yml

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - database_url=${DATABASE_URL}
      - llm_provider=${LLM_PROVIDER}
      - llm_model=${LLM_MODEL}
      - llm_api_key=${LLM_API_KEY}
      - llm_base_url=${LLM_BASE_URL}
    env_file:
      - ./backend/.env

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8000
    depends_on:
      - backend
```

#### 3. Deploy with Docker

```bash
# Build and start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Platform-Specific Deployments

#### Railway

1. Install Railway CLI:
```bash
npm install -g @railway/cli
```

2. Login and initialize:
```bash
railway login
railway init
```

3. Add environment variables in Railway dashboard:
   - `database_url`
   - `llm_api_key`
   - `llm_provider`
   - `llm_model`
   - `llm_base_url`

4. Deploy:
```bash
railway up
```

#### Render

1. Create `render.yaml` in the root:

```yaml
services:
  - type: web
    name: todo-ai-backend
    env: python
    buildCommand: "cd backend && pip install -e . && pip install psycopg[binary]"
    startCommand: "cd backend && uvicorn src.main:app --host 0.0.0.0 --port $PORT"
    envVars:
      - key: database_url
        sync: false
      - key: llm_api_key
        sync: false
      - key: llm_provider
        value: openai
      - key: llm_model
        value: gpt-4o

  - type: web
    name: todo-ai-frontend
    env: node
    buildCommand: "cd frontend && npm install && npm run build"
    startCommand: "cd frontend && npm start"
    envVars:
      - key: NEXT_PUBLIC_API_URL
        value: https://todo-ai-backend.onrender.com
```

2. Connect your GitHub repository in Render dashboard
3. Add secret environment variables in Render UI

#### Vercel (Frontend) + Railway/Render (Backend)

**Frontend on Vercel:**

1. Install Vercel CLI:
```bash
npm install -g vercel
```

2. Deploy frontend:
```bash
cd frontend
vercel --prod
```

3. Set environment variable in Vercel dashboard:
   - `NEXT_PUBLIC_API_URL`: Your backend URL

**Backend on Railway/Render:**
Follow the Railway or Render instructions above.

#### AWS / GCP / Azure

For cloud platforms, you'll need to:

1. **Set up a managed PostgreSQL instance** (or continue using Neon)
2. **Deploy backend** using:
   - AWS: ECS/Fargate or Elastic Beanstalk
   - GCP: Cloud Run or App Engine
   - Azure: Container Instances or App Service

3. **Deploy frontend** using:
   - AWS: Amplify or S3 + CloudFront
   - GCP: Firebase Hosting or Cloud Storage
   - Azure: Static Web Apps

4. **Configure CORS** in your backend to allow frontend domain

### SSL/HTTPS Configuration

For production, always use HTTPS:

1. **Using a reverse proxy (recommended):**
   - Deploy behind Nginx or Caddy
   - Configure SSL certificates (Let's Encrypt)

2. **Platform-managed SSL:**
   - Railway, Render, Vercel provide automatic HTTPS
   - No additional configuration needed

### Database Migrations in Production

```bash
# SSH into your production server or use platform CLI
cd backend

# Run migrations
python -m src.core.database migrate

# Or use Alembic for versioned migrations
alembic upgrade head
```

### Health Checks

Add a health check endpoint for monitoring:

```bash
# Check if server is running
curl https://your-domain.com/health

# Check API documentation
curl https://your-domain.com/docs
```

### Monitoring & Logging

- Use structured logging (already configured with `structlog`)
- Set up log aggregation (e.g., Datadog, CloudWatch, Papertrail)
- Monitor API performance and errors
- Set up alerts for critical failures

## Troubleshooting

### Common Issues

1. **Cannot Access Server at `0.0.0.0:8000`**
   - **Problem**: `ERR_ADDRESS_INVALID` when accessing `http://0.0.0.0:8000`
   - **Solution**: Use `http://localhost:8000` or `http://127.0.0.1:8000` instead
   - **Explanation**: `0.0.0.0` is a binding address for the server, not a browsable address

2. **Database Connection Errors**
   - **Error**: `connect() got an unexpected keyword argument 'sslmode'`
   - **Solution**: Remove SSL parameters from `database_url` in `.env` file
   - **Correct format**: `postgresql+asyncpg://user:pass@host/db` (no `?sslmode=require`)
   - **Note**: SSL is configured automatically in `src/core/database.py` via `connect_args`

3. **Missing `psycopg` Driver**
   - **Error**: `No module named 'psycopg'`
   - **Solution**: Install the sync driver for MCP tools
   ```bash
   pip install psycopg[binary]
   ```

4. **LLM Provider Connection Errors**
   - **Problem**: API key or endpoint errors
   - **Solution**: Verify your API keys and endpoint URLs in the `.env` file
   - Check the correct base URL for your provider:
     - OpenAI: `https://api.openai.com/v1`
     - Anthropic: `https://api.anthropic.com`
     - OpenRouter: `https://openrouter.ai/api/v1`

5. **MCP Tool Execution Failures**
   - **Problem**: Tools not working or timing out
   - **Solution**: Verify that the required MCP tools are available and properly configured
   - Check database connection (tools need sync database access)

6. **Long Response Times**
   - **Problem**: Slow API responses
   - **Solution**: Check the performance of your LLM provider and consider optimizing prompts
   - Use faster models for testing (e.g., `gpt-4o-mini` instead of `gpt-4o`)

7. **CORS Errors (Frontend)**
   - **Problem**: Browser blocks API requests from frontend
   - **Solution**: Ensure backend CORS is configured to allow frontend origin
   - Check `src/main.py` for CORS middleware configuration

### Logging
Server logs are written to the `logs/` directory. Enable debug logging by setting `LOG_LEVEL=DEBUG` in your `.env` file.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.