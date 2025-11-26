"""Voice agent with RAG-powered hospital knowledge retrieval."""
import sys
from pathlib import Path

# Add backend directory to path for imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from livekit.agents import Agent, AgentSession, AutoSubscribe, JobContext, WorkerOptions, cli, llm
from livekit.plugins import silero, openai, cartesia

from services.rag_service import rag_service
from services.appointment_service import appointment_service
from config import settings
from config.prompts import get_system_prompt


@llm.function_tool
async def search_hospital_knowledge(query: str) -> str:
    """Search the hospital's knowledge base for information about services, departments, doctors, hours, policies, and facilities.
    
    Use this function for ANY question about the hospital. Do not answer hospital questions without calling this function.
    
    Args:
        query: The question or topic to search for in the hospital knowledge base.
    """
    if rag_service.is_available():
        result = await rag_service.search(query)
        return result
    else:
        return "I apologize, but I cannot access the hospital knowledge base right now. Please contact the information desk at the hospital directly."


@llm.function_tool
async def book_appointment(
    patient_name: str, patient_age: int, patient_gender: str,
    department: str, doctor: str, date: str, time: str
) -> str:
    """Book appointment. Args: patient_name, patient_age, patient_gender (Male/Female/Other), department, doctor, date (YYYY-MM-DD), time (HH:MM)."""
    if not doctor.startswith("Dr. "):
        doctor = f"Dr. {doctor}"
    
    result = appointment_service.book_appointment(
        "demo_user", patient_name, patient_age, patient_gender, department, doctor, date, time
    )
    
    if result["success"]:
        return f"Booked! {patient_name} with {doctor} on {date} at {time}."
    return f"Sorry, couldn't book. {result['error']}."


@llm.function_tool
async def check_available_slots(department: str, doctor: str, date: str) -> str:
    """Check available slots. Args: department, doctor, date (YYYY-MM-DD)."""
    if not doctor.startswith("Dr. "):
        doctor = f"Dr. {doctor}"
    
    slots = appointment_service.get_available_slots(date, department, doctor)
    
    if slots:
        return f"Available: {', '.join(slots[:3])}. Which time?"
    return f"No slots on {date}. Try another date?"


async def entrypoint(ctx: JobContext):
    """Voice agent entrypoint - connects to room and starts the agent."""
    
    # Verify RAG is loaded before starting
    if not rag_service.is_available():
        print("⚠️  WARNING: RAG service not available! Voice agent will have limited functionality.")
    else:
        print("✅ RAG service is ready for voice agent")
    
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    # Voice-specific instructions (concise for shorter responses)
    base_prompt = get_system_prompt()
    voice_instructions = f"""{base_prompt}

KEEP RESPONSES VERY SHORT - ONE SENTENCE WHEN POSSIBLE.

For bookings: Get name, age, gender first. Then department, date, time. Confirm briefly.
For questions: Use search_hospital_knowledge. Give brief answer.
Only suggest emergency if they say "emergency" or "urgent help now".
"""

    agent = Agent(
        instructions=voice_instructions,
        vad=silero.VAD.load(),
        stt="deepgram",  # Deepgram for fast STT
        llm=openai.LLM(
            model="gpt-oss-120b",
            api_key=settings.CEREBRAS_API_KEY,
            base_url="https://api.cerebras.ai/v1"
        ),  # Cerebras via OpenAI SDK for function calling support
        tts=cartesia.TTS(voice="6ccbfb76-1fc6-48f7-b71d-91ac6298247b"),  # Female voice
        tools=[search_hospital_knowledge, book_appointment, check_available_slots],
    )

    session = AgentSession()
    await session.start(agent=agent, room=ctx.room)

    await session.say("Hello! How can I help you?", allow_interruptions=True)


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))