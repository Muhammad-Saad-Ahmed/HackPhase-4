"""
complete_task MCP tool implementation.
"""
from ..mcp_tools.base import BaseTool, ResponseBuilder
from ..services.task_service import TaskService
from sqlmodel import create_engine
from ..core.config import settings
from typing import Dict, Any


class CompleteTaskTool(BaseTool):
    """
    MCP tool for completing a task.
    """
    
    def __init__(self):
        # Create engine and task service (using sync URL for synchronous operations)
        self.engine = create_engine(settings.sync_database_url)
        self.task_service = TaskService(self.engine)
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the complete_task operation.
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
            
            # Complete the task (this is idempotent as per requirements)
            task = self.task_service.complete_task(task_id=task_id)
            
            # Return success response
            return ResponseBuilder.success(
                data=task.dict(),
                message="Task completed successfully"
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