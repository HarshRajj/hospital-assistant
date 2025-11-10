"""
Utility functions for quick RAG setup.
Provides shortcuts for common operations without needing custom wrapper classes.
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

from llama_index.core import StorageContext, load_index_from_storage, VectorStoreIndex
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.query_engine import BaseQueryEngine

# Load environment variables
backend_dir = Path(__file__).parent.parent
env_path = backend_dir / ".env"
load_dotenv(env_path)


def load_vector_index(
    storage_type: Optional[str] = None,
    index_name: Optional[str] = None,
    persist_dir: Optional[str] = None,
    embedding_model: Optional[str] = None
) -> Optional[VectorStoreIndex]:
    """
    Load vector index from local or Pinecone storage.
    
    This is a convenience function that handles all the boilerplate
    for loading an existing index. Perfect for quick scripts and integrations.
    
    Args:
        storage_type: "local" or "pinecone" (defaults to RAG_STORAGE_TYPE env var)
        index_name: Pinecone index name (defaults to PINECONE_INDEX_NAME env var)
        persist_dir: Local storage directory (defaults to RAG_LOCAL_STORAGE_DIR env var)
        embedding_model: Embedding model name (defaults to RAG_EMBEDDING_MODEL env var)
    
    Returns:
        VectorStoreIndex instance or None if loading fails
    
    Example:
        >>> # Load from environment defaults
        >>> index = load_vector_index()
        >>> 
        >>> # Override storage type
        >>> index = load_vector_index(storage_type="pinecone")
        >>> 
        >>> # Custom local directory
        >>> index = load_vector_index(storage_type="local", persist_dir="./my_index")
    """
    # Get defaults from environment
    storage_type = storage_type or os.getenv("RAG_STORAGE_TYPE", "local")
    index_name = index_name or os.getenv("PINECONE_INDEX_NAME", "hospital-assistant")
    persist_dir = persist_dir or os.getenv("RAG_LOCAL_STORAGE_DIR", "storage/local_index")
    embedding_model = embedding_model or os.getenv("RAG_EMBEDDING_MODEL", "text-embedding-3-small")
    
    # Convert relative path to absolute
    if not os.path.isabs(persist_dir):
        persist_dir = str(backend_dir / persist_dir)
    
    print(f"🔧 Loading index from {storage_type} storage...")
    
    if storage_type == "pinecone":
        return _load_pinecone_index(index_name, embedding_model)
    else:
        return _load_local_index(persist_dir, embedding_model)


def _load_pinecone_index(index_name: str, embedding_model: str) -> Optional[VectorStoreIndex]:
    """Load index from Pinecone."""
    try:
        from pinecone import Pinecone
        
        api_key = os.getenv("PINECONE_API_KEY")
        if not api_key:
            print("❌ Error: PINECONE_API_KEY not set")
            return None
        
        # Initialize Pinecone
        pc = Pinecone(api_key=api_key)
        pinecone_index = pc.Index(index_name)
        
        # Create vector store
        vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
        
        # Create embedding model
        embed_model = OpenAIEmbedding(model=embedding_model)
        
        # Load index
        index = VectorStoreIndex.from_vector_store(
            vector_store=vector_store,
            embed_model=embed_model
        )
        
        print(f"✅ Loaded from Pinecone ({index_name})")
        return index
        
    except Exception as e:
        print(f"❌ Error loading Pinecone index: {e}")
        print("   Make sure you've uploaded embeddings: python scripts/upload_embeddings.py --storage pinecone")
        return None


def _load_local_index(persist_dir: str, embedding_model: str) -> Optional[VectorStoreIndex]:
    """Load index from local storage."""
    try:
        if not os.path.exists(persist_dir):
            print(f"❌ Error: No index found at {persist_dir}")
            print("   Please run: python scripts/upload_embeddings.py --storage local")
            return None
        
        # Create embedding model
        embed_model = OpenAIEmbedding(model=embedding_model)
        
        # Load from storage
        storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
        index = load_index_from_storage(storage_context, embed_model=embed_model)
        
        print(f"✅ Loaded from local storage ({persist_dir})")
        return index
        
    except Exception as e:
        print(f"❌ Error loading local index: {e}")
        print("   Please run: python scripts/upload_embeddings.py --storage local")
        return None


def create_query_engine(
    index: Optional[VectorStoreIndex] = None,
    similarity_top_k: Optional[int] = None,
    streaming: bool = False
) -> Optional[BaseQueryEngine]:
    """
    Create a query engine with optimized settings.
    
    Args:
        index: VectorStoreIndex instance (if None, loads from environment defaults)
        similarity_top_k: Number of similar chunks to retrieve (defaults to RAG_SIMILARITY_TOP_K env var)
        streaming: Enable streaming responses
    
    Returns:
        Query engine instance or None if index loading fails
    
    Example:
        >>> # Create with auto-loaded index
        >>> query_engine = create_query_engine(similarity_top_k=2)
        >>> response = query_engine.query("What are visiting hours?")
        >>> 
        >>> # Use existing index
        >>> index = load_vector_index()
        >>> query_engine = create_query_engine(index, similarity_top_k=3)
    """
    # Load index if not provided
    if index is None:
        index = load_vector_index()
        if index is None:
            return None
    
    # Get default top_k from environment
    if similarity_top_k is None:
        similarity_top_k = int(os.getenv("RAG_SIMILARITY_TOP_K", "2"))
    
    print(f"🔧 Creating query engine (top_k={similarity_top_k}, streaming={streaming})")
    
    # Create query engine
    query_engine = index.as_query_engine(
        similarity_top_k=similarity_top_k,
        streaming=streaming
    )
    
    print("✅ Query engine ready!")
    return query_engine


def get_rag_config() -> dict:
    """
    Get current RAG configuration as a dictionary.
    
    Returns:
        Dictionary with all RAG configuration values
    
    Example:
        >>> config = get_rag_config()
        >>> print(f"Storage type: {config['storage_type']}")
        >>> print(f"Embedding model: {config['embedding_model']}")
    """
    return {
        "storage_type": os.getenv("RAG_STORAGE_TYPE", "local"),
        "embedding_model": os.getenv("RAG_EMBEDDING_MODEL", "text-embedding-3-small"),
        "similarity_top_k": int(os.getenv("RAG_SIMILARITY_TOP_K", "2")),
        "response_mode": os.getenv("RAG_RESPONSE_MODE", "compact"),
        "data_path": os.getenv("RAG_DATA_PATH", "data/Knowledgebase.txt"),
        "local_storage_dir": os.getenv("RAG_LOCAL_STORAGE_DIR", "storage/local_index"),
        "pinecone_index_name": os.getenv("PINECONE_INDEX_NAME", "hospital-assistant"),
        "pinecone_environment": os.getenv("PINECONE_ENVIRONMENT", "us-east-1"),
    }
