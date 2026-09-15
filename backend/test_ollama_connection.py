"""
Quick test script to verify Ollama connection.
"""

from backend.ollama_client import OllamaClient

def main():
    print("Testing Ollama connection...")
    
    client = OllamaClient()
    
    # Test health check
    print("\n1. Health check:", end=" ")
    if client.health_check():
        print("✅ Ollama is running")
    else:
        print("❌ Ollama is not responding")
        return
    
    # Test simple chat
    print("\n2. Testing simple chat request...")
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Say 'Hello' in one word."}
    ]
    
    print("   Sending request to Ollama...")
    response = client.chat(messages, stream=False)
    
    if response:
        print(f"   ✅ Response received: {response[:100]}")
    else:
        print("   ❌ No response received")
    
    print("\n3. Testing with GadgetMart system prompt...")
    from backend.prompt_builder import PromptBuilder
    builder = PromptBuilder()
    
    messages = builder.build_messages(
        history=[],
        user_message="What is the price of the headphones?"
    )
    
    print("   Sending request to Ollama...")
    response = client.chat(messages, stream=False)
    
    if response:
        print(f"   ✅ Response received ({len(response)} chars)")
        print(f"   Response: {response[:200]}...")
    else:
        print("   ❌ No response received")
    
    print("\n✅ Connection test complete!")

if __name__ == "__main__":
    main()
