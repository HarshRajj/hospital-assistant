"""RAG service for hospital knowledge base retrieval."""
import asyncio
from concurrent.futures import ThreadPoolExecutor
import threading
from typing import Optional

from llama_index.core.indices import VectorStoreIndex
from llama_index.core.storage.storage_context import StorageContext
from llama_index.core import Settings, load_index_from_storage
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.embeddings.gemini import GeminiEmbedding
from pinecone import Pinecone

from config import settings as app_settings

# Thread pool for running sync operations - created per-thread
_thread_local = threading.local()


def _get_executor():
    """Get or create a thread-local executor."""
    if not hasattr(_thread_local, 'executor'):
        _thread_local.executor = ThreadPoolExecutor(max_workers=2)
    return _thread_local.executor


class RAGService:
    """Service for RAG-based hospital knowledge retrieval."""
    
    def __init__(self):
        # Don't initialize anything here - defer to first use
        self._index: Optional[VectorStoreIndex] = None
        self._initialized = False
        self._lock = threading.Lock()
    
    def _configure_settings(self):
        """Configure LlamaIndex settings."""
        Settings.chunk_size = app_settings.RAG_CHUNK_SIZE
        Settings.chunk_overlap = app_settings.RAG_CHUNK_OVERLAP
        Settings.embed_model = GeminiEmbedding(
            model_name=app_settings.GEMINI_EMBEDDING_MODEL,
            api_key=app_settings.GOOGLE_API_KEY
        )
    
    def _initialize_sync(self):
        """Initialize the service synchronously - called from thread pool."""
        with self._lock:
            if self._initialized:
                return
            
            print("🔄 Initializing RAG service...")
            self._configure_settings()
            self._load_index()
            self._initialized = True
    
    def _load_index(self):
        """Load vector index from configured storage (Pinecone or local)."""
        storage_type = app_settings.RAG_STORAGE_TYPE
        
        if storage_type == "pinecone":
            self._load_pinecone_index()
        else:
            self._load_local_index()
    
    def _load_pinecone_index(self):
        """Load index from Pinecone cloud storage."""
        if not app_settings.PINECONE_API_KEY:
            print("❌ PINECONE_API_KEY not set")
            return
        
        try:
            pc = Pinecone(api_key=app_settings.PINECONE_API_KEY)
            pinecone_index = pc.Index(app_settings.PINECONE_INDEX_NAME)
            vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
            self._index = VectorStoreIndex.from_vector_store(vector_store=vector_store)
            print("✅ Knowledge base loaded from Pinecone")
        except Exception as e:
            print(f"❌ Pinecone error: {e}")
    
    def _load_local_index(self):
        """Load index from local storage."""
        persist_dir = app_settings.LOCAL_INDEX_DIR
        
        if not persist_dir.exists():
            print(f"❌ No index found at {persist_dir}")
            return
        
        try:
            storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
            self._index = load_index_from_storage(storage_context)
            print("✅ Knowledge base loaded from local storage")
        except Exception as e:
            print(f"❌ Local storage error: {e}")
    
    def is_available(self) -> bool:
        """Check if the knowledge base can be loaded."""
        return True  # Always return True, we'll init lazily
    
    def _sync_search(self, query: str) -> str:
        """Synchronous search - runs in thread pool to avoid event loop issues."""
        # Initialize on first use (in the thread pool thread)
        self._initialize_sync()
        
        if self._index is None:
            return "Knowledge base is not available. Please call (555) 100-2000 for assistance."
        
        try:
            query_engine = self._index.as_query_engine(
                similarity_top_k=app_settings.RAG_SIMILARITY_TOP_K,
                response_mode="compact",
                streaming=False
            )
            # Use sync query to avoid gRPC event loop issues
            response = query_engine.query(query)
            result = str(response)
            print(f"✅ RAG search result for '{query}': {result[:100]}...")
            return result
        except Exception as e:
            print(f"❌ RAG search error: {e}")
            return f"Error searching knowledge base. Please call (555) 100-2000."
    
    async def search(self, query: str) -> str:
        """Search the hospital knowledge base.
        
        Args:
            query: The question to search for
            
        Returns:
            Answer from the knowledge base
        """
        try:
            loop = asyncio.get_running_loop()
            executor = _get_executor()
            # Run sync search in thread pool to avoid gRPC event loop conflicts
            result = await loop.run_in_executor(executor, self._sync_search, query)
            return result
        except Exception as e:
            print(f"❌ RAG async search error: {e}")
            return "Error accessing knowledge base. Please call (555) 100-2000."


# Create instance but don't initialize - initialization happens on first search
rag_service = RAGService()
