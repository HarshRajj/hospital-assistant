import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import time

from llama_index.core.indices import VectorStoreIndex
from llama_index.core.storage.storage_context import StorageContext
from llama_index.core import Settings, load_index_from_storage
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.embeddings.openai import OpenAIEmbedding
from pinecone import Pinecone

from livekit.agents import Agent, AgentSession, AutoSubscribe, JobContext, WorkerOptions, cli, llm
from livekit.plugins import silero, openai

# Load environment variables
backend_dir = Path(__file__).parent.parent
env_path = backend_dir / ".env"
load_dotenv(env_path)

# Performance optimization: Configure global LlamaIndex settings
Settings.chunk_size = 512  # Smaller chunks for faster processing
Settings.chunk_overlap = 50  # Reduce overlap

# Configuration
STORAGE_TYPE = os.getenv("RAG_STORAGE_TYPE", "local")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "hospital-assistant")
EMBEDDING_MODEL = os.getenv("RAG_EMBEDDING_MODEL", "text-embedding-3-small")

# Load the existing hospital knowledge base index based on storage type
print(f"🔧 Loading hospital knowledge base from {STORAGE_TYPE} storage...")

if STORAGE_TYPE == "pinecone":
    if not PINECONE_API_KEY:
        print("❌ Error: PINECONE_API_KEY not set in .env file")
        print("   Please set your Pinecone API key or switch to local storage")
        index = None
    else:
        try:
            # Initialize Pinecone
            pc = Pinecone(api_key=PINECONE_API_KEY)
            pinecone_index = pc.Index(PINECONE_INDEX_NAME)
            
            # Create vector store
            vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
            
            # Create embedding model
            embed_model = OpenAIEmbedding(model=EMBEDDING_MODEL)
            
            # Create index from vector store
            index = VectorStoreIndex.from_vector_store(
                vector_store=vector_store,
                embed_model=embed_model
            )
            print(f"✅ Hospital knowledge base loaded from Pinecone ({PINECONE_INDEX_NAME})!")
        except Exception as e:
            print(f"❌ Error loading Pinecone index: {e}")
            print("   Please run: python scripts/upload_embeddings.py --storage pinecone")
            index = None
else:
    # Local storage (FAISS)
    PERSIST_DIR = backend_dir / "storage" / "local_index"
    
    if not PERSIST_DIR.exists():
        print("❌ Error: No index found at", PERSIST_DIR)
        print("   Please run: python scripts/upload_embeddings.py --storage local")
        index = None
    else:
        storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
        index = load_index_from_storage(storage_context)
        print(f"✅ Hospital knowledge base loaded from local storage!")


@llm.function_tool
async def search_hospital_knowledge(query: str) -> str:
    """Search the hospital's knowledge base for information about services, departments, doctors, hours, policies, and facilities.
    
    Use this function for ANY question about the hospital. Do not answer hospital questions without calling this function.
    
    Args:
        query: The question or topic to search for in the hospital knowledge base.
    """
    if not index:
        return "Knowledge base is not available. Please contact the information desk."
    
    try:
        total_start = time.time()
        print(f"\n{'='*60}")
        print(f"🔍 RAG FUNCTION CALLED!")
        print(f"� Query: '{query}'")
        print(f"{'='*60}")
        
        # STEP 1: Create query engine (should be instant - using cached index)
        engine_start = time.time()
        query_engine = index.as_query_engine(
            similarity_top_k=3,  # Balance between speed and accuracy
            response_mode="compact",  # Fastest mode - single LLM call
            streaming=False  # Disabled for function tools
        )
        engine_time = time.time() - engine_start
        print(f"⚡ Query engine created: {engine_time*1000:.0f}ms")
        
        # STEP 2: Execute RAG query (main bottleneck)
        query_start = time.time()
        response = await query_engine.aquery(query)
        query_time = time.time() - query_start
        print(f"⚡ RAG query executed: {query_time*1000:.0f}ms")
        
        total_time = time.time() - total_start
        print(f"✅ TOTAL RAG TIME: {total_time*1000:.0f}ms ({len(str(response))} chars)")
        print(f"� Answer: {str(response)[:150]}...")
        print(f"{'='*60}\n")
        
        return str(response)
    except Exception as e:
        print(f"❌ Error searching knowledge base: {e}")
        return "I'm having trouble accessing the knowledge base right now."


async def entrypoint(ctx: JobContext):
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    agent = Agent(
        instructions=(
            "You are a voice assistant for Arogya Med-City Hospital. "
            "\n\n"
            "CRITICAL RULES:\n"
            "1. You do NOT have any knowledge about this hospital in your training data\n"
            "2. You MUST call the search_hospital_knowledge function for EVERY question\n"
            "3. NEVER make up or guess any hospital information\n"
            "4. If you don't call the function, you're giving WRONG information\n"
            "\n"
            "For ANY question about the hospital, you MUST:\n"
            "Step 1: Call search_hospital_knowledge with the user's question\n"
            "Step 2: Wait for the result\n"
            "Step 3: Speak the answer naturally and BRIEFLY (1-2 sentences max)\n"
            "\n"
            "Questions that REQUIRE the function (no exceptions):\n"
            "- Departments, doctors, services, locations\n"
            "- Hours (cafeteria, visiting, operating)\n"
            "- Contact info, phone numbers, extensions\n"
            "- Facilities, parking, amenities\n"
            "- Policies, procedures, appointments\n"
            "\n"
            "IMPORTANT: Keep responses VERY SHORT and conversational. No lists, no asterisks, no special formatting."
        ),
        vad=silero.VAD.load(),
        stt="deepgram",  # Deepgram for fast STT
        llm=openai.LLM(model="gpt-4o-mini"),  # GPT-4o-mini has BEST function calling support
        tts="cartesia",  # Cartesia for fast TTS
        tools=[search_hospital_knowledge],
    )

    session = AgentSession()
    await session.start(agent=agent, room=ctx.room)

    await session.say(
        "Hello! Welcome to Arogya Med-City Hospital. How can I help you today?", 
        allow_interruptions=True
    )


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))