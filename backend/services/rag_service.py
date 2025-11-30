"""RAG service for hospital knowledge base retrieval."""
from typing import Optional

from llama_index.core.indices import VectorStoreIndex
from llama_index.core.storage.storage_context import StorageContext
from llama_index.core import Settings, load_index_from_storage
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.embeddings.gemini import GeminiEmbedding
from pinecone import Pinecone

from config import settings as app_settings


class RAGService:
    """Service for RAG-based hospital knowledge retrieval."""
    
    def __init__(self):
        self._index: Optional[VectorStoreIndex] = None
        self._configure_settings()
        self._load_index()
    
    def _configure_settings(self):
        """Configure LlamaIndex settings."""
        Settings.chunk_size = app_settings.RAG_CHUNK_SIZE
        Settings.chunk_overlap = app_settings.RAG_CHUNK_OVERLAP
        Settings.embed_model = GeminiEmbedding(
            model_name=app_settings.GEMINI_EMBEDDING_MODEL,
            api_key=app_settings.GOOGLE_API_KEY
        )
    
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
        """Check if the knowledge base is loaded and available."""
        return self._index is not None
    
    async def search(self, query: str) -> str:
        """Search the hospital knowledge base.
        
        Args:
            query: The question to search for
            
        Returns:
            Answer from the knowledge base
        """
        if not self.is_available():
            return "Knowledge base is not available."
        
        try:
            query_engine = self._index.as_query_engine(
                similarity_top_k=app_settings.RAG_SIMILARITY_TOP_K,
                response_mode="compact",
                streaming=False
            )
            response = await query_engine.aquery(query)
            return str(response)
        except Exception as e:
            print(f"❌ RAG search error: {e}")
            return "Error accessing knowledge base."


rag_service = RAGService()
