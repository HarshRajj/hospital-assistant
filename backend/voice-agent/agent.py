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
from config import settings, HOSPITAL_ASSISTANT_SYSTEM_PROMPT


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
    department: str,
    doctor: str,
    date: str,
    time: str
) -> str:
    """Book a medical appointment for the user.
    
    Use this when the user wants to schedule an appointment, book a consultation, or see a doctor.
    
    Args:
        department: The medical department (e.g., Cardiology, Pediatrics)
        doctor: The doctor's name (e.g., Dr. Sarah Johnson)
        date: Appointment date in YYYY-MM-DD format
        time: Appointment time in HH:MM format (24-hour)
    """
    result = appointment_service.book_appointment(
        user_id="voice_user",
        user_name="Voice User",
        department=department,
        doctor=doctor,
        date=date,
        time=time
    )
    
    if result["success"]:
        return result["message"]
    else:
        return f"I couldn't book that appointment: {result['error']}"


@llm.function_tool
async def check_available_slots(
    department: str,
    doctor: str,
    date: str
) -> str:
    """Check available appointment time slots.
    
    Use this before booking to show available times to the user.
    
    Args:
        department: The medical department
        doctor: The doctor's name
        date: Date to check in YYYY-MM-DD format
    """
    slots = appointment_service.get_available_slots(date, department, doctor)
    
    if slots:
        # Format nicely for voice
        slot_list = ", ".join(slots[:5])  # Only first 5 to keep voice response short
        return f"Available times for {doctor} in {department} on {date}: {slot_list}"
    else:
        return f"I'm sorry, there are no available slots on {date}. Would you like to try another date?"


async def entrypoint(ctx: JobContext):
    """Voice agent entrypoint - connects to room and starts the agent."""
    
    # Verify RAG is loaded before starting
    if not rag_service.is_available():
        print("⚠️  WARNING: RAG service not available! Voice agent will have limited functionality.")
    else:
        print("✅ RAG service is ready for voice agent")
    
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    # Voice-specific instruction addition to system prompt
    voice_instructions = f"""{HOSPITAL_ASSISTANT_SYSTEM_PROMPT}

### CRITICAL TOOL USAGE RULES
* **ALWAYS use search_hospital_knowledge() for ANY question about:**
  - Hospital departments, doctors, services, facilities
  - Operating hours, visiting hours, cafeteria hours
  - Policies, procedures, locations, contact information
  - Emergency services, parking, amenities
* **NEVER answer hospital questions from memory** - you MUST call the search function
* **If user asks about appointments:** Use check_available_slots() first, then book_appointment()
* **The knowledge base has ALL hospital information** - trust it completely

### VOICE OUTPUT CONSTRAINTS (CRITICAL FOR TTS)
* **Length:** Keep responses concise - maximum 2-3 sentences for simple queries
* **Style:** Natural, conversational spoken English. Avoid robotic phrasing
* **Formatting:** NO lists, NO markdown, NO asterisks, NO special characters, NO bullet points
* **Readability:** This text goes directly to a Text-to-Speech engine - write for listening, not reading
* **Numbers:** Spell out numbers (e.g., "twenty-four seven" not "24/7")
* **Pronunciation:** Use phonetically clear language

### IMPORTANT
If the search_hospital_knowledge function returns information, use it EXACTLY as provided. Do not say "I don't have that information" if the function returned results.
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

    await session.say(
        "Hello! Welcome to Arogya Med-City Hospital. How can I help you today?", 
        allow_interruptions=True
    )


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))