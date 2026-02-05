"""
Basic test to verify the Chat Agent Connector implementation.
"""
import asyncio
from src.services.agent_runner import AgentRunner
from src.services.conversation_service import ConversationService


async def test_basic_functionality():
    """
    Test basic functionality of the chat agent connector.
    """
    print("Testing basic functionality of Chat Agent Connector...")
    
    # Create an instance of AgentRunner
    agent_runner = AgentRunner()
    
    # Test conversation creation and message handling
    print("\n1. Testing conversation creation and message handling...")
    result = await agent_runner.run_conversation(
        user_id="test_user_123",
        message="Hello, can you help me create a task?",
        conversation_id=None  # Will create a new conversation
    )
    
    print(f"Initial conversation ID: {result['conversation_id']}")
    print(f"Response: {result['response']}")
    print(f"Tool calls: {result['tool_calls']}")
    
    # Test continuing the conversation
    print("\n2. Testing conversation continuation...")
    result2 = await agent_runner.run_conversation(
        user_id="test_user_123",
        message="Can you create a task to buy groceries?",
        conversation_id=result['conversation_id']
    )
    
    print(f"Continued conversation ID: {result2['conversation_id']}")
    print(f"Response: {result2['response']}")
    print(f"Tool calls: {result2['tool_calls']}")
    
    # Test conversation service directly
    print("\n3. Testing conversation history retrieval...")
    conversation_service = ConversationService()
    history = conversation_service.get_conversation_history(result2['conversation_id'])
    
    print(f"Retrieved {len(history)} items from conversation history:")
    for i, item in enumerate(history):
        print(f"  {i+1}. {item['role']}: {item['content'][:50]}...")
    
    print("\nBasic functionality test completed successfully!")


if __name__ == "__main__":
    asyncio.run(test_basic_functionality())