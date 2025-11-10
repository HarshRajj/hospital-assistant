"""
Script to upload embeddings to both Pinecone and local storage.
Processes the knowledge base and creates vector indices.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from rag import EmbeddingManager, VectorStoreManager, RAGConfig
from dotenv import load_dotenv

# Load environment variables from backend/.env (single source of truth)
backend_dir = Path(__file__).parent.parent
env_path = backend_dir / ".env"
load_dotenv(env_path)


def upload_embeddings(
    data_path: str = "data/Knowledgebase.txt",
    storage_type: str = "both",  # "local", "pinecone", or "both"
    embedding_model: str = "text-embedding-3-small"
):
    """
    Upload embeddings to vector stores.
    
    Args:
        data_path: Path to the knowledge base file/directory
        storage_type: Type of storage ("local", "pinecone", or "both")
        embedding_model: OpenAI embedding model to use
    """
    print("🚀 Starting embedding upload process...")
    
    # Print configuration
    RAGConfig.print_config()
    
    # Validate configuration
    if not RAGConfig.validate():
        print("\n❌ Configuration validation failed. Please check your .env file.")
        return
    
    # Initialize embedding manager
    print(f"📊 Initializing embedding manager with model: {embedding_model}")
    embed_manager = EmbeddingManager(model=embedding_model)
    
    # Load documents
    print(f"📄 Loading documents from: {data_path}")
    documents = embed_manager.load_documents(data_path)
    print(f"✅ Loaded {len(documents)} document(s)")
    
    # Get embedding model
    embed_model = embed_manager.get_embed_model()
    
    # Upload to local storage
    if storage_type in ["local", "both"]:
        print("\n💾 Creating local vector store...")
        local_store = VectorStoreManager(
            embed_model=embed_model,
            storage_type="local",
            persist_dir=str(backend_dir / "storage" / "local_index")
        )
        local_index = local_store.create_index(documents)
        print("✅ Local vector store created successfully!")
    
    # Upload to Pinecone
    if storage_type in ["pinecone", "both"]:
        print("\n☁️  Creating Pinecone vector store...")
        
        # Check for Pinecone credentials
        if not os.getenv("PINECONE_API_KEY"):
            print("⚠️  Warning: PINECONE_API_KEY not found in environment variables.")
            print("   Skipping Pinecone upload. Please add PINECONE_API_KEY to .env file.")
        else:
            pinecone_store = VectorStoreManager(
                embed_model=embed_model,
                storage_type="pinecone",
                index_name="hospital-assistant"
            )
            pinecone_index = pinecone_store.create_index(documents)
            print("✅ Pinecone vector store created successfully!")
    
    print("\n🎉 Embedding upload completed!")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Upload embeddings to vector stores")
    parser.add_argument(
        "--data-path",
        type=str,
        default="data/Knowledgebase.txt",
        help="Path to knowledge base file or directory"
    )
    parser.add_argument(
        "--storage",
        type=str,
        choices=["local", "pinecone", "both"],
        default="both",
        help="Storage type: local, pinecone, or both"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="text-embedding-3-small",
        help="OpenAI embedding model"
    )
    
    args = parser.parse_args()
    
    upload_embeddings(
        data_path=args.data_path,
        storage_type=args.storage,
        embedding_model=args.model
    )
