import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import time

from llama_index.core import StorageContext, load_index_from_storage, VectorStoreIndex, Settings
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from pinecone import Pinecone

from livekit.agents import Agent, AgentSession, AutoSubscribe, JobContext, WorkerOptions, cli, llm
from livekit.plugins import noise_cancellation, silero, openai
# from livekit.plugins import deepgram

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
    
    Args:
        query: The question or topic to search for in the hospital knowledge base.
    """
    if not index:
        return "Knowledge base is not available. Please contact the information desk."
    
    try:
        start_time = time.time()
        print(f"🔍 Searching knowledge base for: '{query}'")
        
        # OPTIMIZATION 1: Reduce to top 1 result for faster response
        # OPTIMIZATION 2: Use compact mode for minimal processing
        # OPTIMIZATION 3: Disable LLM synthesis - return raw context only
        query_engine = index.as_query_engine(
            similarity_top_k=1,  # Reduced from 2 to 1 (50% faster)
            response_mode="compact",  # Fast mode
            streaming=False  # Disabled for function tools
        )
        
        response = await query_engine.aquery(query)
        
        elapsed = time.time() - start_time
        print(f"✅ Found answer in {elapsed:.2f}s ({len(str(response))} chars)")
        
        return str(response)
    except Exception as e:
        print(f"❌ Error searching knowledge base: {e}")
        return "I'm having trouble accessing the knowledge base right now."


async def entrypoint(ctx: JobContext):
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    agent = Agent(
        instructions=(
            "You are a helpful voice assistant for Arogya Med-City Hospital. "
            "You assist patients, visitors, and staff with hospital information, appointments, and services. "
            "Your responses should be concise, friendly, and conversational for voice interaction. "
            "Avoid complex formatting, symbols, asterisks, or unpronounceable punctuation. "
            "\n\n"
            "IMPORTANT: You have access to the hospital's official knowledge base through the 'search_hospital_knowledge' function. "
            "ALWAYS use this function when users ask about:\n"
            "- Hospital departments, services, locations, or facilities\n"
            "- Doctor information, availability, or specialties\n"
            "- Visiting hours, parking, or amenities\n"
            "- Appointment booking procedures or policies\n"
            "- Operating hours for any hospital service\n"
            "- Contact information, extensions, or phone numbers\n"
            "- Emergency procedures or triage information\n"
            "\n"
            "Do NOT make up information about the hospital. Always use the search function to get accurate, official information. "
            "Present the information naturally and conversationally."
        ),
        vad=silero.VAD.load(),
        stt="assemblyai/universal-streaming:en",
        # llm="cerebras/llama3.1-8b",
        llm=openai.LLM.with_cerebras(model="llama3.1-8b",),
        tts="cartesia/sonic-3:9626c31c-bec5-4cca-baa8-f8ba9e84c8bc",
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