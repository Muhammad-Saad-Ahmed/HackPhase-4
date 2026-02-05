"""
ConversationService for managing conversation state.
"""
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, Dict, Any
from uuid import uuid4
from datetime import datetime
from ..models.chat_message import ChatMessage, ChatMessageBase
from ..models.chat_response import ChatResponse, ChatResponseBase
from ..models.conversation_metadata import ConversationMetadata
from ..core.database import AsyncSessionLocal


class ConversationService:
    """Service class for managing conversation state and history."""

    def __init__(self):
        self.session_maker = AsyncSessionLocal

    def create_conversation_id(self) -> str:
        """Generate a new conversation ID."""
        return f"conv_{str(uuid4())[:8]}"

    async def get_conversation_history(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Retrieve the conversation history for a given conversation ID."""
        async with self.session_maker() as session:
            # Get messages associated with this conversation
            message_query = select(ChatMessage).where(ChatMessage.conversation_id == conversation_id)
            result = await session.execute(message_query)
            messages = result.scalars().all()

            # Get responses associated with this conversation
            response_query = select(ChatResponse).where(ChatResponse.conversation_id == conversation_id)
            result = await session.execute(response_query)
            responses = result.scalars().all()

            # Combine and sort by timestamp
            history = []

            # Add user messages
            for msg in messages:
                history.append({
                    "role": "user",
                    "content": msg.message,
                    "timestamp": msg.timestamp,
                    "user_id": msg.user_id
                })

            # Add assistant responses
            for resp in responses:
                history.append({
                    "role": "assistant",
                    "content": resp.response,
                    "tool_calls": resp.get_tool_calls(),  # Use the helper method to get the list
                    "timestamp": resp.timestamp,
                    "user_id": resp.user_id
                })

            # Sort by timestamp
            history.sort(key=lambda x: x["timestamp"])

            return history

    async def get_conversation_metadata(self, conversation_id: str) -> Dict[str, Any]:
        """Retrieve metadata for a given conversation ID."""
        async with self.session_maker() as session:
            query = select(ConversationMetadata).where(
                ConversationMetadata.conversation_id == conversation_id
            )
            result = await session.execute(query)
            metadata_obj = result.scalars().first()

            if metadata_obj:
                return metadata_obj.get_metadata()
            else:
                return {}

    async def update_conversation_metadata(self, conversation_id: str, metadata: Dict[str, Any]) -> bool:
        """Update metadata for a given conversation ID."""
        async with self.session_maker() as session:
            # Check if metadata already exists
            query = select(ConversationMetadata).where(
                ConversationMetadata.conversation_id == conversation_id
            )
            result = await session.execute(query)
            existing = result.scalars().first()

            if existing:
                # Update existing metadata - merge with existing
                current_metadata = existing.get_metadata()
                current_metadata.update(metadata)
                existing.set_metadata(current_metadata)
                session.add(existing)
            else:
                # Create new metadata
                new_metadata = ConversationMetadata(
                    conversation_id=conversation_id
                )
                new_metadata.set_metadata(metadata)
                session.add(new_metadata)

            await session.commit()
            return True

    async def store_user_message(self, user_id: str, message: str, conversation_id: Optional[str] = None) -> str:
        """Store a user message and return the conversation ID."""
        async with self.session_maker() as session:
            # If no conversation ID provided, create a new one
            if not conversation_id:
                conversation_id = self.create_conversation_id()

            # Create a new message
            chat_message = ChatMessage(
                user_id=user_id,
                message=message,
                conversation_id=conversation_id
            )

            # Add to session and commit
            session.add(chat_message)
            await session.commit()

            return conversation_id

    async def store_assistant_response(self, conversation_id: str, user_id: str, response: str, tool_calls: List[Dict[str, Any]] = None) -> int:
        """Store an assistant response and return the response ID."""
        if tool_calls is None:
            tool_calls = []

        async with self.session_maker() as session:
            # Create a new response
            chat_response = ChatResponse(
                conversation_id=conversation_id,
                response=response,
                user_id=user_id
            )
            # Set tool_calls using the helper method
            chat_response.set_tool_calls(tool_calls)

            # Add to session and commit
            session.add(chat_response)
            await session.commit()
            await session.refresh(chat_response)

            return chat_response.id

    def validate_conversation_id(self, conversation_id: str) -> bool:
        """Validate if a conversation ID exists and is valid."""
        # For now, just check if it has the expected format
        # In a real implementation, you might check if it exists in the database
        return conversation_id.startswith("conv_") and len(conversation_id) >= 10