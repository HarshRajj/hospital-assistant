"""
Upload embeddings script with Gemini support (FREE)
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import argparse

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from llama_index.core import Settings, VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.storage.storage_context import StorageContext
from llama_index.embeddings.gemini import GeminiEmbedding

# Load environment
backend_dir = Path(__file__).parent.parent
env_path = backend_dir / ".env"
load_dotenv(env_path)

# Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL = os.getenv("RAG_GEMINI_EMBEDDING_MODEL", "models/embedding-001")
DATA_PATH = backend_dir / "data"
PERSIST_DIR = backend_dir / "storage" / "local_index"

# Chunk settings for faster processing
Settings.chunk_size = 256
Settings.chunk_overlap = 20

def create_gemini_embeddings():
    """Create embeddings using FREE Google Gemini"""
    print("=" * 70)
    print("🆓 Using FREE Google Gemini Embeddings")
    print(f"📦 Model: {GEMINI_MODEL}")
    print(f"✅ FREE Tier: 15,000 requests/day")
    print("=" * 70)
    
    if not GOOGLE_API_KEY or GOOGLE_API_KEY == "your_gemini_api_key_here":
        print("\n❌ ERROR: GOOGLE_API_KEY not set!")
        print("📝 Get your FREE API key from: https://aistudio.google.com/app/apikey")
        print("💡 Then add it to backend/.env:")
        print("   GOOGLE_API_KEY=your_key_here")
        return
    
    # Create Gemini embedding model
    embed_model = GeminiEmbedding(
        model_name=GEMINI_MODEL,
        api_key=GOOGLE_API_KEY
    )
    
    Settings.embed_model = embed_model
    
    # Load documents
    print(f"\n📄 Loading documents from: {DATA_PATH}")
    documents = SimpleDirectoryReader(
        input_dir=str(DATA_PATH),
        filename_as_id=True
    ).load_data()
    print(f"✅ Loaded {len(documents)} documents")
    
    # Create vector store index
    print(f"\n🔧 Creating vector index with Gemini embeddings...")
    print(f"   Chunk size: {Settings.chunk_size}")
    
    index = VectorStoreIndex.from_documents(
        documents,
        embed_model=embed_model,
        show_progress=True
    )
    
    # Persist to disk
    PERSIST_DIR.mkdir(parents=True, exist_ok=True)
    print(f"\n💾 Saving index to: {PERSIST_DIR}")
    index.storage_context.persist(persist_dir=str(PERSIST_DIR))
    
    print("\n" + "=" * 70)
    print("✅ SUCCESS! Gemini embeddings created and saved!")
    print("=" * 70)
    print(f"📁 Index location: {PERSIST_DIR}")
    print(f"🆓 Cost: $0.00 (using free tier!)")
    print(f"📊 Daily limit: 15,000 requests")
    print("\n✨ Your voice agent is ready to use with Gemini embeddings!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create Gemini embeddings (FREE)")
    parser.add_argument("--storage", default="local", help="Storage type")
    args = parser.parse_args()
    
    create_gemini_embeddings()
