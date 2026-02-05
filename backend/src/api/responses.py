"""
Base response models for success and error responses.
"""
from pydantic import BaseModel
from typing import Any, Optional, Dict, List


class SuccessResponse(BaseModel):
    success: bool = True
    data: Any
    message: Optional[str] = None


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    code: str
    details: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    conversation_id: str
    response: str
    tool_calls: List[Dict[str, Any]] = []