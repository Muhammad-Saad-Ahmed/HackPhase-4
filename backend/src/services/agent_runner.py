"""
AgentRunner abstraction for managing the conversation flow.
Implements intent recognition, tool selection, and natural language processing.
"""
import re
import time
from typing import Dict, Any, List, Optional, Tuple
from pydantic import BaseModel
from datetime import datetime
from ..services.llm_client import get_llm_client
from ..services.mcp_client_direct import MCPTaskExecutor  # Direct tool execution
from ..services.conversation_service import ConversationService
from ..services.response_formatter import get_response_formatter
from ..services.error_humanizer import get_error_humanizer
from ..services.task_reference_resolver import get_task_reference_resolver
from ..services.confirmation_handler import ConfirmationHandler
from ..core.logging import logger


class IntentResult(BaseModel):
    """Result of intent recognition."""
    intent_type: str  # "create", "list", "update", "complete", "delete", "unclear"
    confidence: float  # 0.0 - 1.0
    entities: Dict[str, Any]  # Extracted entities (title, description, etc.)
    alternatives: List[Tuple[str, float]] = []  # Alternative intents with confidence
    reasoning: Optional[str] = None  # LLM's reasoning for the classification


class ToolSelectionResult(BaseModel):
    """Result of tool selection."""
    tool_name: str  # Selected tool name
    confidence: float  # 0.0 - 1.0
    parameters: Dict[str, Any]  # Parameters for the tool
    requires_confirmation: bool  # Whether confirmation is needed (for destructive ops)
    alternatives: List[Tuple[str, float]] = []  # Alternative tools with confidence


class AgentRunner:
    """Manages the complete conversation flow with intent recognition and tool selection."""

    def __init__(self):
        self.llm_client = get_llm_client()
        self.mcp_executor = MCPTaskExecutor()
        self.conversation_service = ConversationService()
        self.response_formatter = get_response_formatter()
        self.error_humanizer = get_error_humanizer()
        self.task_reference_resolver = get_task_reference_resolver()
        self.confirmation_handler = ConfirmationHandler()

        # Confidence thresholds by intent type
        self.confidence_thresholds = {
            "create": 0.80,
            "list": 0.70,
            "update": 0.85,
            "complete": 0.80,
            "delete": 0.90
        }

    async def run_conversation(self, user_id: str, message: str, conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Run the complete conversation flow from user message to assistant response.

        This method orchestrates the entire agent workflow including intent recognition,
        tool selection, MCP tool execution, response formatting, and conversation state management.

        Args:
            user_id: Unique identifier for the user
            message: User's natural language message
            conversation_id: Optional conversation ID to continue existing conversation

        Returns:
            Dict containing:
                - conversation_id: ID of the conversation
                - response: Formatted response text for the user
                - tool_calls: List of tool calls made (if any)

        Raises:
            Exception: If any error occurs during the conversation flow

        Flow:
            1. Load conversation history and metadata
            2. Store user message in database
            3. Recognize intent from user message
            4. Select appropriate tool based on intent
            5. Execute MCP tools if identified
            6. Format response based on tool results
            7. Store assistant response in database
            8. Return formatted result
        """
        # Track performance
        start_time = time.time()

        try:
            # 1. Load conversation (get history and metadata)
            if conversation_id:
                conversation_history = await self.conversation_service.get_conversation_history(conversation_id)
                conversation_metadata = await self.conversation_service.get_conversation_metadata(conversation_id)
            else:
                conversation_history = []
                conversation_metadata = {}

            # 2. Store user message
            conversation_id = await self.conversation_service.store_user_message(
                user_id=user_id,
                message=message,
                conversation_id=conversation_id
            )

            # 2.5. Check for pending confirmation (delete confirmation flow)
            if self.confirmation_handler.has_pending_confirmation(conversation_metadata):
                confirmation_response = self.confirmation_handler.is_confirmation_response(message)

                if confirmation_response is not None:
                    pending = self.confirmation_handler.get_pending_confirmation(conversation_metadata)

                    if confirmation_response:  # User said yes
                        # Execute the pending action
                        try:
                            tool_result = await self.mcp_executor.execute_tool(
                                tool_name=pending["tool_name"],
                                arguments=pending["parameters"]
                            )

                            response_message = self.confirmation_handler.get_confirmation_accepted_message(
                                pending["action"],
                                pending["task_title"]
                            )

                            # Clear pending confirmation
                            conversation_metadata = self.confirmation_handler.clear_pending_confirmation(conversation_metadata)
                            await self.conversation_service.update_conversation_metadata(conversation_id, conversation_metadata)

                            # Store response
                            await self.conversation_service.store_assistant_message(
                                conversation_id=conversation_id,
                                message=response_message
                            )

                            return {
                                "conversation_id": conversation_id,
                                "response": response_message,
                                "tool_calls": [tool_result] if tool_result else [],
                                "reasoning_trace": {"action": "confirmed_delete"}
                            }

                        except Exception as e:
                            error_message = f"Failed to complete {pending['action']}: {str(e)}"
                            conversation_metadata = self.confirmation_handler.clear_pending_confirmation(conversation_metadata)
                            await self.conversation_service.update_conversation_metadata(conversation_id, conversation_metadata)

                            await self.conversation_service.store_assistant_message(
                                conversation_id=conversation_id,
                                message=error_message
                            )

                            return {
                                "conversation_id": conversation_id,
                                "response": error_message,
                                "tool_calls": [],
                                "reasoning_trace": {"action": "confirmation_error", "error": str(e)}
                            }

                    else:  # User said no
                        response_message = self.confirmation_handler.get_confirmation_declined_message(pending["action"])

                        # Clear pending confirmation
                        conversation_metadata = self.confirmation_handler.clear_pending_confirmation(conversation_metadata)
                        await self.conversation_service.update_conversation_metadata(conversation_id, conversation_metadata)

                        await self.conversation_service.store_assistant_message(
                            conversation_id=conversation_id,
                            message=response_message
                        )

                        return {
                            "conversation_id": conversation_id,
                            "response": response_message,
                            "tool_calls": [],
                            "reasoning_trace": {"action": "cancelled_delete"}
                        }

            # Prepare messages for LLM
            llm_messages = []

            # Add conversation history to messages
            for item in conversation_history:
                role = item["role"]
                content = item["content"]

                # For assistant messages with tool calls, format appropriately
                if role == "assistant" and "tool_calls" in item:
                    # Add the assistant response
                    llm_messages.append({"role": role, "content": content})

                    # Add tool call results if they exist
                    for tool_call in item["tool_calls"]:
                        if "result" in tool_call:
                            llm_messages.append({
                                "role": "tool",
                                "content": str(tool_call["result"]),
                                "tool_call_id": tool_call.get("id", "")
                            })
                else:
                    llm_messages.append({"role": role, "content": content})

            # Add the new user message
            llm_messages.append({"role": "user", "content": message})

            # 3. Recognize intent from user message
            intent_result = await self._recognize_intent(message)
            logger.info(
                "Intent recognized",
                intent=intent_result.intent_type,
                confidence=intent_result.confidence,
                user_id=user_id
            )

            # 4. Select appropriate tool based on intent
            tool_selection_result = await self._select_tool(intent_result, conversation_metadata, message)
            if tool_selection_result:
                logger.info(
                    "Tool selected",
                    tool=tool_selection_result.tool_name,
                    requires_confirmation=tool_selection_result.requires_confirmation,
                    user_id=user_id
                )

            # 5. Execute MCP tools if identified
            tool_results = []
            if tool_selection_result and tool_selection_result.tool_name:
                # Check if confirmation is required (e.g., delete operations)
                if tool_selection_result.requires_confirmation:
                    # Get task title for confirmation message
                    task_id = tool_selection_result.parameters.get("task_id")
                    task_title = "this task"

                    # Try to get task title from task_details in metadata
                    if task_id and "task_details" in conversation_metadata:
                        for task in conversation_metadata["task_details"]:
                            if task["id"] == task_id:
                                task_title = task["title"]
                                break

                    # Ask for confirmation and store pending action
                    confirmation_message = self.confirmation_handler.get_confirmation_prompt(
                        intent_result.intent_type,
                        task_title
                    )

                    # Store pending confirmation in metadata
                    conversation_metadata = self.confirmation_handler.set_pending_confirmation(
                        conversation_metadata=conversation_metadata,
                        action=intent_result.intent_type,
                        task_id=task_id,
                        task_title=task_title,
                        tool_name=tool_selection_result.tool_name,
                        parameters=tool_selection_result.parameters
                    )

                    await self.conversation_service.update_conversation_metadata(conversation_id, conversation_metadata)
                    await self.conversation_service.store_assistant_message(
                        conversation_id=conversation_id,
                        message=confirmation_message
                    )

                    logger.info("Confirmation required", action=intent_result.intent_type, task_title=task_title)

                    return {
                        "conversation_id": conversation_id,
                        "response": confirmation_message,
                        "tool_calls": [],
                        "reasoning_trace": {
                            "intent": intent_result.intent_type,
                            "action": "awaiting_confirmation"
                        }
                    }

                logger.info("Executing tool", tool_name=tool_selection_result.tool_name, parameters=tool_selection_result.parameters)

                # Execute the selected tool
                try:
                    tool_result = await self.mcp_executor.execute_tool(
                        tool_name=tool_selection_result.tool_name,
                        arguments=tool_selection_result.parameters
                    )
                    tool_results = [tool_result]

                    # Update tool selection result with execution result
                    tool_selection_result.parameters["result"] = tool_result

                    # Store task_references in conversation metadata after list_tasks
                    if tool_selection_result.tool_name == "list_tasks" and tool_result.get("success"):
                        task_data = tool_result.get("data", [])
                        # Store as position-to-id mapping for resolver
                        task_references = {
                            str(i + 1): task["id"]
                            for i, task in enumerate(task_data)
                        }
                        # Also store task details for display/matching
                        task_details = [
                            {"position": str(i + 1), "id": task["id"], "title": task.get("title", "")}
                            for i, task in enumerate(task_data)
                        ]
                        await self.conversation_service.update_conversation_metadata(
                            conversation_id=conversation_id,
                            metadata={
                                "task_references": task_references,
                                "task_details": task_details,
                                "referenced_at": datetime.utcnow().isoformat()
                            }
                        )
                        logger.info("Stored task references in conversation metadata", count=len(task_references))

                except Exception as e:
                    # Humanize the error for user-friendly response
                    error_message = self.error_humanizer.humanize(e)
                    logger.error("Tool execution failed", error=str(e), user_id=user_id)

                    # Return error response
                    elapsed_time = time.time() - start_time
                    return {
                        "conversation_id": conversation_id,
                        "response": error_message,
                        "tool_calls": [],
                        "reasoning_trace": {
                            "intent": intent_result.intent_type,
                            "confidence": intent_result.confidence,
                            "tool_selected": tool_selection_result.tool_name if tool_selection_result else None,
                            "error": "Tool execution failed",
                            "response_time_ms": round(elapsed_time * 1000, 2)
                        }
                    }
            else:
                # No tool was selected
                # Check if this is because of missing task references
                if intent_result.intent_type in ["update", "complete", "delete"]:
                    # User wants to perform an action on a task but we don't have context
                    if not conversation_metadata.get("task_references"):
                        helpful_message = "I don't have any tasks in context. Could you please list your tasks first by saying 'show my tasks' or 'list tasks'?"
                    else:
                        # We have references but couldn't resolve the specific one
                        helpful_message = f"I'm not sure which task you're referring to. Could you please specify the task number? For example, 'complete task 1' or 'delete the second one'."

                    elapsed_time = time.time() - start_time
                    return {
                        "conversation_id": conversation_id,
                        "response": helpful_message,
                        "tool_calls": [],
                        "reasoning_trace": {
                            "intent": intent_result.intent_type,
                            "confidence": intent_result.confidence,
                            "tool_selected": None,
                            "reason": "Missing task references",
                            "response_time_ms": round(elapsed_time * 1000, 2)
                        }
                    }

                # For other cases, try to get LLM response
                llm_response = await self.llm_client.generate_response(llm_messages)
                elapsed_time = time.time() - start_time
                return {
                    "conversation_id": conversation_id,
                    "response": llm_response["response"],
                    "tool_calls": llm_response.get("tool_calls", []),
                    "reasoning_trace": {
                        "intent": intent_result.intent_type,
                        "confidence": intent_result.confidence,
                        "tool_selected": None,
                        "reason": "Low confidence or unclear intent",
                        "response_time_ms": round(elapsed_time * 1000, 2)
                    }
                }

            # 6. Format response based on tool result
            formatted_response = await self._format_response(intent_result, tool_selection_result, tool_results)

            # 7. Store assistant response
            response_id = await self.conversation_service.store_assistant_response(
                conversation_id=conversation_id,
                user_id=user_id,
                response=formatted_response,
                tool_calls=[{
                    "tool_name": tool_selection_result.tool_name,
                    "parameters": tool_selection_result.parameters,
                    "result": tool_results[0] if tool_results else None
                }] if tool_selection_result else []
            )

            # 8. Return result
            elapsed_time = time.time() - start_time
            logger.info(
                "Conversation completed",
                user_id=user_id,
                conversation_id=conversation_id,
                response_time_ms=round(elapsed_time * 1000, 2),
                tool_used=tool_selection_result.tool_name if tool_selection_result else None
            )

            return {
                "conversation_id": conversation_id,
                "response": formatted_response,
                "tool_calls": [{
                    "tool_name": tool_selection_result.tool_name,
                    "parameters": tool_selection_result.parameters,
                    "result": tool_results[0] if tool_results else None
                }] if tool_selection_result else [],
                "reasoning_trace": {
                    "intent": intent_result.intent_type,
                    "confidence": intent_result.confidence,
                    "tool_selected": tool_selection_result.tool_name if tool_selection_result else None,
                    "response_time_ms": round(elapsed_time * 1000, 2)
                }
            }

        except Exception as e:
            elapsed_time = time.time() - start_time
            logger.error(
                "Error in conversation flow",
                error=str(e),
                user_id=user_id,
                response_time_ms=round(elapsed_time * 1000, 2)
            )
            raise

    async def _recognize_intent(self, user_message: str) -> IntentResult:
        """
        Recognize the intent from the user's message.

        Args:
            user_message: The user's natural language message

        Returns:
            IntentResult with the recognized intent and confidence
        """
        user_message_lower = user_message.lower().strip()

        # Intent recognition patterns
        intent_scores = {
            "create": 0.0,
            "list": 0.0,
            "update": 0.0,
            "complete": 0.0,
            "delete": 0.0
        }

        # CREATE intent patterns
        create_patterns = [
            r"\b(add|create|make|remind me to|need to|have to|want to|should|must)\b",
            r"\b(todo|to-do|item|thing|action)\b",
            r"\b(grocer|shop|buy|purchase)\b",
            r"\b(call|contact|email|message)\b",
            r"\b(schedule|book|arrange|plan)\b"
        ]

        for pattern in create_patterns:
            if re.search(pattern, user_message_lower):
                intent_scores["create"] += 0.2

        # LIST intent patterns
        list_patterns = [
            r"\b(show|list|display|what|do i have|need to do|todo|task|tasks|todos|items)\b",
            r"\b(see|view|check|look at|my)\b",
            r"\b(pending|completed|done|finished|all)\b"
        ]

        for pattern in list_patterns:
            if re.search(pattern, user_message_lower):
                intent_scores["list"] += 0.2

        # UPDATE intent patterns
        update_patterns = [
            r"\b(change|update|modify|edit|alter|fix|correct)\b",
            r"\b(task|the|it|that)\b"
        ]

        for pattern in update_patterns:
            if re.search(pattern, user_message_lower):
                intent_scores["update"] += 0.2

        # COMPLETE intent patterns
        complete_patterns = [
            r"\b(complete|finish|done|finished|did|completed|already)\b",
            r"\b(task|it|that|the|already)\b"
        ]

        for pattern in complete_patterns:
            if re.search(pattern, user_message_lower):
                intent_scores["complete"] += 0.2

        # DELETE intent patterns
        delete_patterns = [
            r"\b(delete|remove|get rid of|trash|discard|eliminate)\b",
            r"\b(task|it|that|the)\b"
        ]

        for pattern in delete_patterns:
            if re.search(pattern, user_message_lower):
                intent_scores["delete"] += 0.2

        # Normalize scores to 0-1 range
        max_score = max(intent_scores.values()) if intent_scores else 0.0
        if max_score > 0:
            for intent in intent_scores:
                intent_scores[intent] /= max_score

        # Find the highest scoring intent
        best_intent = max(intent_scores, key=intent_scores.get)
        confidence = intent_scores[best_intent]

        # Extract entities based on intent
        entities = {}
        if best_intent == "create":
            # Extract potential title from message
            # Remove common verbs and focus on nouns
            cleaned_message = re.sub(r"\b(remind me to|need to|i want to|add task:|create|make)\b", "", user_message_lower).strip()
            if cleaned_message:
                entities["title"] = cleaned_message[:255]  # Max 255 chars for title

        elif best_intent == "list":
            # Extract status filter from message
            status_filter = None
            if re.search(r"\b(pending|not done|not completed|to do|todo)\b", user_message_lower):
                status_filter = "pending"
            elif re.search(r"\b(completed|done|finished)\b", user_message_lower):
                status_filter = "completed"
            elif re.search(r"\ball\b", user_message_lower):
                status_filter = None  # Show all tasks

            entities["status_filter"] = status_filter

        elif best_intent == "update":
            # Extract new title/description from message
            # Look for patterns like "change task 2 to X" or "update task 1 to Y"
            match = re.search(r"\b(?:to|with)\s+['\"]?([^'\"]+)['\"]?", user_message, re.IGNORECASE)
            if match:
                new_value = match.group(1).strip()
                # Simple heuristic: if it's long, it's a description; otherwise, it's a title
                if len(new_value) > 50:
                    entities["new_description"] = new_value[:1000]
                else:
                    entities["new_title"] = new_value[:255]

        elif best_intent == "complete":
            # Extract task reference from message
            # Patterns like "I finished the groceries" or "complete task 2"
            # The reference will be resolved in tool selection
            entities["inferred"] = "bought" in user_message_lower or "finished" in user_message_lower or "did" in user_message_lower

        elif best_intent == "delete":
            # Extract task reference from message
            # The reference will be resolved in tool selection
            pass

        # Create intent result
        return IntentResult(
            intent_type=best_intent,
            confidence=confidence,
            entities=entities,
            alternatives=[
                (intent, score)
                for intent, score in sorted(intent_scores.items(), key=lambda x: x[1], reverse=True)
                if score > 0
            ]
        )

    async def _select_tool(self, intent_result: IntentResult, conversation_metadata: Dict[str, Any], user_message: str) -> Optional[ToolSelectionResult]:
        """
        Select the appropriate tool based on the recognized intent.

        Args:
            intent_result: The recognized intent
            conversation_metadata: Conversation metadata for context
            user_message: The original user message for reference resolution

        Returns:
            ToolSelectionResult with the selected tool and parameters
        """
        intent_type = intent_result.intent_type
        confidence = intent_result.confidence
        entities = intent_result.entities

        # Check if confidence is above threshold
        threshold = self.confidence_thresholds.get(intent_type, 0.80)
        if confidence < threshold:
            # If confidence is too low, we might need clarification
            # For now, return None to indicate uncertain intent
            return None

        # Check for context staleness (task references older than 1 hour)
        referenced_at_str = conversation_metadata.get("referenced_at")
        if referenced_at_str and intent_type in ["update", "complete", "delete"]:
            referenced_at = datetime.fromisoformat(referenced_at_str)
            time_elapsed = (datetime.utcnow() - referenced_at).total_seconds()
            if time_elapsed > 3600:  # 1 hour
                logger.warning("Task references are stale", elapsed_seconds=time_elapsed)
                # References are stale, but we'll still try to use them

        # Map intent to tool
        intent_to_tool = {
            "create": "add_task",
            "list": "list_tasks",
            "update": "update_task",
            "complete": "complete_task",
            "delete": "delete_task"
        }

        tool_name = intent_to_tool.get(intent_type)
        if not tool_name:
            return None

        # Build parameters based on intent and entities
        parameters = {}

        if intent_type == "create":
            # Extract title and description from entities
            title = entities.get("title", "").strip()
            if not title:
                # Try to extract from the original message
                title = "New task"  # Default title if none extracted

            # Sanitize inputs (strip leading/trailing whitespace)
            title = title.strip()[:255]  # Enforce max length
            description = entities.get("description", None)
            if description:
                description = description.strip()[:1000]  # Enforce max length

            parameters = {
                "title": title,
                "description": description
            }

        elif intent_type == "list":
            # Get status filter from entities (extracted in intent recognition)
            status_filter = entities.get("status_filter", None)

            parameters = {
                "status": status_filter
            }

        elif intent_type == "update":
            # Resolve task reference from user message
            task_id = self.task_reference_resolver.resolve_task_reference(
                conversation_metadata, user_message
            )

            # Check if we have a valid task reference
            if task_id is None:
                # No task reference found - need to prompt user
                logger.warning("No task reference found for update intent")
                return None

            # Extract new values from message
            # For now, use simple extraction - this could be enhanced
            parameters = {
                "task_id": task_id,
                "title": entities.get("new_title", None),
                "description": entities.get("new_description", None)
            }

        elif intent_type == "complete":
            # Resolve task reference from user message
            task_id = self.task_reference_resolver.resolve_task_reference(
                conversation_metadata, user_message
            )

            # Check if we have a valid task reference
            if task_id is None:
                # No task reference found - need to prompt user
                logger.warning("No task reference found for complete intent")
                return None

            parameters = {
                "task_id": task_id
            }

        elif intent_type == "delete":
            # Resolve task reference from user message
            task_id = self.task_reference_resolver.resolve_task_reference(
                conversation_metadata, user_message
            )

            # Check if we have a valid task reference
            if task_id is None:
                # No task reference found - need to prompt user
                logger.warning("No task reference found for delete intent")
                return None

            parameters = {
                "task_id": task_id
            }

        # Determine if confirmation is required (for destructive operations)
        requires_confirmation = tool_name in ["delete_task"]

        return ToolSelectionResult(
            tool_name=tool_name,
            confidence=confidence,
            parameters=parameters,
            requires_confirmation=requires_confirmation
        )

    async def _format_response(self, intent_result: IntentResult, tool_result: ToolSelectionResult, execution_results: List[Dict[str, Any]]) -> str:
        """
        Format the response based on intent and tool execution result.

        Args:
            intent_result: The recognized intent
            tool_result: The selected tool and parameters
            execution_results: Results from tool execution

        Returns:
            Formatted response string
        """
        if not execution_results or not execution_results[0].get("success"):
            # Handle error case
            error_msg = execution_results[0].get("error", "An error occurred") if execution_results else "An error occurred"
            return self.error_humanizer.humanize(Exception(error_msg))

        # Format response based on intent type
        if intent_result.intent_type == "create":
            result_data = execution_results[0].get("data", {})
            title = result_data.get("title", tool_result.parameters.get("title", "unknown"))
            return self.response_formatter.format_task_created(title)

        elif intent_result.intent_type == "complete":
            result_data = execution_results[0].get("data", {})
            title = result_data.get("title", "unknown task")
            return self.response_formatter.format_task_completed(title)

        elif intent_result.intent_type == "list":
            result_data = execution_results[0].get("data", [])
            filter_name = tool_result.parameters.get("status") or "all"
            return self.response_formatter.format_task_listed(result_data, filter_name)

        elif intent_result.intent_type == "delete":
            result_data = execution_results[0].get("data", {})
            task_id = tool_result.parameters.get("task_id", "unknown")
            title = result_data.get("title", "task")
            return self.response_formatter.format_task_deleted(task_id, title)

        elif intent_result.intent_type == "update":
            result_data = execution_results[0].get("data", {})
            task_id = tool_result.parameters.get("task_id", "unknown")
            new_title = result_data.get("title", tool_result.parameters.get("title", "updated task"))
            return self.response_formatter.format_task_updated(task_id, new_title)

        # Default response if we can't format properly
        return "Operation completed successfully"