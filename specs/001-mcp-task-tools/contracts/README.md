# MCP Tool Contracts

This directory contains JSON Schema definitions for all MCP tools in the Task Management system.

## Overview

Each JSON file defines the input and output schema for a single MCP tool. These schemas serve multiple purposes:

1. **MCP SDK Registration**: Schemas are used to register tools with the Official MCP SDK
2. **Input Validation**: Agent requests are validated against input schemas before execution
3. **Documentation**: AI agents use schemas to understand tool capabilities and parameters
4. **Type Safety**: Pydantic models are generated from these schemas for runtime validation

## Tool Inventory

| Tool | Purpose | Input | Output |
|------|---------|-------|--------|
| `add_task` | Create new task | `title` (required), `description` (optional) | Created task with ID and timestamps |
| `list_tasks` | Query tasks | `status` (optional filter) | Array of tasks ordered by creation date |
| `update_task` | Modify task | `task_id`, `title` and/or `description` | Updated task details |
| `complete_task` | Mark complete | `task_id` | Completed task with completion timestamp |
| `delete_task` | Remove task | `task_id` | Deletion confirmation |

## Schema Format

All schemas follow this structure:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "tool_name",
  "description": "What the tool does",
  "type": "object",
  "properties": {
    "input": {
      "type": "object",
      "properties": { /* input parameters */ },
      "required": [ /* required fields */ ]
    },
    "output": {
      "oneOf": [
        { /* success response schema */ },
        { /* error response schema */ }
      ]
    }
  }
}
```

## Response Format Convention

All tools return responses in this unified structure:

### Success Response
```json
{
  "success": true,
  "data": { /* tool-specific data */ },
  "message": "Human-readable success message"
}
```

### Error Response
```json
{
  "success": false,
  "error": "Human-readable error message",
  "code": "MACHINE_READABLE_CODE",
  "details": { /* optional context */ }
}
```

## Error Codes

| Code | Meaning | Used By |
|------|---------|---------|
| `VALIDATION_ERROR` | Input validation failed | All tools |
| `NOT_FOUND` | Task ID does not exist | `update_task`, `complete_task`, `delete_task` |
| `DATABASE_ERROR` | Database operation failed | All tools |
| `INTERNAL_ERROR` | Unexpected server error | All tools |

## Usage in Implementation

### 1. Pydantic Model Generation

```python
from pydantic import BaseModel, Field

class AddTaskInput(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=1000)

class TaskResponse(BaseModel):
    id: int
    title: str
    description: str | None
    status: str
    created_at: datetime
    completed_at: datetime | None
```

### 2. MCP SDK Registration

```python
from mcp import Server

server = Server("task-manager")

@server.tool("add_task")
async def add_task_handler(title: str, description: str | None = None):
    # Schema validation happens automatically
    # Tool logic here
    pass
```

### 3. Response Building

```python
from backend.src.mcp_tools.base import ResponseBuilder

# Success
return ResponseBuilder.success(
    data=task.dict(),
    message="Task created successfully"
)

# Error
return ResponseBuilder.error(
    error_msg="Task not found",
    code="NOT_FOUND",
    details={"task_id": task_id}
)
```

## Validation Rules Summary

### Common Constraints
- **task_id**: Integer, minimum value 1
- **title**: String, 1-255 characters
- **description**: String or null, max 1000 characters
- **status**: Enum: "pending" or "completed"

### Type Coercion
- Empty strings for description treated as null
- Whitespace trimmed from title and description
- Invalid status values rejected with VALIDATION_ERROR

## Testing Tool Contracts

Each contract can be validated independently:

```bash
# Validate schema format
jsonschema -i contracts/add_task.json

# Test tool invocation
curl -X POST http://localhost:8000/mcp/tool/add_task \
  -H "Content-Type: application/json" \
  -d '{"title": "Test task", "description": "Test description"}'
```

## Extending Contracts

When adding new tools:

1. Create a new `{tool_name}.json` file in this directory
2. Follow the schema format above
3. Define input parameters with validation rules
4. Define success and error response structures
5. Add tool to the inventory table in this README
6. Update Pydantic models in `backend/src/mcp_tools/schemas.py`
7. Register tool with MCP SDK in `backend/src/mcp_tools/server.py`

## References

- [JSON Schema Specification](https://json-schema.org/specification.html)
- [MCP SDK Documentation](https://github.com/modelcontextprotocol/python-sdk)
- [Pydantic JSON Schema](https://docs.pydantic.dev/latest/concepts/json_schema/)
