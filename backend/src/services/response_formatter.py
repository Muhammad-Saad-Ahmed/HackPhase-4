"""
Response formatter service for AI agent responses.
Provides template-based response generation with personality variations.
"""
from typing import Dict, Any, List, Optional
import random
from pydantic import BaseModel


class ResponseTemplate(BaseModel):
    """Template for different response types."""
    task_created: str = "I've added '{title}' to your tasks. {encouragement}"
    task_completed: str = "{celebration} I've marked '{title}' as completed ✓"
    task_deleted: str = "✓ Deleted: '{title}' (Task #{position})"
    task_updated: str = "I've updated task {position} to '{new_title}'"
    task_listed_empty: str = "You don't have any tasks yet. Would you like to create one?"
    task_listed: str = "Here are your {filter_name} tasks:\n{task_list}"
    error_not_found: str = "I couldn't find task {reference}. {suggestion}"
    error_validation: str = "That {field} is too long. Please keep it under {limit} characters."
    clarification_needed: str = "I'm not entirely sure what you want to do. Did you mean to {suggestions}?"
    confirmation_required: str = "⚠️ This will permanently delete '{title}'. Are you sure?"


class PersonalityVariations(BaseModel):
    """Personality variations for different response types."""
    encouragement: List[str] = ["You got this!", "Let's make it happen!", "On it!", "Got it!"]
    celebration: List[str] = ["Great!", "Awesome!", "Nice!", "Way to go!", "Excellent!"]
    suggestions: List[str] = ["add a task", "list your tasks", "update a task", "complete a task", "delete a task"]
    suggestions_continued: List[str] = ["create a new task", "view your current tasks", "modify an existing task", "finish a task", "remove a task"]
    error_suggestions: List[str] = ["Try 'show my tasks' to see what's available.", "Would you like to see your current tasks?", "Maybe list tasks first to see what's available."]


class ResponseFormatter:
    """Format agent responses with consistent tone and personality."""

    def __init__(self):
        self.templates = ResponseTemplate()
        self.personality = PersonalityVariations()

    def format_task_created(self, title: str) -> str:
        """Format response for task creation."""
        encouragement = random.choice(self.personality.encouragement)
        return self.templates.task_created.format(
            title=title,
            encouragement=encouragement
        )

    def format_task_completed(self, title: str) -> str:
        """Format response for task completion."""
        celebration = random.choice(self.personality.celebration)
        return self.templates.task_completed.format(
            title=title,
            celebration=celebration
        )

    def format_task_deleted(self, position: int, title: str) -> str:
        """Format response for task deletion."""
        return self.templates.task_deleted.format(
            position=position,
            title=title
        )

    def format_task_updated(self, position: int, new_title: str) -> str:
        """Format response for task update."""
        return self.templates.task_updated.format(
            position=position,
            new_title=new_title
        )

    def format_task_listed_empty(self) -> str:
        """Format response when no tasks exist."""
        return self.templates.task_listed_empty

    def format_task_listed(self, tasks: List[Dict[str, Any]], filter_name: str = "all") -> str:
        """Format response for task listing."""
        if not tasks:
            return self.format_task_listed_empty()

        task_list = "\n".join([
            f"{i+1}. {task['title']}"
            for i, task in enumerate(tasks)
        ])

        return self.templates.task_listed.format(
            filter_name=filter_name,
            task_list=task_list
        )

    def format_error_not_found(self, reference: str = "that task") -> str:
        """Format response for not found errors."""
        suggestion = random.choice(self.personality.error_suggestions)
        try:
            return self.templates.error_not_found.format(
                reference=reference,
                suggestion=suggestion
            )
        except (KeyError, ValueError):
            # Fallback if template formatting fails
            return f"I couldn't find {reference}. {suggestion}"

    def format_error_validation(self, field: str, limit: int) -> str:
        """Format response for validation errors."""
        return self.templates.error_validation.format(
            field=field,
            limit=limit
        )

    def format_clarification_needed(self, suggestions: Optional[List[str]] = None) -> str:
        """Format response when clarification is needed."""
        if suggestions:
            suggestions_text = ", ".join(suggestions)
        else:
            suggestions_text = random.choice(self.personality.suggestions)

        return self.templates.clarification_needed.format(
            suggestions=suggestions_text
        )

    def format_confirmation_required(self, title: str) -> str:
        """Format confirmation message for destructive operations."""
        return self.templates.confirmation_required.format(title=title)


# Global instance for easy access
_response_formatter = ResponseFormatter()


def get_response_formatter() -> ResponseFormatter:
    """Get the global response formatter instance."""
    return _response_formatter