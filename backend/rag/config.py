"""
Configuration settings for RAG pipeline.
Centralized configuration for easy adjustments.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from backend/.env (single source of truth)
backend_dir = Path(__file__).parent.parent
env_path = backend_dir / ".env"
load_dotenv(env_path)


class RAGConfig:
    """Configuration class for RAG pipeline."""
    
    # Storage Configuration
    STORAGE_TYPE = os.getenv("RAG_STORAGE_TYPE", "local")  # "local" or "pinecone"
    LOCAL_STORAGE_DIR = os.getenv("RAG_LOCAL_STORAGE_DIR", "storage/local_index")
    PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "hospital-assistant")
    
    # Embedding Configuration
    EMBEDDING_MODEL = os.getenv("RAG_EMBEDDING_MODEL", "text-embedding-3-small")
    EMBEDDING_DIMENSION = 1536  # For text-embedding-3-small
    EMBEDDING_BATCH_SIZE = 100
    
    # Retrieval Configuration
    SIMILARITY_TOP_K = int(os.getenv("RAG_SIMILARITY_TOP_K", "2"))  # Keep low for speed
    RESPONSE_MODE = os.getenv("RAG_RESPONSE_MODE", "compact")  # "compact" or "tree_summarize"
    
    # Pinecone Configuration
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "")
    PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "us-east-1")
    PINECONE_METRIC = "cosine"
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    
    # Data Configuration
    DATA_PATH = os.getenv("RAG_DATA_PATH", "data/Knowledgebase.txt")
    
    @classmethod
    def validate(cls) -> bool:
        """
        Validate configuration.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        if not cls.OPENAI_API_KEY:
            print("❌ Error: OPENAI_API_KEY not set")
            return False
        
        if cls.STORAGE_TYPE == "pinecone" and not cls.PINECONE_API_KEY:
            print("❌ Error: PINECONE_API_KEY not set for Pinecone storage")
            return False
        
        return True
    
    @classmethod
    def print_config(cls):
        """Print current configuration (hiding API keys)."""
        print("\n" + "=" * 60)
        print("RAG Pipeline Configuration")
        print("=" * 60)
        print(f"Storage Type:       {cls.STORAGE_TYPE}")
        print(f"Embedding Model:    {cls.EMBEDDING_MODEL}")
        print(f"Embedding Dim:      {cls.EMBEDDING_DIMENSION}")
        print(f"Similarity Top K:   {cls.SIMILARITY_TOP_K}")
        print(f"Response Mode:      {cls.RESPONSE_MODE}")
        print(f"Data Path:          {cls.DATA_PATH}")
        
        if cls.STORAGE_TYPE == "local":
            print(f"Local Storage Dir:  {cls.LOCAL_STORAGE_DIR}")
        else:
            print(f"Pinecone Index:     {cls.PINECONE_INDEX_NAME}")
            print(f"Pinecone Region:    {cls.PINECONE_ENVIRONMENT}")
        
        print(f"OpenAI API Key:     {'✅ Set' if cls.OPENAI_API_KEY else '❌ Not Set'}")
        
        if cls.STORAGE_TYPE == "pinecone":
            print(f"Pinecone API Key:   {'✅ Set' if cls.PINECONE_API_KEY else '❌ Not Set'}")
        
        print("=" * 60 + "\n")


# Convenience function
def get_config() -> RAGConfig:
    """Get RAG configuration instance."""
    return RAGConfig
