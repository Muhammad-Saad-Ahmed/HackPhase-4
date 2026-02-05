# Quickstart Guide: Chat Agent Connector

## Overview
This guide provides instructions for setting up and using the Chat Agent Connector service. The service connects reusable agents to MCP tools using an external LLM provider through a stateless chat backend.

## Prerequisites
- Python 3.11+
- Poetry (dependency manager)
- Neon PostgreSQL account and database
- Access to an LLM provider (OpenAI, Anthropic, etc.)

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <repository-url>
cd <repository-directory>
```

### 2. Install Dependencies
```bash
cd backend
poetry install
```

### 3. Configure Environment Variables
Create a `.env` file in the backend directory with the following variables:
```env
DATABASE_URL=postgresql+asyncpg://username:password@ep-xxx.us-east-1.aws.neon.tech/dbname
LLM_PROVIDER=openai  # or anthropic, google, etc.
LLM_MODEL=gpt-4o  # or claude-3-opus, gemini-pro, etc.
LLM_BASE_URL=https://api.openai.com/v1  # Adjust for your provider
LLM_API_KEY=sk-xxx
SERVER_HOST=localhost
SERVER_PORT=8000
LOG_LEVEL=INFO
```

### 4. Run Database Migrations
```bash
cd backend
poetry run python -m src.core.database migrate
```

### 5. Start the Chat Service
```bash
cd backend
poetry run python -m src.main
```

## Using the Chat API

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

## Error Handling

The service handles various error conditions gracefully:

- **LLM Provider Unavailable**: Returns appropriate error message when LLM provider is unreachable
- **MCP Tool Execution Failures**: Handles tool execution errors and continues conversation appropriately
- **Malformed Requests**: Validates input and returns clear error messages
- **Authentication Failures**: Handles LLM provider authentication issues

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

### Architecture
- Models: Defined using SQLModel in the `models` directory
- Services: Business logic in the `services` directory (LLM client, MCP client, conversation service, agent runner)
- API: Chat endpoint implementation in the `api` directory
- Core: Configuration, database, and utility functions in the `core` directory

## Troubleshooting

### Common Issues
1. **LLM Provider Connection Errors**: Verify your API keys and endpoint URLs in the `.env` file
2. **Database Connection Errors**: Check your Neon PostgreSQL credentials in the `.env` file
3. **MCP Tool Execution Failures**: Verify that the required MCP tools are available and properly configured
4. **Long Response Times**: Check the performance of your LLM provider and consider optimizing prompts

### Logging
Server logs are written to the `logs/` directory. Enable debug logging by setting `LOG_LEVEL=DEBUG` in your `.env` file.