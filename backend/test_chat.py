"""Test script for chat service."""
import sys
from pathlib import Path
import asyncio

# Add backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from services.chat_service import chat_service


async def test_chat():
    """Test the chat service with sample queries."""
    
    print("🧪 Testing Chat Service")
    print("=" * 60)
    
    test_queries = [
        "What are the emergency department hours?",
        "I have severe chest pain, what should I do?",
        "Can you tell me about Dr. Smith?",
        "What departments do you have?",
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Test {i}: {query}")
        print("-" * 60)
        
        try:
            result = await chat_service.chat(message=query)
            
            print(f"✅ Response: {result['response']}")
            print(f"📊 Context Used: {result['context_used']}")
            print(f"🤖 Model: {result['model']}")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        print("-" * 60)
    
    print("\n✅ Testing complete!")


async def interactive_chat():
    """Interactive chat session."""
    
    print("\n💬 Interactive Chat Mode")
    print("=" * 60)
    print("Type 'quit' or 'exit' to end the session")
    print("=" * 60)
    
    conversation_history = []
    
    while True:
        try:
            user_input = input("\n👤 You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not user_input:
                continue
            
            # Get response
            result = await chat_service.chat(
                message=user_input,
                conversation_history=conversation_history
            )
            
            # Display response
            print(f"\n🤖 Assistant: {result['response']}")
            print(f"   (Context: {'✓' if result['context_used'] else '✗'}, Model: {result['model']})")
            
            # Update conversation history
            conversation_history.append({"role": "user", "content": user_input})
            conversation_history.append({"role": "assistant", "content": result['response']})
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")


async def main():
    """Main test function."""
    
    print("\n🚀 Chat Service Test Suite")
    print("=" * 60)
    
    # Check if RAG is available
    from services.rag_service import rag_service
    if rag_service.is_available():
        print("✅ RAG Service: Available")
    else:
        print("⚠️  RAG Service: Not available (responses may be limited)")
    
    print("\nChoose test mode:")
    print("1. Run automated tests")
    print("2. Interactive chat")
    print("3. Both")
    
    choice = input("\nEnter choice (1/2/3): ").strip()
    
    if choice == "1":
        await test_chat()
    elif choice == "2":
        await interactive_chat()
    elif choice == "3":
        await test_chat()
        await interactive_chat()
    else:
        print("Invalid choice. Running automated tests...")
        await test_chat()


if __name__ == "__main__":
    asyncio.run(main())
