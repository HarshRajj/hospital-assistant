"""
Retriever module for fast and efficient RAG queries.
"""

from llama_index.core import VectorStoreIndex
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.response_synthesizers import get_response_synthesizer
from llama_index.core.response_synthesizers import ResponseMode
from typing import Optional, List


class RAGRetriever:
    """Fast retriever for RAG pipeline optimized for voice agent responses."""
    
    def __init__(
        self,
        index: VectorStoreIndex,
        similarity_top_k: int = 2,  # Optimized for speed (reduced from 3)
        response_mode: str = "compact"  # Fast response mode
    ):
        """
        Initialize the RAG retriever.
        
        Args:
            index: VectorStoreIndex instance
            similarity_top_k: Number of similar documents to retrieve (2 is optimal for voice)
            response_mode: Response synthesis mode ("compact" for speed, "tree_summarize" for quality)
        """
        self.index = index
        self.similarity_top_k = similarity_top_k
        
        # Create retriever
        self.retriever = VectorIndexRetriever(
            index=index,
            similarity_top_k=similarity_top_k,
        )
        
        # Create response synthesizer (optimized for speed)
        response_mode_enum = ResponseMode.COMPACT if response_mode == "compact" else ResponseMode.TREE_SUMMARIZE
        self.response_synthesizer = get_response_synthesizer(
            response_mode=response_mode_enum,
        )
        
        # Create query engine
        self.query_engine = RetrieverQueryEngine(
            retriever=self.retriever,
            response_synthesizer=self.response_synthesizer,
        )
    
    async def aquery(self, query_text: str) -> str:
        """
        Async query the RAG pipeline and return a response.
        
        Args:
            query_text: User query
            
        Returns:
            Generated response
        """
        response = await self.query_engine.aquery(query_text)
        return str(response)
    
    def query(self, query_text: str) -> str:
        """
        Query the RAG pipeline and return a response (sync version).
        
        Args:
            query_text: User query
            
        Returns:
            Generated response
        """
        response = self.query_engine.query(query_text)
        return str(response)
    
    def retrieve(self, query_text: str) -> List:
        """
        Retrieve relevant documents without synthesis.
        
        Args:
            query_text: User query
            
        Returns:
            List of retrieved nodes
        """
        nodes = self.retriever.retrieve(query_text)
        return nodes
    
    def get_context(self, query_text: str) -> str:
        """
        Get raw context from retrieved documents.
        
        Args:
            query_text: User query
            
        Returns:
            Concatenated context from retrieved documents
        """
        nodes = self.retrieve(query_text)
        context = "\n\n".join([node.get_content() for node in nodes])
        return context
