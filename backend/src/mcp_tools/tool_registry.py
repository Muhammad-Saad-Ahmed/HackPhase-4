"""
MCP tool registry for managing and discovering tools.
"""
from typing import Dict, List, Type
from .base import BaseTool
from .add_task_tool import AddTaskTool
from .list_tasks_tool import ListTasksTool
from .complete_task_tool import CompleteTaskTool
from .update_task_tool import UpdateTaskTool
from .delete_task_tool import DeleteTaskTool


class ToolRegistry:
    """
    Registry for managing MCP tools.
    """
    
    def __init__(self):
        self._tools: Dict[str, Type[BaseTool]] = {}
        self._instances: Dict[str, BaseTool] = {}
        self._descriptions: Dict[str, str] = {}
        
        # Register all available tools
        self._register_default_tools()
    
    def _register_default_tools(self):
        """
        Register all default tools for the todo application.
        """
        # Add task tool
        self.register_tool(
            name="add_task",
            tool_class=AddTaskTool,
            description="Create a new task with a title and optional description. The task will have 'pending' status by default."
        )
        
        # List tasks tool
        self.register_tool(
            name="list_tasks",
            tool_class=ListTasksTool,
            description="Retrieve a list of tasks with optional filtering by status (pending/completed/all) and pagination support."
        )
        
        # Complete task tool
        self.register_tool(
            name="complete_task",
            tool_class=CompleteTaskTool,
            description="Mark a task as completed by its ID. This operation is idempotent - calling it multiple times on the same task will return success."
        )
        
        # Update task tool
        self.register_tool(
            name="update_task",
            tool_class=UpdateTaskTool,
            description="Update a task's title or description by its ID. At least one field (title or description) must be provided."
        )
        
        # Delete task tool
        self.register_tool(
            name="delete_task",
            tool_class=DeleteTaskTool,
            description="Permanently remove a task from the system by its ID."
        )
    
    def register_tool(self, name: str, tool_class: Type[BaseTool], description: str):
        """
        Register a new tool in the registry.
        """
        self._tools[name] = tool_class
        self._descriptions[name] = description
        
        # Create an instance of the tool
        self._instances[name] = tool_class()
    
    def get_tool(self, name: str) -> BaseTool:
        """
        Get a tool instance by name.
        """
        if name not in self._instances:
            raise ValueError(f"Tool '{name}' not found in registry")
        
        return self._instances[name]
    
    def get_tool_description(self, name: str) -> str:
        """
        Get the description of a tool by name.
        """
        if name not in self._descriptions:
            raise ValueError(f"Description for tool '{name}' not found in registry")
        
        return self._descriptions[name]
    
    def list_tool_names(self) -> List[str]:
        """
        Get a list of all registered tool names.
        """
        return list(self._tools.keys())
    
    def get_all_descriptions(self) -> Dict[str, str]:
        """
        Get all tool descriptions.
        """
        return self._descriptions.copy()


# Global tool registry instance
tool_registry = ToolRegistry()