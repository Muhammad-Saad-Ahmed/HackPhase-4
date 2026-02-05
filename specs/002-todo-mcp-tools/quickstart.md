# Quickstart Guide: Todo MCP Tools

## Overview
This guide provides instructions for setting up and using the Todo MCP Tools server. The server exposes Todo application capabilities as MCP tools that can be consumed by reusable agents.

## Prerequisites
- Python 3.11+
- Poetry (dependency manager)
- Neon PostgreSQL account and database
- OpenAI API key (for embeddings)

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <repository-url>
cd <repository-directory>
```

### 2. Install Dependencies
```bash
poetry install
```

### 3. Configure Environment Variables
Create a `.env` file in the backend directory with the following variables:
```env
DATABASE_URL=postgresql+asyncpg://username:password@ep-xxx.us-east-1.aws.neon.tech/dbname
OPENAI_API_KEY=sk-xxx
MCP_SERVER_HOST=localhost
MCP_SERVER_PORT=8080
```

### 4. Run Database Migrations
```bash
cd backend
poetry run python -m src.core.database migrate
```

### 5. Start the MCP Server
```bash
cd backend
poetry run python -m src.main
```

## Using the Tools

### Registering Tools
The server automatically registers all available tools on startup. The following tools are available:

1. `add_task` - Create a new task
2. `list_tasks` - Retrieve a list of tasks
3. `complete_task` - Mark a task as completed
4. `update_task` - Modify task details
5. `delete_task` - Remove a task

### Example Tool Invocations

#### Adding a Task
```json
{
  "method": "tools/call",
  "params": {
    "name": "add_task",
    "arguments": {
      "title": "Buy groceries",
      "description": "Milk, eggs, bread"
    }
  }
}
```

#### Listing Tasks
```json
{
  "method": "tools/call",
  "params": {
    "name": "list_tasks",
    "arguments": {
      "status": "pending",
      "limit": 10,
      "offset": 0
    }
  }
}
```

#### Completing a Task
```json
{
  "method": "tools/call",
  "params": {
    "name": "complete_task",
    "arguments": {
      "task_id": 123
    }
  }
}
```

## Tool Discovery

The server supports semantic search for tool discovery. Tools are indexed with embeddings based on their descriptions and capabilities, allowing agents to find appropriate tools based on natural language queries.

Example discovery query:
```json
{
  "method": "tools/discover",
  "params": {
    "query": "create a new task",
    "limit": 3
  }
}
```

## Error Handling

All tools return structured error responses following the format:
```json
{
  "success": false,
  "error": "Error message",
  "code": "ERROR_CODE",
  "details": {
    "field": "field_name",
    "message": "Detailed error message"
  }
}
```

Common error codes:
- `VALIDATION_ERROR`: Input validation failed
- `TASK_NOT_FOUND`: Requested task does not exist
- `DATABASE_ERROR`: Database operation failed
- `NO_UPDATE_FIELDS`: No fields provided for update operation

## Development

### Running Tests
```bash
cd backend
poetry run pytest
```

### Adding New Tools
To add a new tool:
1. Create a new tool class inheriting from the base tool class
2. Implement the required methods
3. Register the tool in the tool registry
4. Add the corresponding contract file in the contracts directory

### Architecture
- Models: Defined using SQLModel in the `models` directory
- Services: Business logic in the `services` directory
- Tools: MCP tool implementations in the `mcp_tools` directory
- API: MCP server implementation in the `api` directory
- Core: Configuration, database, and utility functions in the `core` directory

## Troubleshooting

### Common Issues
1. **Database Connection Errors**: Verify your Neon PostgreSQL credentials in the `.env` file
2. **Tool Not Found**: Ensure the tool name matches exactly what's registered
3. **Validation Errors**: Check that all required fields are provided with correct types

### Logging
Server logs are written to the `logs/` directory. Enable debug logging by setting `LOG_LEVEL=debug` in your `.env` file.