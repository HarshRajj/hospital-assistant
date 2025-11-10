"""
RAG Pipeline for Hospital Assistant.
Provides a modular, fast, and efficient retrieval system using LlamaIndex.

This module supports both:
1. Pure LlamaIndex usage (lightweight, direct)
2. Custom wrapper classes (flexible, feature-rich)

Quick Start (Pure LlamaIndex):
    >>> from rag.utils import load_vector_index
    >>> index = load_vector_index(storage_type="local")
    >>> query_engine = index.as_query_engine(similarity_top_k=2)
    >>> response = query_engine.query("What are the cafeteria hours?")

Advanced Usage (Custom Wrappers):
    >>> from rag import EmbeddingManager, VectorStoreManager, RAGRetriever
    >>> embed_manager = EmbeddingManager()
    >>> vector_store = VectorStoreManager(embed_manager.get_embed_model())
    >>> index = vector_store.load_index()
    >>> retriever = RAGRetriever(index)
    >>> response = retriever.query("What are the cafeteria hours?")
"""

from .embeddings import EmbeddingManager
from .vector_store import VectorStoreManager
from .retriever import RAGRetriever
from .config import RAGConfig, get_config
from .utils import load_vector_index, create_query_engine

__all__ = [
    "EmbeddingManager",
    "VectorStoreManager", 
    "RAGRetriever",
    "RAGConfig",
    "get_config",
    "load_vector_index",
    "create_query_engine"
]
