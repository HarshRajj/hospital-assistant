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
from llama_index.embeddings.gemini import GeminiEmbedding
from pinecone import Pinecone

from livekit.agents import Agent, AgentSession, AutoSubscribe, JobContext, WorkerOptions, cli, llm
from livekit.plugins import silero, openai

# Load environment variables
backend_dir = Path(__file__).parent.parent
env_path = backend_dir / ".env"
load_dotenv(env_path)

# Performance optimization: Configure global LlamaIndex settings
Settings.chunk_size = 256  # SMALLER chunks = FASTER retrieval
Settings.chunk_overlap = 20  # Minimal overlap for speed

# Configuration
STORAGE_TYPE = os.getenv("RAG_STORAGE_TYPE", "local")
EMBEDDING_PROVIDER = os.getenv("RAG_EMBEDDING_PROVIDER", "gemini")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "hospital-assistant")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GEMINI_MODEL = os.getenv("RAG_GEMINI_EMBEDDING_MODEL", "models/embedding-001")

# Set up embedding model based on provider
if EMBEDDING_PROVIDER == "gemini":
    print(f"🆓 Using FREE Gemini embeddings: {GEMINI_MODEL}")
    Settings.embed_model = GeminiEmbedding(
        model_name=GEMINI_MODEL,
        api_key=GOOGLE_API_KEY
    )
else:
    print(f"Using OpenAI embeddings")
    Settings.embed_model = OpenAIEmbedding()

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
            
            # Create index from vector store (uses the global embed_model from Settings)
            index = VectorStoreIndex.from_vector_store(
                vector_store=vector_store
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
            """
                You are the compassionate, intelligent Voice Assistant for Arogya Med-City Hospital.

                ### PHASE 1: CONTEXT & INTENT ANALYSIS (Internal Process)
                Before generating a response, instantly evaluate the user's input for:
                1. **User Identity:** Are they a patient (anxious/in pain), a visitor (confused/lost), or staff?
                2. **Urgency Level:** Is this a medical emergency, a time-sensitive appointment, or a general inquiry?
                3. **Emotional State:** Are they frustrated, scared, or casual?

                ### PHASE 2: ADAPTIVE BEHAVIOR RULES
                * **If Emergency/Pain:** Tone must be calm, urgent, and reassuring. Prioritize safety instructions immediately.
                * **If Frustrated/Confused:** Tone must be apologetic and patient. Focus on solving the problem immediately.
                * **If Casual Inquiry:** Tone should be warm, bright, and welcoming.

                ### PHASE 3: KNOWLEDGE RETRIEVAL (CRITICAL)
                1.  You do NOT have internal knowledge of Arogya Med-City Hospital.
                2.  You **MUST** call the function `search_hospital_knowledge` for EVERY question regarding hospital data (doctors, timings, locations, policies).
                3.  **NEVER** guess or hallucinate facts. If you don't check the database, you are failing the user.

                ### PHASE 4: VOICE OUTPUT CONSTRAINTS
                * **Step 1:** Call `search_hospital_knowledge` with the specific query.
                * **Step 2:** Synthesize the returned data into a spoken response.
                * **Length:** Maximum 2 sentences. Keep it punchy.
                * **Style:** Natural, conversational English. Avoid robotic phrasing.
                * **Formatting:** NO lists, NO markdown, NO asterisks, NO special characters. (This text goes directly to a Text-to-Speech engine).

                ### EXAMPLE INTERACTIONS
                * *User (Panicked):* "My father is having chest pain, where do I go?"
                    * *Your thought:* Emergency context.
                    * *Action:* Call tool -> Get Emergency Ward location.
                    * *Response:* "Please head immediately to the Emergency Department on the Ground Floor, Gate 4. I am alerting the staff there."

                * *User (Casual):* "Can I get a coffee here?"
                    * *Your thought:* Visitor comfort context.
                    * *Action:* Call tool -> Get Cafeteria info.
                    * *Response:* "Yes, the cafeteria is open 24/7 on the first floor near the main lobby.
                """
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