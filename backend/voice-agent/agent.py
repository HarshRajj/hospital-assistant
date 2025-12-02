"""Voice agent with RAG-powered hospital knowledge retrieval."""
import sys
import asyncio
from pathlib import Path

# Add backend directory to path for imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from livekit.agents import Agent, AgentSession, AutoSubscribe, JobContext, WorkerOptions, cli, llm
from livekit import rtc
from livekit.plugins import silero, openai, deepgram

from services.rag_service import rag_service
from services.appointment_service import appointment_service
from config import settings


# User session info (extracted from LiveKit participant identity)
current_user_id = "demo_user"
current_user_name = ""
current_session = None  # Store session reference for disconnect


def extract_name_from_email(email: str) -> str:
    """Extract a readable name from email address.
    
    Example: harsh.raj.cseiot.2022@miet.ac.in -> Harsh Raj
    """
    if not email or "@" not in email:
        return ""
    
    # Get the part before @
    local_part = email.split("@")[0]
    parts = local_part.split(".")
    
    # Filter out numbers and department codes
    name_parts = []
    skip_codes = ["cse", "cseiot", "ece", "eee", "mech", "civil", "it"]
    
    for part in parts:
        # Skip if it's mostly numbers or a department code
        if part.isdigit():
            continue
        if any(c.isdigit() for c in part) and len(part) > 3:
            continue
        if part.lower() in skip_codes:
            continue
        name_parts.append(part.capitalize())
    
    # Take first 2 parts as name
    return " ".join(name_parts[:2]) if name_parts else ""


def parse_participant_identity(identity: str):
    """Parse user_id and email from participant identity.
    
    Format: user_id|email or just user_id
    """
    global current_user_id, current_user_name
    
    if "|" in identity:
        parts = identity.split("|", 1)
        current_user_id = parts[0]
        email = parts[1] if len(parts) > 1 else ""
        current_user_name = extract_name_from_email(email)
    else:
        current_user_id = identity
        current_user_name = ""


# ========== TOOL DEFINITIONS ==========

@llm.function_tool
async def search_hospital_knowledge(query: str) -> str:
    """Search our hospital database. You MUST call this before mentioning any doctor name - you don't know doctors from memory!
    
    Args:
        query: What to search for, e.g. "pediatrics doctor", "cardiology doctor", "visiting hours"
    """
    if rag_service.is_available():
        result = await rag_service.search(query)
        return f"DATABASE RESULT: {result}"
    return "I'm having trouble accessing the system. Please call us at (555) 100-2000."


@llm.function_tool
async def book_appointment(
    patient_name: str,
    patient_age: int,
    patient_gender: str,
    department: str,
    doctor: str,
    date: str,
    time: str
) -> str:
    """Book an appointment. ALL parameters are required.
    
    Args:
        patient_name: Patient's full name (required)
        patient_age: Patient's age in years (required)
        patient_gender: Must be exactly "Male", "Female", or "Other" (required)
        department: Medical department name (required)
        doctor: Doctor's full name with Dr. prefix (required)
        date: Date in YYYY-MM-DD format (required)
        time: Time in HH:MM 24-hour format (required)
    """
    # Use extracted name if not provided
    name = patient_name.strip() if patient_name else current_user_name
    if not name:
        return "Need patient name"
    
    # Validate gender
    if patient_gender not in ["Male", "Female", "Other"]:
        return f"Gender must be Male, Female, or Other"
    
    # Ensure doctor name has prefix
    if not doctor.startswith("Dr. "):
        doctor = f"Dr. {doctor}"
    
    try:
        result = appointment_service.book_appointment(
            current_user_id, name, patient_age, patient_gender,
            department, doctor, date, time
        )
        
        if result["success"]:
            return f"Booked! {name} with {doctor} on {date} at {time}."
        return f"Failed: {result['error']}"
    except Exception as e:
        return f"Error: {str(e)}"


@llm.function_tool
async def check_available_slots(department: str, doctor: str, date: str) -> str:
    """Check available appointment slots for a doctor on a date.
    
    Args:
        department: Medical department (e.g., Cardiology, Pediatrics)
        doctor: Doctor's name (e.g., Dr. Harsh Sharma)
        date: Date in YYYY-MM-DD format
    """
    if not doctor.startswith("Dr. "):
        doctor = f"Dr. {doctor}"
    
    try:
        slots = appointment_service.get_available_slots(date, department, doctor)
        if slots:
            # Return only first 3 slots to keep it simple
            return f"{', '.join(slots[:5])}"
        return f"No slots available on {date}."
    except Exception as e:
        return f"Error: {str(e)}"


@llm.function_tool
async def check_existing_appointments(date: str) -> str:
    """Check if user has existing appointments on a date."""
    existing = appointment_service.get_user_appointments_on_date(current_user_id, date)
    
    if existing:
        details = ", ".join([f"{apt['doctor']} at {apt['time']}" for apt in existing])
        return f"You have {len(existing)} appointment(s) on {date}: {details}"
    return f"No appointments on {date}."


@llm.function_tool
async def end_call() -> str:
    """End the voice call. Use this when:
    - User says goodbye, bye, thank you, or wants to end the call
    - After successfully booking an appointment and confirming with user
    - User explicitly asks to disconnect or hang up
    """
    global current_session
    if current_session:
        # Schedule disconnect after a short delay to let the goodbye message play
        asyncio.create_task(_delayed_disconnect())
    return "Ending the call now. Goodbye!"


async def _delayed_disconnect():
    """Disconnect after a short delay."""
    global current_session
    await asyncio.sleep(3)  # Wait for goodbye message to finish
    if current_session:
        await current_session.aclose()


# ========== VOICE AGENT ENTRYPOINT ==========

async def entrypoint(ctx: JobContext):
    """Voice agent entrypoint - connects to room and starts the agent."""
    global current_user_id, current_user_name, current_session
    
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
    
    # Extract user_id and name from room participant identity
    for participant in ctx.room.remote_participants.values():
        if participant.identity and participant.identity != "agent":
            parse_participant_identity(participant.identity)
            break
    
    # Listen for participants joining later
    @ctx.room.on("participant_connected")
    def on_participant_connected(participant: rtc.RemoteParticipant):
        if participant.identity and participant.identity != "agent":
            parse_participant_identity(participant.identity)
    
    # Build voice instructions
    name_info = f"User's name: {current_user_name}." if current_user_name else ""
    
    voice_instructions = f"""You are Maya, a hospital receptionist talking to a patient on the phone. {name_info}

Talk naturally like a real person. Don't narrate what you're thinking or planning to do. Just have a normal conversation.

To book an appointment:
1. "What brings you in today?"
2. Search for doctor with their symptom
3. "Great, Dr. [Name] can help. What date works for you?"
4. Check available slots
5. "I have these times available: [times]. Which one?"
6. "Your name, age, and gender please?"
7. Book it
8. "You're all set!"

Be brief. One question at a time. Use the tools to find information - don't make anything up.
Today is {{current_date}}.
"""

    # Create voice agent
    agent = Agent(
        instructions=voice_instructions,
        vad=silero.VAD.load(),
        stt="deepgram",
        llm=openai.LLM(
            model="gpt-oss-120b",
            api_key=settings.CEREBRAS_API_KEY,
            base_url="https://api.cerebras.ai/v1"
            # model="gpt-4o-mini",  # Fast, cheap, high rate limits
            # api_key=settings.OPENAI_API_KEY
        ),
        tts=deepgram.TTS(
            model="aura-asteria-en"  # Natural female voice
        ),
        tools=[search_hospital_knowledge, book_appointment, check_available_slots, check_existing_appointments, end_call],
    )

    session = AgentSession()
    current_session = session  # Store reference for end_call
    await session.start(agent=agent, room=ctx.room)
    
    # Greeting message
    greeting = f"Hi{' ' + current_user_name if current_user_name else ''}! This is Maya from Arogya Med-City Hospital. How can I help you today?"
    await session.say(greeting, allow_interruptions=True)


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))

