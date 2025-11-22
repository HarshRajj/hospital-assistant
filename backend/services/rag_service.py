"""RAG (Retrieval-Augmented Generation) service for hospital knowledge base."""
import time
from typing import Optional
from pathlib import Path

from llama_index.core.indices import VectorStoreIndex
from llama_index.core.storage.storage_context import StorageContext
from llama_index.core import Settings, load_index_from_storage
from llama_index.core.query_engine import BaseQueryEngine
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.embeddings.gemini import GeminiEmbedding
from pinecone import Pinecone

from config import settings as app_settings


class RAGService:
    """Service for RAG-based hospital knowledge retrieval."""
    
    def __init__(self):
        """Initialize RAG service with embedding model and vector store."""
        self._index: Optional[VectorStoreIndex] = None
        self._configure_settings()
        self._load_index()
    
    def _configure_settings(self):
        """Configure global LlamaIndex settings for performance."""
        Settings.chunk_size = app_settings.RAG_CHUNK_SIZE
        Settings.chunk_overlap = app_settings.RAG_CHUNK_OVERLAP
        
        # Set up embedding model based on provider
        if app_settings.RAG_EMBEDDING_PROVIDER == "gemini":
            print(f"🆓 Using FREE Gemini embeddings: {app_settings.GEMINI_EMBEDDING_MODEL}")
            Settings.embed_model = GeminiEmbedding(
                model_name=app_settings.GEMINI_EMBEDDING_MODEL,
                api_key=app_settings.GOOGLE_API_KEY
            )
        else:
            print(f"Using OpenAI embeddings")
            Settings.embed_model = OpenAIEmbedding(
                api_key=app_settings.OPENAI_API_KEY
            )
    
    def _load_index(self):
        """Load the vector index based on configured storage type."""
        storage_type = app_settings.RAG_STORAGE_TYPE
        print(f"🔧 Loading hospital knowledge base from {storage_type} storage...")
        
        if storage_type == "pinecone":
            self._load_pinecone_index()
        else:
            self._load_local_index()
    
    def _load_pinecone_index(self):
        """Load index from Pinecone cloud storage."""
        if not app_settings.PINECONE_API_KEY:
            print("❌ Error: PINECONE_API_KEY not set in .env file")
            print("   Please set your Pinecone API key or switch to local storage")
            self._index = None
            return
        
        try:
            # Initialize Pinecone
            pc = Pinecone(api_key=app_settings.PINECONE_API_KEY)
            pinecone_index = pc.Index(app_settings.PINECONE_INDEX_NAME)
            
            # Create vector store
            vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
            
            # Create index from vector store
            self._index = VectorStoreIndex.from_vector_store(
                vector_store=vector_store
            )
            print(f"✅ Hospital knowledge base loaded from Pinecone ({app_settings.PINECONE_INDEX_NAME})!")
        except Exception as e:
            print(f"❌ Error loading Pinecone index: {e}")
            print("   Please run: python scripts/upload_embeddings.py --storage pinecone")
            self._index = None
    
    def _load_local_index(self):
        """Load index from local FAISS storage."""
        persist_dir = app_settings.LOCAL_INDEX_DIR
        
        if not persist_dir.exists():
            print(f"❌ Error: No index found at {persist_dir}")
            print("   Please run: python scripts/upload_embeddings.py --storage local")
            self._index = None
            return
        
        try:
            storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
            self._index = load_index_from_storage(storage_context)
            print(f"✅ Hospital knowledge base loaded from local storage!")
        except Exception as e:
            print(f"❌ Error loading local index: {e}")
            self._index = None
    
    def is_available(self) -> bool:
        """Check if the knowledge base is loaded and available."""
        return self._index is not None
    
    def create_query_engine(self) -> Optional[BaseQueryEngine]:
        """Create a query engine for the knowledge base.
        
        Returns:
            Query engine configured for optimal performance, or None if index unavailable
        """
        if not self.is_available():
            return None
        
        return self._index.as_query_engine(
            similarity_top_k=app_settings.RAG_SIMILARITY_TOP_K,
            response_mode="compact",  # Fastest mode - single LLM call
            streaming=False  # Disabled for function tools
        )
    
    async def search(self, query: str) -> str:
        """Search the hospital knowledge base for information.
        
        Args:
            query: The question or topic to search for
            
        Returns:
            Answer from the knowledge base, or error message if unavailable
        """
        if not self.is_available():
            return "Knowledge base is not available. Please contact the information desk."
        
        try:
            total_start = time.time()
            print(f"\n{'='*60}")
            print(f"🔍 RAG SEARCH INITIATED")
            print(f"📝 Query: '{query}'")
            print(f"{'='*60}")
            
            # Create query engine
            engine_start = time.time()
            query_engine = self.create_query_engine()
            engine_time = time.time() - engine_start
            print(f"⚡ Query engine created: {engine_time*1000:.0f}ms")
            
            # Execute RAG query
            query_start = time.time()
            response = await query_engine.aquery(query)
            query_time = time.time() - query_start
            print(f"⚡ RAG query executed: {query_time*1000:.0f}ms")
            
            total_time = time.time() - total_start
            result = str(response)
            print(f"✅ TOTAL RAG TIME: {total_time*1000:.0f}ms ({len(result)} chars)")
            print(f"💬 Answer: {result[:150]}...")
            print(f"{'='*60}\n")
            
            return result
        except Exception as e:
            print(f"❌ Error searching knowledge base: {e}")
            return "I'm having trouble accessing the knowledge base right now."
    
    def get_index(self) -> Optional[VectorStoreIndex]:
        """Get the underlying vector store index.
        
        Returns:
            Vector store index, or None if not available
        """
        return self._index


# Singleton instance
rag_service = RAGService()
