"""
Quick test to verify RAG function tool works
"""
import asyncio
from query_engine import search_hospital_knowledge, index

async def test_rag():
    print("\n" + "="*60)
    print("Testing RAG Function Tool")
    print("="*60 + "\n")
    
    if not index:
        print("❌ Index not loaded!")
        return
    
    print("✅ Index loaded successfully!\n")
    
    # Test queries
    test_queries = [
        "What are the cafeteria hours?",
        "Tell me about the cardiology department",
        "Who are the cardiologists?",
        "What are the visiting hours?"
    ]
    
    for query in test_queries:
        print(f"\n{'─'*60}")
        print(f"❓ Question: {query}")
        print(f"{'─'*60}")
        
        result = await search_hospital_knowledge(query)
        
        print(f"\n💬 Answer: {result[:300]}...")
        print()
    
    print("\n" + "="*60)
    print("✅ RAG function test complete!")
    print("="*60 + "\n")

if __name__ == "__main__":
    asyncio.run(test_rag())
