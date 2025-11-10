"""
Test script for RAG pipeline.
Run this to verify the RAG pipeline is working correctly.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from rag import EmbeddingManager, VectorStoreManager, RAGRetriever
from dotenv import load_dotenv

# Load environment variables from backend/.env (single source of truth)
backend_dir = Path(__file__).parent.parent
env_path = backend_dir / ".env"
load_dotenv(env_path)


def test_rag_pipeline():
    """Test the RAG pipeline with sample queries."""
    
    print("=" * 60)
    print("🧪 Testing RAG Pipeline")
    print("=" * 60)
    
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not found in environment variables.")
        print("   Please add it to your .env file.")
        return
    
    try:
        # Initialize embedding manager
        print("\n1️⃣  Initializing embedding manager...")
        embed_manager = EmbeddingManager(model="text-embedding-3-small")
        embed_model = embed_manager.get_embed_model()
        print("   ✅ Embedding manager initialized")
        
        # Load vector store
        storage_type = os.getenv("RAG_STORAGE_TYPE", "local")
        print(f"\n2️⃣  Loading vector store ({storage_type})...")
        
        if storage_type == "pinecone":
            if not os.getenv("PINECONE_API_KEY"):
                print("   ⚠️  PINECONE_API_KEY not found. Falling back to local storage.")
                storage_type = "local"
        
        if storage_type == "pinecone":
            vector_store = VectorStoreManager(
                embed_model=embed_model,
                storage_type="pinecone",
                index_name="hospital-assistant"
            )
        else:
            vector_store = VectorStoreManager(
                embed_model=embed_model,
                storage_type="local",
                persist_dir=str(backend_dir / "storage" / "local_index")
            )
        
        # Load index
        print("   Loading index...")
        index = vector_store.load_index()
        
        if not index:
            print("   ❌ No index found!")
            print("   Please run: python upload_embeddings.py --storage local")
            return
        
        print("   ✅ Vector store loaded")
        
        # Create retriever
        print("\n3️⃣  Creating retriever...")
        retriever = RAGRetriever(
            index=index,
            similarity_top_k=3,
            response_mode="compact"
        )
        print("   ✅ Retriever created")
        
        # Test queries
        print("\n4️⃣  Running test queries...")
        print("=" * 60)
        
        test_queries = [
            "What are the cafeteria hours?",
            "How do I book an appointment?",
            "Where is the parking located?",
            "What are the visiting hours for ICU?",
            "How can I contact Dr. Priya Sharma?",
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n📝 Query {i}: {query}")
            print("-" * 60)
            
            # Get context
            context = retriever.get_context(query)
            
            # Get full response
            response = retriever.query(query)
            
            print(f"📄 Context (top matches):")
            print(f"   {context[:200]}..." if len(context) > 200 else f"   {context}")
            print(f"\n💬 Response:")
            print(f"   {response}")
            print("-" * 60)
        
        print("\n" + "=" * 60)
        print("✅ All tests completed successfully!")
        print("=" * 60)
        
        # Performance info
        print("\n📊 Performance Info:")
        print(f"   Storage Type: {storage_type}")
        print(f"   Embedding Model: text-embedding-3-small")
        print(f"   Similarity Top K: 3")
        print(f"   Response Mode: compact")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_rag_pipeline()
