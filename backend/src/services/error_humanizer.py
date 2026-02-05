"""
Error humanizer service for translating technical errors to user-friendly messages.
"""
from typing import Dict, Any, Optional
import re


class ErrorHumanizer:
    """Translate technical errors to user-friendly messages."""

    ERROR_TEMPLATES = {
        "validation_error": "That {field} is too long. Please keep it under {limit} characters.",
        "not_found": "I couldn't find task {reference}. {suggestion}",
        "rate_limit": "Too many requests right now. Please wait a moment and try again.",
        "database_error": "I'm having trouble saving that right now. Let's try again in a moment.",
        "internal_error": "Something went wrong on my end. Please try again.",
        "connection_timeout": "I couldn't connect to the service right now. Please try again in a moment.",
        "permission_denied": "You don't have permission to do that.",
        "unprocessable_entity": "I couldn't process that request. Please check your input and try again.",
        "bad_request": "I need more information: {details}",
        "service_unavailable": "The service is temporarily unavailable. Please try again in a moment."
    }

    SUGGESTIONS = [
        "Try 'show my tasks' to see what's available.",
        "Would you like to see your current tasks?",
        "Maybe list tasks first to see what's available.",
        "Could you try rephrasing your request?",
        "Try 'show my tasks' to see what you can work with.",
        "Let me know if you'd like to create a new task instead."
    ]

    @staticmethod
    def humanize(error: Exception, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Translate technical error to user-friendly message.

        Args:
            error: Exception to translate
            context: Additional context for error translation

        Returns:
            User-friendly error message
        """
        error_type = type(error).__name__.lower()
        error_str = str(error).lower()

        # Check for specific error type matches
        for key, template in ErrorHumanizer.ERROR_TEMPLATES.items():
            if key in error_type or key in error_str:
                return ErrorHumanizer._format_message(template, error, context)

        # Check for common patterns in error message
        common_patterns = [
            ("not found", "not_found"),
            ("validation", "validation_error"),
            ("database", "database_error"),
            ("connection", "connection_timeout"),
            ("timeout", "connection_timeout"),
            ("rate limit", "rate_limit"),
            ("permission", "permission_denied")
        ]

        for pattern, error_key in common_patterns:
            if pattern in error_str:
                template = ErrorHumanizer.ERROR_TEMPLATES[error_key]
                return ErrorHumanizer._format_message(template, error, context)

        # Default fallback
        return ErrorHumanizer._get_random_suggestion()

    @staticmethod
    def _format_message(template: str, error: Exception, context: Optional[Dict[str, Any]]) -> str:
        """Format error message with context."""
        error_str = str(error)

        # Extract field and limit from validation errors
        if "validation" in template.lower() or "long" in template.lower():
            # Try to extract field name and limit from error message
            field_match = re.search(r"'([^']+)'", error_str)
            limit_match = re.search(r'(\d+)', error_str)

            field = field_match.group(1) if field_match else "input"
            limit = limit_match.group(1) if limit_match else "1000"

            return template.format(field=field, limit=limit)

        # Extract reference from not found errors
        if "not found" in template.lower():
            # Try to extract task ID from error string
            ref_match = re.search(r'task[:\s]*(\d+)', error_str, re.IGNORECASE)
            if ref_match:
                ref = f"#{ref_match.group(1)}"
            else:
                # If no ID found, use generic reference
                ref = "that task"

            suggestion = ErrorHumanizer._get_random_suggestion()
            try:
                return template.format(reference=ref, suggestion=suggestion)
            except KeyError:
                # If template doesn't have placeholders, return as is with suggestion
                return f"{template} {suggestion}"

        # Handle bad request with details
        if "bad_request" in template.lower() and context:
            details = context.get("details", "more information")
            return template.format(details=details)

        return template

    @staticmethod
    def _get_random_suggestion() -> str:
        """Get a random helpful suggestion."""
        import random
        return random.choice(ErrorHumanizer.SUGGESTIONS)

    @staticmethod
    def translate_error_code(error_code: str, details: Optional[Dict[str, Any]] = None) -> str:
        """
        Translate error code to user-friendly message.

        Args:
            error_code: Error code from MCP tools (VALIDATION_ERROR, NOT_FOUND, etc.)
            details: Additional error details

        Returns:
            User-friendly error message
        """
        error_code_lower = error_code.lower()

        if error_code_lower in ErrorHumanizer.ERROR_TEMPLATES:
            template = ErrorHumanizer.ERROR_TEMPLATES[error_code_lower]

            # Special handling for specific error codes
            if error_code_lower == "validation_error" and details:
                field = details.get("field", "input")
                limit = details.get("limit", "1000")
                return template.format(field=field, limit=limit)
            elif error_code_lower == "not_found" and details:
                reference = details.get("reference", "that")
                suggestion = ErrorHumanizer._get_random_suggestion()
                return template.format(reference=reference, suggestion=suggestion)
            elif error_code_lower == "bad_request" and details:
                field_details = details.get("field", "more information")
                return template.format(details=field_details)

            return template

        # Default fallback for unknown error codes
        return f"Something went wrong: {error_code}. Please try again."


# Global instance for easy access
_error_humanizer = ErrorHumanizer()


def get_error_humanizer() -> ErrorHumanizer:
    """Get the global error humanizer instance."""
    return _error_humanizer