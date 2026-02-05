"""
add_task MCP tool implementation.
"""
from ..mcp_tools.base import BaseTool, ResponseBuilder
from ..services.task_service import TaskService
from sqlmodel import create_engine
from ..core.config import settings
from typing import Dict, Any


class AddTaskTool(BaseTool):
    """
    MCP tool for adding a new task.
    """
    
    def __init__(self):
        # Create engine and task service (using sync URL for synchronous operations)
        self.engine = create_engine(settings.sync_database_url)
        self.task_service = TaskService(self.engine)
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the add_task operation.
        Expected kwargs: title (str), description (str, optional)
        """
        try:
            # Extract parameters
            title = kwargs.get('title')
            description = kwargs.get('description')
            
            # Validate required parameters
            if not title:
                return ResponseBuilder.error(
                    "Title is required and must be between 1 and 255 characters",
                    "VALIDATION_ERROR",
                    {"field": "title", "message": "Title is required"}
                )
            
            # Validate title length
            if len(title) < 1 or len(title) > 255:
                return ResponseBuilder.error(
                    "Title must be between 1 and 255 characters",
                    "VALIDATION_ERROR",
                    {"field": "title", "message": "Title length is invalid"}
                )
            
            # Validate description length if provided
            if description and len(description) > 1000:
                return ResponseBuilder.error(
                    "Description must be 1000 characters or less",
                    "VALIDATION_ERROR",
                    {"field": "description", "message": "Description too long"}
                )
            
            # Create the task
            task = self.task_service.create_task(title=title, description=description)
            
            # Return success response
            return ResponseBuilder.success(
                data=task.dict(),
                message="Task created successfully"
            )
            
        except Exception as e:
            return ResponseBuilder.error(
                f"Database error occurred: {str(e)}",
                "DATABASE_ERROR",
                {"message": "Failed to create task in database"}
            )