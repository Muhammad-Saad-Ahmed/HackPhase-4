"""
Direct MCP tool execution without HTTP server.
Bypasses the HTTP MCP server and calls tools directly for better performance.
"""
from typing import Dict, Any, List
from ..mcp_tools.add_task_tool import AddTaskTool
from ..mcp_tools.list_tasks_tool import ListTasksTool
from ..mcp_tools.update_task_tool import UpdateTaskTool
from ..mcp_tools.complete_task_tool import CompleteTaskTool
from ..mcp_tools.delete_task_tool import DeleteTaskTool


class MCPTaskExecutor:
    """Direct execution of MCP tasks without HTTP overhead."""

    def __init__(self):
        # Initialize all tool instances
        self.tools = {
            "add_task": AddTaskTool(),
            "list_tasks": ListTasksTool(),
            "update_task": UpdateTaskTool(),
            "complete_task": CompleteTaskTool(),
            "delete_task": DeleteTaskTool(),
        }

    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an MCP tool directly."""
        try:
            # Get the tool instance
            if tool_name not in self.tools:
                return {
                    "success": False,
                    "error": f"Tool '{tool_name}' not found",
                    "message": f"Unknown tool: {tool_name}"
                }

            tool = self.tools[tool_name]

            # Execute the tool
            result = await tool.execute(**arguments)

            return result

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to execute tool {tool_name}"
            }

    async def list_available_tools(self) -> List[Dict[str, Any]]:
        """List all available MCP tools."""
        return [
            {
                "name": "add_task",
                "description": "Create a new task with title and optional description",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "Task title"},
                        "description": {"type": "string", "description": "Optional task description"}
                    },
                    "required": ["title"]
                }
            },
            {
                "name": "list_tasks",
                "description": "List all tasks or filter by status",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "enum": ["pending", "completed"], "description": "Filter by status"}
                    }
                }
            },
            {
                "name": "update_task",
                "description": "Update task title and/or description by ID",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "integer", "description": "Task ID"},
                        "title": {"type": "string", "description": "New task title"},
                        "description": {"type": "string", "description": "New task description"}
                    },
                    "required": ["task_id"]
                }
            },
            {
                "name": "complete_task",
                "description": "Mark a task as completed",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "integer", "description": "Task ID to complete"}
                    },
                    "required": ["task_id"]
                }
            },
            {
                "name": "delete_task",
                "description": "Delete a task permanently",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "integer", "description": "Task ID to delete"}
                    },
                    "required": ["task_id"]
                }
            }
        ]

    async def close(self) -> None:
        """Cleanup (no-op for direct execution)."""
        pass
