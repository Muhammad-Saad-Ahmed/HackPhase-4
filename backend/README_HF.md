---
title: HackPhase-4 Backend
emoji: 🤖
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
license: mit
app_port: 7860
---

# Todo AI Chatbot Backend

A stateless chat backend that connects reusable agents to MCP tools using an external LLM provider.

## Features

- **Reusable Intelligence**: Agents and skills designed as reusable intelligence units
- **MCP Integration**: Connects to Model Context Protocol (MCP) tools for extended functionality
- **LLM Provider Agnostic**: Supports multiple LLM providers (OpenAI, Anthropic, etc.)
- **Stateless Architecture**: Completely stateless backend with all state persisted in PostgreSQL
- **FastAPI Backend**: Built with FastAPI for high performance

## Configuration

This Space requires the following environment variables to be set:

### Required Environment Variables

1. **Database Configuration**
   ```
   database_url=postgresql+asyncpg://user:password@host:5432/dbname
   ```

2. **LLM Provider Configuration**
   ```
   llm_provider=openai
   llm_model=gpt-4o
   llm_base_url=https://api.openai.com/v1
   llm_api_key=YOUR_API_KEY_HERE
   ```

3. **Server Configuration**
   ```
   server_host=0.0.0.0
   server_port=7860
   log_level=INFO
   ```

4. **Authentication**
   ```
   BETTER_AUTH_SECRET=your-secret-key-here
   ```

## Setup Instructions

1. Go to the **Settings** tab in this Space
2. Add the required environment variables as **Secrets**
3. The Space will automatically rebuild and deploy

## API Endpoints

Once deployed, the following endpoints will be available:

- `GET /` - Root endpoint with service information
- `GET /health` - Health check endpoint
- `GET /docs` - Interactive API documentation (Swagger UI)
- `POST /api/{user_id}/chat` - Send chat messages
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user

## Testing the API

You can test the API using the interactive documentation at `/docs` or with curl:

```bash
curl -X POST "https://huggingface.co/spaces/MSK9218/HackPhase-4/api/{user_id}/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, can you help me create a task?"}'
```

## Local Development

To run this backend locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables in .env file
cp .env.example .env
# Edit .env with your configuration

# Run the server
python app.py
```

## Tech Stack

- **Framework**: FastAPI (Python 3.11+)
- **ORM**: SQLModel
- **Database**: PostgreSQL (Neon)
- **MCP SDK**: Official MCP SDK
- **Authentication**: JWT-based auth

## License

MIT License
