#!/usr/bin/env python3
"""
Debug OpenAI Integration
"""
import os
from emergentintegrations.llm.chat import LlmChat, UserMessage
import asyncio

async def test_openai():
    api_key = os.environ.get('OPENAI_API_KEY')
    print(f"API Key present: {bool(api_key)}")
    print(f"API Key starts with: {api_key[:10] if api_key else 'None'}...")
    
    try:
        session_id = "test_session"
        system_message = "You are a helpful assistant."
        
        chat = LlmChat(
            api_key=api_key,
            session_id=session_id,
            system_message=system_message
        ).with_model("openai", "gpt-4o")
        
        user_message = UserMessage(text="Hello, this is a test.")
        response = await chat.send_message(user_message)
        
        print(f"Response: {response}")
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_openai())