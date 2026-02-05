"""
Base tool class for MCP tools.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict
from pydantic import BaseModel
import json
from datetime import datetime, date
import decimal


def serialize_datetime(obj):
    """
    Serialize datetime objects to ISO format strings.
    """
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    elif isinstance(obj, decimal.Decimal):
        return float(obj)
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


class BaseTool(ABC):
    """
    Abstract base class for all MCP tools.
    """

    @abstractmethod
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the tool with the given parameters.
        """
        pass


class ResponseBuilder:
    """
    Helper class to build standardized responses.
    """
    
    @staticmethod
    def success(data: Any, message: str = None) -> Dict[str, Any]:
        """
        Build a success response.
        """
        import json
        from pydantic import BaseModel

        def make_serializable(obj):
            """Recursively make objects JSON serializable."""
            if isinstance(obj, BaseModel):
                # Use Pydantic's built-in serialization with proper datetime handling
                return obj.model_dump(mode='json')
            elif isinstance(obj, (list, tuple)):
                return [make_serializable(item) for item in obj]
            elif isinstance(obj, dict):
                return {key: make_serializable(value) for key, value in obj.items()}
            elif isinstance(obj, (datetime, date)):
                return obj.isoformat()
            elif isinstance(obj, decimal.Decimal):
                return float(obj)
            else:
                return obj

        # Make the data JSON serializable
        serialized_data = make_serializable(data)

        return {
            "success": True,
            "data": serialized_data,
            "message": message
        }
    
    @staticmethod
    def error(error_msg: str, code: str, details: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Build an error response.
        """
        return {
            "success": False,
            "error": error_msg,
            "code": code,
            "details": details
        }