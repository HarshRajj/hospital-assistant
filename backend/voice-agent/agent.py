"""Voice agent with RAG-powered hospital knowledge retrieval."""
import sys
from pathlib import Path

# Add backend directory to path for imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from livekit.agents import Agent, AgentSession, AutoSubscribe, JobContext, WorkerOptions, cli, llm
from livekit.plugins import silero, groq

from services.rag_service import rag_service
from config import settings


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
                    * *Response:* "Yes, the cafeteria is open 24/7 on the first floor near the main lobby."
                """
        ),
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