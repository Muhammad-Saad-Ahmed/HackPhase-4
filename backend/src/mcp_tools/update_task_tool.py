"""
update_task MCP tool implementation.
"""
from ..mcp_tools.base import BaseTool, ResponseBuilder
from ..services.task_service import TaskService
from sqlmodel import create_engine
from ..core.config import settings
from typing import Dict, Any


class UpdateTaskTool(BaseTool):
    """
    MCP tool for updating a task.
    """
    
    def __init__(self):
        # Create engine and task service (using sync URL for synchronous operations)
        self.engine = create_engine(settings.sync_database_url)
        self.task_service = TaskService(self.engine)
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the update_task operation.
        Expected kwargs: task_id (int), title (str, optional), description (str, optional)
        """
        try:
            # Extract parameters
            task_id = kwargs.get('task_id')
            title = kwargs.get('title')
            description = kwargs.get('description')
            
            # Validate required parameters
            if task_id is None:
                return ResponseBuilder.error(
                    "Task ID is required",
                    "VALIDATION_ERROR",
                    {"field": "task_id", "message": "Task ID is required"}
                )
            
            # Validate that at least one field to update is provided
            if title is None and description is None:
                return ResponseBuilder.error(
                    "At least one field (title or description) must be provided",
                    "NO_UPDATE_FIELDS",
                    {"message": "No fields to update"}
                )
            
            # Validate task_id type and range
            if not isinstance(task_id, int) or task_id < 1:
                return ResponseBuilder.error(
                    "Task ID must be a positive integer",
                    "VALIDATION_ERROR",
                    {"field": "task_id", "message": "Task ID must be a positive integer"}
                )
            
            # Validate title if provided
            if title is not None:
                if not isinstance(title, str) or len(title) < 1 or len(title) > 255:
                    return ResponseBuilder.error(
                        "Title must be between 1 and 255 characters",
                        "VALIDATION_ERROR",
                        {"field": "title", "message": "Title must be between 1 and 255 characters"}
                    )
            
            # Validate description if provided
            if description is not None:
                if not isinstance(description, str) or len(description) > 1000:
                    return ResponseBuilder.error(
                        "Description must be 1000 characters or less",
                        "VALIDATION_ERROR",
                        {"field": "description", "message": "Description too long"}
                    )
            
            # Update the task
            task = self.task_service.update_task(task_id=task_id, title=title, description=description)
            
            # Return success response
            return ResponseBuilder.success(
                data=task.dict(),
                message="Task updated successfully"
            )
            
        except ValueError as e:
            # Handle case where task doesn't exist
            if "not found" in str(e).lower():
                return ResponseBuilder.error(
                    "Task not found",
                    "TASK_NOT_FOUND",
                    {"message": "No task found with the provided ID"}
                )
            else:
                raise e
        except Exception as e:
            return ResponseBuilder.error(
                f"Database error occurred: {str(e)}",
                "DATABASE_ERROR",
                {"message": "Failed to update task in database"}
            )