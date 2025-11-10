"""
Vector Store module for RAG pipeline.
Supports both Pinecone (cloud) and local storage using LlamaIndex.
"""

from llama_index.core import VectorStoreIndex, StorageContext, load_index_from_storage
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.core.vector_stores import SimpleVectorStore
from typing import List, Optional
from llama_index.core import Document
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from backend/.env
backend_dir = Path(__file__).parent.parent
env_path = backend_dir / ".env"
load_dotenv(env_path)


class VectorStoreManager:
    """Manages vector stores for both Pinecone and local storage."""
    
    def __init__(
        self,
        embed_model,
        storage_type: str = "local",  # "local" or "pinecone"
        index_name: str = "hospital-assistant",
        persist_dir: str = "./storage"
    ):
        """
        Initialize the vector store manager.
        
        Args:
            embed_model: LlamaIndex embedding model
            storage_type: Type of storage ("local" or "pinecone")
            index_name: Name of the index for Pinecone
            persist_dir: Directory for local storage
        """
        self.embed_model = embed_model
        self.storage_type = storage_type
        self.index_name = index_name
        self.persist_dir = persist_dir
        self.index = None
        
    def create_index(self, documents: List[Document]) -> VectorStoreIndex:
        """
        Create a new index from documents.
        
        Args:
            documents: List of Document objects
            
        Returns:
            VectorStoreIndex instance
        """
        if self.storage_type == "pinecone":
            return self._create_pinecone_index(documents)
        else:
            return self._create_local_index(documents)
    
    def _create_pinecone_index(self, documents: List[Document]) -> VectorStoreIndex:
        """Create Pinecone vector store index."""
        from pinecone import Pinecone, ServerlessSpec
        
        # Initialize Pinecone
        pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        
        # Create index if it doesn't exist
        if self.index_name not in pc.list_indexes().names():
            pc.create_index(
                name=self.index_name,
                dimension=1536,  # text-embedding-3-small dimension
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region=os.getenv("PINECONE_ENVIRONMENT", "us-east-1")
                )
            )
        
        # Get the index
        pinecone_index = pc.Index(self.index_name)
        
        # Create vector store
        vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        
        # Create and return index
        self.index = VectorStoreIndex.from_documents(
            documents,
            storage_context=storage_context,
            embed_model=self.embed_model,
            show_progress=True
        )
        
        return self.index
    
    def _create_local_index(self, documents: List[Document]) -> VectorStoreIndex:
        """Create local vector store index."""
        # Create index
        self.index = VectorStoreIndex.from_documents(
            documents,
            embed_model=self.embed_model,
            show_progress=True
        )
        
        # Persist to disk
        os.makedirs(self.persist_dir, exist_ok=True)
        self.index.storage_context.persist(persist_dir=self.persist_dir)
        
        return self.index
    
    def load_index(self) -> Optional[VectorStoreIndex]:
        """
        Load an existing index.
        
        Returns:
            VectorStoreIndex instance or None if not found
        """
        if self.storage_type == "pinecone":
            return self._load_pinecone_index()
        else:
            return self._load_local_index()
    
    def _load_pinecone_index(self) -> Optional[VectorStoreIndex]:
        """Load Pinecone index."""
        try:
            from pinecone import Pinecone
            
            pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
            pinecone_index = pc.Index(self.index_name)
            
            vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
            
            self.index = VectorStoreIndex.from_vector_store(
                vector_store=vector_store,
                embed_model=self.embed_model
            )
            
            return self.index
        except Exception as e:
            print(f"Error loading Pinecone index: {e}")
            return None
    
    def _load_local_index(self) -> Optional[VectorStoreIndex]:
        """Load local index."""
        try:
            if not os.path.exists(self.persist_dir):
                print(f"Storage directory {self.persist_dir} not found.")
                return None
            
            storage_context = StorageContext.from_defaults(
                persist_dir=self.persist_dir
            )
            
            self.index = load_index_from_storage(
                storage_context,
                embed_model=self.embed_model
            )
            
            return self.index
        except Exception as e:
            print(f"Error loading local index: {e}")
            return None
    
    def get_index(self) -> Optional[VectorStoreIndex]:
        """Get the current index instance."""
        return self.index
