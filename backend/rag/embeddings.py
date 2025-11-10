"""
Embeddings module for RAG pipeline using LlamaIndex.
Handles document loading and embedding generation.
"""

from llama_index.core import SimpleDirectoryReader, Document
from llama_index.embeddings.openai import OpenAIEmbedding
from typing import List
import os


class EmbeddingManager:
    """Manages document embeddings using OpenAI embeddings via LlamaIndex."""
    
    def __init__(self, model: str = "text-embedding-3-small"):
        """
        Initialize the embedding manager.
        
        Args:
            model: OpenAI embedding model to use (default: text-embedding-3-small for speed)
        """
        self.embed_model = OpenAIEmbedding(
            model=model,
            embed_batch_size=100  # Batch processing for speed
        )
    
    def load_documents(self, data_path: str) -> List[Document]:
        """
        Load documents from a directory or file.
        
        Args:
            data_path: Path to the data directory or file
            
        Returns:
            List of Document objects
        """
        if os.path.isfile(data_path):
            # Load single file
            with open(data_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return [Document(text=content, metadata={"source": data_path})]
        else:
            # Load from directory
            reader = SimpleDirectoryReader(
                input_dir=data_path,
                recursive=True
            )
            return reader.load_data()
    
    def get_embed_model(self):
        """Get the embedding model instance."""
        return self.embed_model
