"""
list_tasks MCP tool implementation.
"""
from ..mcp_tools.base import BaseTool, ResponseBuilder
from ..services.task_service import TaskService
from sqlmodel import create_engine
from ..core.config import settings
from typing import Dict, Any


class ListTasksTool(BaseTool):
    """
    MCP tool for listing tasks.
    """
    
    def __init__(self):
        # Create engine and task service (using sync URL for synchronous operations)
        self.engine = create_engine(settings.sync_database_url)
        self.task_service = TaskService(self.engine)
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the list_tasks operation.
        Expected kwargs: status (str, optional), limit (int, optional), offset (int, optional)
        """
        try:
            # Extract parameters with defaults
            status = kwargs.get('status', 'all')
            limit = kwargs.get('limit', 50)
            offset = kwargs.get('offset', 0)

            # Handle None case - treat as 'all'
            if status is None:
                status = 'all'

            # Validate parameters
            if status not in ['all', 'pending', 'completed']:
                return ResponseBuilder.error(
                    f"Invalid status '{status}'. Must be 'all', 'pending', or 'completed'",
                    "VALIDATION_ERROR",
                    {"field": "status", "message": "Invalid status value"}
                )
            
            # Validate limit
            if not isinstance(limit, int) or limit < 1 or limit > 100:
                return ResponseBuilder.error(
                    "Limit must be between 1 and 100",
                    "VALIDATION_ERROR",
                    {"field": "limit", "message": "Limit must be between 1 and 100"}
                )
            
            # Validate offset
            if not isinstance(offset, int) or offset < 0:
                return ResponseBuilder.error(
                    "Offset must be a non-negative integer",
                    "VALIDATION_ERROR",
                    {"field": "offset", "message": "Offset must be a non-negative integer"}
                )
            
            # Get the tasks
            tasks = self.task_service.get_tasks(status=status, limit=limit, offset=offset)
            
            # Return success response
            return ResponseBuilder.success(
                data=[task.dict() for task in tasks],
                message="Tasks retrieved successfully"
            )
            
        except Exception as e:
            return ResponseBuilder.error(
                f"Database error occurred: {str(e)}",
                "DATABASE_ERROR",
                {"message": "Failed to retrieve tasks from database"}
            )