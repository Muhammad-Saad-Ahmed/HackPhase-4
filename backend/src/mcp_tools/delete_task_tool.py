"""
delete_task MCP tool implementation.
"""
from ..mcp_tools.base import BaseTool, ResponseBuilder
from ..services.task_service import TaskService
from sqlmodel import create_engine
from ..core.config import settings
from typing import Dict, Any


class DeleteTaskTool(BaseTool):
    """
    MCP tool for deleting a task.
    """
    
    def __init__(self):
        # Create engine and task service (using sync URL for synchronous operations)
        self.engine = create_engine(settings.sync_database_url)
        self.task_service = TaskService(self.engine)
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the delete_task operation.
        Expected kwargs: task_id (int)
        """
        try:
            # Extract parameters
            task_id = kwargs.get('task_id')
            
            # Validate required parameters
            if task_id is None:
                return ResponseBuilder.error(
                    "Task ID is required",
                    "VALIDATION_ERROR",
                    {"field": "task_id", "message": "Task ID is required"}
                )
            
            # Validate task_id type and range
            if not isinstance(task_id, int) or task_id < 1:
                return ResponseBuilder.error(
                    "Task ID must be a positive integer",
                    "VALIDATION_ERROR",
                    {"field": "task_id", "message": "Task ID must be a positive integer"}
                )
            
            # Delete the task
            success = self.task_service.delete_task(task_id=task_id)
            
            if success:
                # Return success response
                return ResponseBuilder.success(
                    data={"deleted_id": task_id},
                    message="Task deleted successfully"
                )
            else:
                # This shouldn't happen if delete_task is implemented correctly
                return ResponseBuilder.error(
                    "Task deletion failed",
                    "DATABASE_ERROR",
                    {"message": "Failed to delete task from database"}
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
                {"message": "Failed to delete task from database"}
            )