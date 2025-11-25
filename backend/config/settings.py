"""Centralized configuration management for hospital assistant."""
import os
from pathlib import Path
from typing import Literal
from dotenv import load_dotenv

# Load environment variables from backend/.env
backend_dir = Path(__file__).parent.parent
env_path = backend_dir / ".env"
load_dotenv(env_path)


class Settings:
    """Application settings loaded from environment variables."""
    
    # LiveKit Configuration
    LIVEKIT_URL: str = os.getenv("LIVEKIT_URL", "")
    LIVEKIT_API_KEY: str = os.getenv("LIVEKIT_API_KEY", "")
    LIVEKIT_API_SECRET: str = os.getenv("LIVEKIT_API_SECRET", "")
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # Google/Gemini Configuration
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    GEMINI_EMBEDDING_MODEL: str = os.getenv("RAG_GEMINI_EMBEDDING_MODEL", "models/text-embedding-004")
    
    # RAG Configuration
    RAG_STORAGE_TYPE: Literal["local", "pinecone"] = os.getenv("RAG_STORAGE_TYPE", "local")  # type: ignore
    RAG_EMBEDDING_PROVIDER: Literal["openai", "gemini"] = os.getenv("RAG_EMBEDDING_PROVIDER", "gemini")  # type: ignore
    RAG_CHUNK_SIZE: int = int(os.getenv("RAG_CHUNK_SIZE", "256"))
    RAG_CHUNK_OVERLAP: int = int(os.getenv("RAG_CHUNK_OVERLAP", "20"))
    RAG_SIMILARITY_TOP_K: int = int(os.getenv("RAG_SIMILARITY_TOP_K", "3"))
    
    # Pinecone Configuration
    PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY", "")
    PINECONE_INDEX_NAME: str = os.getenv("PINECONE_INDEX_NAME", "hospital-assistant")
    
    # Deepgram Configuration
    DEEPGRAM_API_KEY: str = os.getenv("DEEPGRAM_API_KEY", "")
    
    # Cartesia Configuration
    CARTESIA_API_KEY: str = os.getenv("CARTESIA_API_KEY", "")
    
    # Cerebras Configuration
    CEREBRAS_API_KEY: str = os.getenv("CEREBRAS_API_KEY", "")
    
    # Clerk Configuration
    CLERK_SECRET_KEY: str = os.getenv("CLERK_SECRET_KEY", "")
    
    # Paths
    BACKEND_DIR: Path = backend_dir
    STORAGE_DIR: Path = backend_dir / "storage"
    LOCAL_INDEX_DIR: Path = backend_dir / "storage" / "local_index"
    DATA_DIR: Path = backend_dir / "data"
    
    # API Configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    
    # CORS Configuration
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ]
    
    def validate_livekit(self) -> bool:
        """Check if LiveKit credentials are configured."""
        return bool(self.LIVEKIT_URL and self.LIVEKIT_API_KEY and self.LIVEKIT_API_SECRET)
    
    def validate_rag_storage(self) -> bool:
        """Check if RAG storage is properly configured."""
        if self.RAG_STORAGE_TYPE == "pinecone":
            return bool(self.PINECONE_API_KEY)
        else:
            return self.LOCAL_INDEX_DIR.exists()
    
    def get_embedding_api_key(self) -> str:
        """Get the appropriate API key for the selected embedding provider."""
        if self.RAG_EMBEDDING_PROVIDER == "gemini":
            return self.GOOGLE_API_KEY
        else:
            return self.OPENAI_API_KEY


# Singleton instance
settings = Settings()
