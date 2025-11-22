"""Voice agent with RAG-powered hospital knowledge retrieval."""
import sys
from pathlib import Path

# Add backend directory to path for imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from livekit.agents import Agent, AgentSession, AutoSubscribe, JobContext, WorkerOptions, cli, llm
from livekit.plugins import silero, groq

from services.rag_service import rag_service
from config import settings, HOSPITAL_ASSISTANT_SYSTEM_PROMPT


@llm.function_tool
async def search_hospital_knowledge(query: str) -> str:
    """Search the hospital's knowledge base for information about services, departments, doctors, hours, policies, and facilities.
    
    Use this function for ANY question about the hospital. Do not answer hospital questions without calling this function.
    
    Args:
        query: The question or topic to search for in the hospital knowledge base.
    """
    return await rag_service.search(query)


async def entrypoint(ctx: JobContext):
    """Voice agent entrypoint - connects to room and starts the agent."""
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    # Voice-specific instruction addition to system prompt
    voice_instructions = f"""{HOSPITAL_ASSISTANT_SYSTEM_PROMPT}

### VOICE OUTPUT CONSTRAINTS (CRITICAL FOR TTS)
* **Length:** Keep responses concise - maximum 2-3 sentences for simple queries
* **Style:** Natural, conversational spoken English. Avoid robotic phrasing
* **Formatting:** NO lists, NO markdown, NO asterisks, NO special characters, NO bullet points
* **Readability:** This text goes directly to a Text-to-Speech engine - write for listening, not reading
* **Numbers:** Spell out numbers (e.g., "twenty-four seven" not "24/7")
* **Pronunciation:** Use phonetically clear language
"""

    agent = Agent(
        instructions=voice_instructions,
        vad=silero.VAD.load(),
        stt="deepgram",  # Deepgram for fast STT
        llm=groq.LLM(
            model="gpt-oss-120b",
            api_key=settings.CEREBRAS_API_KEY,
            base_url="https://api.cerebras.ai/v1"
        ),  # FREE Cerebras (ultra-fast inference)
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