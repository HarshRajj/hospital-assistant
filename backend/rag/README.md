# RAG Pipeline for Hospital Assistant

## Overview
This RAG (Retrieval-Augmented Generation) pipeline provides fast and efficient knowledge retrieval for the hospital voice assistant using LlamaIndex. It supports both **Pinecone** (cloud) and **local storage** (FAISS) for maximum flexibility.

## Architecture

```
backend/
├── rag/
│   ├── __init__.py           # Module exports
│   ├── embeddings.py         # Document loading & embedding generation
│   ├── vector_store.py       # Pinecone & local storage management
│   └── retriever.py          # Fast retrieval interface
├── scripts/
│   └── upload_embeddings.py  # Upload script for creating indices
├── data/
│   └── Knowledgebase.txt     # Hospital knowledge base (Markdown)
└── storage/
    └── local_index/          # Local vector store (auto-generated)
```

## Features

✅ **Dual Storage Support**: Pinecone (cloud) and local (FAISS)  
✅ **Fast Retrieval**: Optimized for voice agent responses (<500ms)  
✅ **Modular Design**: Easy to extend and maintain  
✅ **Batch Processing**: Efficient embedding generation  
✅ **Automatic Persistence**: Local indices saved to disk  

## Setup

### 1. Install Dependencies

```bash
pip install llama-index llama-index-embeddings-openai llama-index-vector-stores-pinecone pinecone-client python-dotenv
```

### 2. Configure Environment Variables

Create a `.env` file in the `voice-agent` directory:

```env
# OpenAI API Key (required)
OPENAI_API_KEY=your_openai_api_key

# Pinecone Configuration (optional, for cloud storage)
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_ENVIRONMENT=us-east-1

# RAG Configuration
RAG_STORAGE_TYPE=local  # Options: "local" or "pinecone"
```

### 3. Upload Embeddings

Run the upload script to create vector indices:

```bash
# Upload to both local and Pinecone
cd backend/scripts
python upload_embeddings.py --storage both

# Upload to local only (no Pinecone required)
python upload_embeddings.py --storage local

# Upload to Pinecone only
python upload_embeddings.py --storage pinecone

# Custom data path
python upload_embeddings.py --data-path ../data/Knowledgebase.txt --storage local
```

## Usage

### In Voice Agent

The RAG pipeline is automatically integrated into the voice agent:

```python
from rag import EmbeddingManager, VectorStoreManager, RAGRetriever

# Initialize
embed_manager = EmbeddingManager(model="text-embedding-3-small")
vector_store = VectorStoreManager(
    embed_model=embed_manager.get_embed_model(),
    storage_type="local",  # or "pinecone"
    persist_dir="../storage/local_index"
)

# Load index
index = vector_store.load_index()

# Create retriever
retriever = RAGRetriever(
    index=index,
    similarity_top_k=2,  # Number of relevant chunks
    response_mode="compact"  # Fast mode
)

# Query
context = retriever.get_context("What are the cafeteria hours?")
```

### Standalone Usage

```python
from rag import RAGRetriever

# Query the knowledge base
response = retriever.query("How do I book an appointment?")
print(response)
```

## Performance Optimization

### Speed Optimizations
- **Embedding Model**: `text-embedding-3-small` (faster than `text-embedding-3-large`)
- **Top K**: Set to 2-3 for voice responses (balance speed vs. accuracy)
- **Response Mode**: `compact` mode for fastest synthesis
- **Batch Processing**: Embeddings generated in batches of 100

### Memory Optimization
- Local indices are persisted to disk (not loaded into memory until needed)
- Pinecone handles storage in the cloud (minimal local memory)

## Storage Comparison

| Feature | Local Storage | Pinecone |
|---------|--------------|----------|
| **Setup** | Easy (no API key) | Requires API key |
| **Speed** | Very fast | Fast (network latency) |
| **Scalability** | Limited by disk | Highly scalable |
| **Cost** | Free | Paid (free tier available) |
| **Best For** | Development, small datasets | Production, large datasets |

## Troubleshooting

### Issue: "No existing index found"
**Solution**: Run `upload_embeddings.py` to create the index first.

### Issue: Pinecone connection error
**Solution**: Check your `PINECONE_API_KEY` and `PINECONE_ENVIRONMENT` in `.env`

### Issue: Slow responses
**Solution**: 
- Reduce `similarity_top_k` (default: 3 → try 2)
- Use local storage instead of Pinecone
- Use `text-embedding-3-small` model

### Issue: Out of memory
**Solution**: The local index is persisted to disk. Make sure you're calling `load_index()` instead of `create_index()` for existing indices.

## Advanced Configuration

### Custom Embedding Model

```python
embed_manager = EmbeddingManager(model="text-embedding-3-large")
```

### Adjust Retrieval Parameters

```python
retriever = RAGRetriever(
    index=index,
    similarity_top_k=5,  # More context (slower)
    response_mode="tree_summarize"  # Better quality (slower)
)
```

### Use Both Storage Types

You can maintain both local and Pinecone indices simultaneously:

```bash
python upload_embeddings.py --storage both
```

Then switch between them using the `RAG_STORAGE_TYPE` environment variable.

## Next Steps

1. ✅ Upload your knowledge base embeddings
2. ✅ Test the retriever standalone
3. ✅ Integrate with voice agent
4. ⏳ Monitor performance and adjust parameters
5. ⏳ Add more documents to the knowledge base

## API Reference

### EmbeddingManager
- `load_documents(data_path)`: Load documents from file/directory
- `get_embed_model()`: Get the embedding model instance

### VectorStoreManager
- `create_index(documents)`: Create new index from documents
- `load_index()`: Load existing index
- `get_index()`: Get current index instance

### RAGRetriever
- `query(query_text)`: Full RAG query with response
- `retrieve(query_text)`: Retrieve relevant nodes only
- `get_context(query_text)`: Get raw context text
