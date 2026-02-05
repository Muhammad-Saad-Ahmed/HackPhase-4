"""
Task reference resolver service for mapping user references to task IDs.
Handles positional references like "task 2", "the first one", "#3", etc.
"""
from typing import Dict, Any, Optional, List
import re


class TaskReferenceResolver:
    """Resolve user's task references to actual task IDs."""

    def __init__(self):
        pass

    def resolve_task_reference(
        self,
        conversation_metadata: Dict[str, Any],
        user_reference: str
    ) -> Optional[int]:
        """
        Resolve user's task reference to actual task ID.

        Args:
            conversation_metadata: Conversation metadata dict containing task_references
            user_reference: User's reference string (e.g., "task 2", "the first one", "2")

        Returns:
            Task ID if found, None otherwise

        Examples:
            - "task 2" → 43 (if task_references["2"] = 43)
            - "the first one" → 42 (if task_references["1"] = 42)
            - "#3" → 44 (if task_references["3"] = 44)
        """
        task_refs = conversation_metadata.get("task_references", {})

        if not task_refs:
            return None

        # Handle numeric references: "task 2", "2", "#2", "number 2"
        numeric_match = re.search(r'\d+', user_reference)
        if numeric_match:
            position = numeric_match.group()
            return task_refs.get(position)

        # Handle ordinal references: "the first one", "first task", "second", "last"
        ordinals = {
            "first": "1",
            "second": "2",
            "third": "3",
            "fourth": "4",
            "fifth": "5",
            "sixth": "6",
            "seventh": "7",
            "eighth": "8",
            "ninth": "9",
            "tenth": "10",
            "last": str(len(task_refs))  # Dynamic based on list length
        }

        user_lower = user_reference.lower()
        for word, position in ordinals.items():
            if word in user_lower:
                return task_refs.get(position)

        return None

    def extract_task_positions_from_message(self, message: str) -> List[str]:
        """
        Extract all potential task positions from a user message.

        Args:
            message: User message to scan

        Returns:
            List of position strings found in the message
        """
        positions = []

        # Find all numeric references
        numeric_matches = re.findall(r'\d+', message)
        positions.extend(numeric_matches)

        # Find ordinal references
        ordinals = ["first", "second", "third", "fourth", "fifth", "last"]
        user_lower = message.lower()
        for ordinal in ordinals:
            if ordinal in user_lower:
                positions.append(ordinal)

        return positions

    def validate_task_reference_exists(
        self,
        conversation_metadata: Dict[str, Any],
        user_reference: str
    ) -> bool:
        """
        Check if a task reference exists in the conversation metadata.

        Args:
            conversation_metadata: Conversation metadata dict
            user_reference: User's reference string

        Returns:
            True if reference exists, False otherwise
        """
        task_id = self.resolve_task_reference(conversation_metadata, user_reference)
        return task_id is not None

    def get_all_referenced_tasks(
        self,
        conversation_metadata: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Get all currently referenced tasks with their positions.

        Args:
            conversation_metadata: Conversation metadata dict

        Returns:
            List of task references with position and ID
        """
        task_refs = conversation_metadata.get("task_references", {})
        referenced_at = conversation_metadata.get("referenced_at")

        return [
            {
                "position": position,
                "task_id": task_id,
                "referenced_at": referenced_at
            }
            for position, task_id in task_refs.items()
        ]

    def find_matching_tasks_by_description(
        self,
        conversation_metadata: Dict[str, Any],
        description: str
    ) -> List[Dict[str, Any]]:
        """
        Find tasks that match a description in the conversation context.

        Args:
            conversation_metadata: Conversation metadata dict
            description: Description to search for

        Returns:
            List of matching task references with position and ID
        """
        # This would typically require access to the actual task details
        # For now, this is a placeholder that just returns the referenced tasks
        # In a real implementation, you'd want to store the task titles/descriptions
        # along with the references to enable this functionality
        task_refs = conversation_metadata.get("task_references", {})
        referenced_at = conversation_metadata.get("referenced_at")

        # Since we only have IDs in task_references, we can't match by description
        # This would need to be enhanced with title/description storage
        return [
            {
                "position": position,
                "task_id": task_id,
                "referenced_at": referenced_at,
                "description": description  # Placeholder
            }
            for position, task_id in task_refs.items()
        ]


# Global instance for easy access
_task_reference_resolver = TaskReferenceResolver()


def get_task_reference_resolver() -> TaskReferenceResolver:
    """Get the global task reference resolver instance."""
    return _task_reference_resolver