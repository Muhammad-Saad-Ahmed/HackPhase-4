"""
Provider-agnostic LLM client for connecting to external LLM providers.
Uses MCP client for tool integration.
"""
from openai import AsyncOpenAI
from typing import Dict, Any, Optional, List
import json
from abc import ABC, abstractmethod
from ..core.config import settings
from .mcp_client_direct import MCPTaskExecutor  # Direct tool execution


class BaseLLMClient(ABC):
    """Abstract base class for LLM clients."""

    @abstractmethod
    async def generate_response(self, messages: List[Dict[str, str]], conversation_context: Optional[str] = None) -> Dict[str, Any]:
        """Generate a response from the LLM based on the input messages."""
        pass


class OpenAIAgentsClient(BaseLLMClient):
    """Client using OpenAI Agents SDK with MCP integration."""

    def __init__(self):
        # Initialize OpenAI client
        self.api_key = settings.openai_api_key or settings.llm_api_key

        # Use base_url if provided (for OpenRouter and other OpenAI-compatible providers)
        if settings.llm_base_url:
            self.client = AsyncOpenAI(
                api_key=self.api_key,
                base_url=settings.llm_base_url
            )
        else:
            self.client = AsyncOpenAI(api_key=self.api_key)

        self.model = settings.llm_model

        # Initialize MCP client for tool integration
        self.mcp_client = MCPTaskExecutor()

    async def generate_response(self, messages: List[Dict[str, str]], conversation_context: Optional[str] = None) -> Dict[str, Any]:
        """Generate a response from OpenAI with MCP tool integration."""
        try:
            # Try to get available tools from MCP server (optional)
            tools = []
            try:
                available_tools = await self.mcp_client.list_available_tools()
                # Convert MCP tools to OpenAI format
                for tool in available_tools:
                    tools.append({
                        "type": "function",
                        "function": {
                            "name": tool["name"],
                            "description": tool["description"],
                            "parameters": tool["inputSchema"]
                        }
                    })
            except Exception as mcp_error:
                # MCP tools not available, continue without them
                print(f"[INFO] MCP tools not available: {mcp_error}")

            # Call OpenAI with or without tools
            if tools:
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=tools,
                    tool_choice="auto",  # Let the model decide when to use tools
                    temperature=0.7,
                    max_tokens=1000
                )
            else:
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=1000
                )

            # Extract the response content
            choice = response.choices[0]
            content = choice.message.content or ""  # Handle None content

            # Extract tool calls if present
            tool_calls = []
            if choice.message.tool_calls:
                for tool_call in choice.message.tool_calls:
                    # Execute the tool call via MCP client
                    result = await self.mcp_client.execute_tool(
                        tool_name=tool_call.function.name,
                        arguments=json.loads(tool_call.function.arguments)
                    )

                    tool_calls.append({
                        "id": tool_call.id,
                        "function": {
                            "name": tool_call.function.name,
                            "arguments": tool_call.function.arguments
                        },
                        "type": tool_call.type,
                        "result": result
                    })

            # If content is empty but we have tool calls, provide a helpful message
            if not content and tool_calls:
                content = "I've executed the requested action for you."

            return {
                "response": content,
                "tool_calls": tool_calls
            }

        except Exception as e:
            raise Exception(f"OpenAI Agents SDK request failed: {str(e)}")

    async def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get available tools from MCP server."""
        try:
            mcp_tools = await self.mcp_client.list_available_tools()

            # Convert to OpenAI format
            tools = []
            for tool in mcp_tools:
                tools.append({
                    "type": "function",
                    "function": {
                        "name": tool.get('tool_name') or tool.get('name'),
                        "description": tool.get('description', ''),
                        "parameters": tool.get('parameter_schema') or tool.get('inputSchema', {})
                    }
                })

            return tools
        except Exception as e:
            raise Exception(f"Failed to get MCP tools: {str(e)}")

    async def close(self) -> None:
        """Close client connections."""
        await self.mcp_client.close()


def get_llm_client() -> BaseLLMClient:
    """Factory function to get the appropriate LLM client based on configuration."""
    provider = settings.llm_provider.lower()

    if provider in ["openai", "openai-agents", "openrouter"]:
        return OpenAIAgentsClient()
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")