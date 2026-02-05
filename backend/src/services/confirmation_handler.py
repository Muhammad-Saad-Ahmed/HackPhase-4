"""
Confirmation handler for destructive operations like delete.
Manages pending confirmations in conversation metadata.
"""
import re
from typing import Dict, Any, Optional, Tuple


class ConfirmationHandler:
    """Handles confirmation flow for destructive operations."""

    @staticmethod
    def is_confirmation_response(message: str) -> Optional[bool]:
        """
        Check if user message is a confirmation (yes/no) response.

        Args:
            message: User's message

        Returns:
            True if confirmed (yes), False if declined (no), None if not a confirmation
        """
        message_lower = message.lower().strip()

        # Positive confirmation patterns
        yes_patterns = [
            r"^(yes|yeah|yep|yup|sure|ok|okay|confirm|do it|go ahead|proceed)$",
            r"^(y|ha|han|haan)$",  # Short forms + Urdu/Hindi yes
        ]

        # Negative confirmation patterns
        no_patterns = [
            r"^(no|nope|nah|cancel|don't|stop|abort|nahi|na)$",
            r"^n$",  # Short form
        ]

        for pattern in yes_patterns:
            if re.search(pattern, message_lower):
                return True

        for pattern in no_patterns:
            if re.search(pattern, message_lower):
                return False

        return None

    @staticmethod
    def has_pending_confirmation(conversation_metadata: Dict[str, Any]) -> bool:
        """Check if there's a pending confirmation in metadata."""
        return conversation_metadata.get("pending_confirmation") is not None

    @staticmethod
    def get_pending_confirmation(conversation_metadata: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get pending confirmation details from metadata."""
        return conversation_metadata.get("pending_confirmation")

    @staticmethod
    def set_pending_confirmation(
        conversation_metadata: Dict[str, Any],
        action: str,
        task_id: str,
        task_title: str,
        tool_name: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Store pending confirmation in metadata.

        Args:
            conversation_metadata: Current conversation metadata
            action: Action type (e.g., "delete")
            task_id: Task ID to act upon
            task_title: Task title for display
            tool_name: MCP tool name to execute
            parameters: Tool parameters

        Returns:
            Updated conversation metadata
        """
        conversation_metadata["pending_confirmation"] = {
            "action": action,
            "task_id": task_id,
            "task_title": task_title,
            "tool_name": tool_name,
            "parameters": parameters
        }
        return conversation_metadata

    @staticmethod
    def clear_pending_confirmation(conversation_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Clear pending confirmation from metadata."""
        if "pending_confirmation" in conversation_metadata:
            del conversation_metadata["pending_confirmation"]
        return conversation_metadata

    @staticmethod
    def get_confirmation_prompt(action: str, task_title: str) -> str:
        """
        Generate confirmation prompt message.

        Args:
            action: Action type (e.g., "delete")
            task_title: Task title

        Returns:
            Confirmation prompt string
        """
        if action == "delete":
            return f"⚠️ Are you sure you want to delete '{task_title}'? Reply 'yes' to confirm or 'no' to cancel."
        return f"⚠️ Confirm {action} on '{task_title}'? Reply 'yes' or 'no'."

    @staticmethod
    def get_confirmation_accepted_message(action: str, task_title: str) -> str:
        """Get message for when confirmation is accepted."""
        if action == "delete":
            return f"✓ Deleted: '{task_title}'"
        return f"✓ {action.capitalize()} completed: '{task_title}'"

    @staticmethod
    def get_confirmation_declined_message(action: str) -> str:
        """Get message for when confirmation is declined."""
        return f"Cancelled. The {action} has been cancelled."
