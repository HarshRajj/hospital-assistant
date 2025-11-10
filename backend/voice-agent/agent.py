import os
import sys
from pathlib import Path
from dotenv import load_dotenv

from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import noise_cancellation, silero

# Add backend directory to path for importing RAG modules
sys.path.append(str(Path(__file__).parent.parent))

from rag import EmbeddingManager, VectorStoreManager, RAGRetriever

# Load environment variables from backend/.env (single source of truth)
backend_dir = Path(__file__).parent.parent
env_path = backend_dir / ".env"
load_dotenv(env_path)


class Assistant(Agent):
    def __init__(self, rag_retriever=None) -> None:
        """
        Initialize the Assistant with optional RAG retriever.
        
        Args:
            rag_retriever: RAGRetriever instance for knowledge base queries
        """
        # Base instructions for the agent
        base_instructions = """You are a helpful voice AI assistant for Arogya Med-City Hospital.
You assist patients, visitors, and staff with hospital information, appointments, directions, and services.
Your responses are concise, accurate, and friendly - perfect for voice interaction.
Avoid complex formatting, emojis, asterisks, or symbols in your responses.

IMPORTANT: You have access to the hospital's knowledge base. When answering questions about:
- Hospital services, departments, or facilities
- Doctor information and availability
- Visiting hours, parking, or amenities
- Appointment booking or policies
- Any hospital-specific information

You MUST use the provided context from the knowledge base to give accurate, specific answers.
Do not make up information. If the context doesn't contain the answer, politely say so and offer to connect them with the appropriate department."""

        super().__init__(instructions=base_instructions)
        self.rag_retriever = rag_retriever
    
    def get_context(self, query: str) -> str:
        """
        Retrieve context from RAG pipeline for a given query.
        
        Args:
            query: User's question
            
        Returns:
            Retrieved context or empty string
        """
        if not self.rag_retriever:
            return ""
        
        try:
            print(f"🔍 Retrieving context for: '{query}'")
            context = self.rag_retriever.get_context(query)
            
            if context:
                print(f"✅ Retrieved context ({len(context)} chars)")
                return context
            else:
                print("⚠️  No relevant context found")
                return ""
                
        except Exception as e:
            print(f"❌ Error retrieving context: {e}")
            return ""



async def entrypoint(ctx: agents.JobContext):
    """
    Main entrypoint for the voice agent with RAG integration.
    """
    # Initialize RAG pipeline
    rag_retriever = None
    storage_type = os.getenv("RAG_STORAGE_TYPE", "local")  # "local" or "pinecone"
    
    try:
        print(f"🔧 Initializing RAG pipeline with {storage_type} storage...")
        
        # Initialize embedding manager
        embed_manager = EmbeddingManager(model="text-embedding-3-small")
        embed_model = embed_manager.get_embed_model()
        
        # Load vector store
        if storage_type == "pinecone":
            vector_store = VectorStoreManager(
                embed_model=embed_model,
                storage_type="pinecone",
                index_name="hospital-assistant"
            )
        else:
            vector_store = VectorStoreManager(
                embed_model=embed_model,
                storage_type="local",
                persist_dir=str(backend_dir / "storage" / "local_index")
            )
        
        # Load existing index
        index = vector_store.load_index()
        
        if index:
            # Create retriever with optimized settings for voice
            rag_retriever = RAGRetriever(
                index=index,
                similarity_top_k=2,  # Keep minimal for fast response
                response_mode="compact"
            )
            print("✅ RAG pipeline initialized successfully!")
        else:
            print("⚠️  No existing index found. Run upload_embeddings.py first.")
            print("   Agent will run without RAG support.")
    
    except Exception as e:
        print(f"⚠️  Error initializing RAG pipeline: {e}")
        print("   Agent will run without RAG support.")
    
    # Create assistant instance
    assistant = Assistant(rag_retriever=rag_retriever)
    
    # Create agent session
    session = AgentSession(
        stt="assemblyai/universal-streaming:en",
        llm="openai/gpt-4.1-mini",
        tts="cartesia/sonic-3:9626c31c-bec5-4cca-baa8-f8ba9e84c8bc",
        vad=silero.VAD.load(),
    )

    # Set up RAG context injection using session events
    @session.on("user_speech_committed")
    def on_user_speech(msg: agents.llm.ChatMessage):
        """Inject RAG context when user speaks."""
        if assistant.rag_retriever and msg.content:
            context = assistant.get_context(msg.content)
            if context:
                # Add context as a system message
                context_msg = agents.llm.ChatMessage(
                    role="system",
                    content=f"""[HOSPITAL KNOWLEDGE BASE CONTEXT]
{context}
[END OF CONTEXT]

Use the above context to answer the user's question accurately."""
                )
                session.chat_ctx.messages.append(context_msg)

    await session.start(
        room=ctx.room,
        agent=assistant,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(), 
        ),
    )

    await session.generate_reply(
        instructions="Greet the user warmly as a hospital receptionist and offer your assistance."
    )



if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))