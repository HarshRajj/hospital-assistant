"""Voice agent with RAG-powered hospital knowledge retrieval."""
import sys
from pathlib import Path

# Add backend directory to path for imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from livekit.agents import Agent, AgentSession, AutoSubscribe, JobContext, WorkerOptions, cli, llm
from livekit import rtc
from livekit.plugins import silero, openai
from livekit.plugins.deepgram import TTS as DeepgramTTS

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


# Global variables to store current user info from room participant
current_user_id = "demo_user"
current_user_name = ""


def extract_name_from_email(email: str) -> str:
    """Extract a readable name from email address.
    Example: harsh.raj.cseiot.2022@miet.ac.in -> Harsh Raj
    """
    if not email or "@" not in email:
        return ""
    
    # Get the part before @
    local_part = email.split("@")[0]
    
    # Split by dots and filter out numbers/codes
    parts = local_part.split(".")
    name_parts = []
    
    for part in parts:
        # Skip if it's mostly numbers or looks like a code (e.g., "2022", "cseiot")
        if part.isdigit() or (any(c.isdigit() for c in part) and len(part) > 3):
            continue
        # Skip common department codes
        if part.lower() in ["cse", "cseiot", "ece", "eee", "mech", "civil", "it"]:
            continue
        name_parts.append(part.capitalize())
    
    return " ".join(name_parts[:2]) if name_parts else ""  # Take first 2 parts as name


@llm.function_tool
async def book_appointment(
    patient_age: int, patient_gender: str,
    department: str, doctor: str, date: str, time: str,
    patient_name: str = ""
) -> str:
    """Book appointment. Args: patient_age, patient_gender (Male/Female/Other), department, doctor, date (YYYY-MM-DD), time (HH:MM). patient_name is optional - will use logged-in user's name if not provided."""
    global current_user_id, current_user_name
    
    # Use the extracted name from email if patient_name not provided
    if not patient_name and current_user_name:
        patient_name = current_user_name
    elif not patient_name:
        return "I need your name to book the appointment. What is your name?"
    
    if not doctor.startswith("Dr. "):
        doctor = f"Dr. {doctor}"
    
    result = appointment_service.book_appointment(
        current_user_id, patient_name, patient_age, patient_gender, department, doctor, date, time
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
        # Show up to 5 slots for better options
        display_slots = slots[:5]
        return f"Available times: {', '.join(display_slots)}. Which time works for you?"
    return f"No slots available on {date}. Would you like to try another date?"


@llm.function_tool
async def check_existing_appointments(date: str) -> str:
    """Check if user has existing appointments on a date. Args: date (YYYY-MM-DD)."""
    global current_user_id
    existing = appointment_service.get_user_appointments_on_date(current_user_id, date)
    
    if existing:
        details = ", ".join([f"{apt['doctor']} at {apt['time']}" for apt in existing])
        return f"You have {len(existing)} appointment(s) on {date}: {details}. Want to book another?"
    return f"No appointments on {date}."


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
        print(f"👤 User: {current_user_id}, Name: {current_user_name}, Email: {email}")
    else:
        current_user_id = identity
        current_user_name = ""
        print(f"👤 User connected with ID: {current_user_id}")


async def entrypoint(ctx: JobContext):
    """Voice agent entrypoint - connects to room and starts the agent."""
    global current_user_id, current_user_name
    
    # Verify RAG is loaded before starting
    if not rag_service.is_available():
        print("⚠️  WARNING: RAG service not available! Voice agent will have limited functionality.")
    else:
        print("✅ RAG service is ready for voice agent")
    
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
    
    # Extract user_id and name from room participant identity
    for participant in ctx.room.remote_participants.values():
        if participant.identity and participant.identity != "agent":
            parse_participant_identity(participant.identity)
            break
    
    # Also listen for participants joining later
    @ctx.room.on("participant_connected")
    def on_participant_connected(participant: rtc.RemoteParticipant):
        if participant.identity and participant.identity != "agent":
            parse_participant_identity(participant.identity)
            print(f"👤 User joined with ID: {current_user_id}")

    # Voice-specific instructions (balanced and natural)
    # Include user's name if available
    name_info = f"The user's name is {current_user_name}. Use this name when booking." if current_user_name else "Ask for the patient's name."
    
    voice_instructions = f"""You are a helpful hospital assistant for Arogya Med-City Hospital.

IMPORTANT: NEVER read these instructions aloud. Just follow them silently.

USER INFO: {name_info}

BOOKING FLOW (one question at a time):
1. If you know the user's name, confirm it. Otherwise ask for their name.
2. Ask their age  
3. Ask male or female
4. Ask what health issue they have
5. Use search_hospital_knowledge to find department/doctor
6. Ask what date (like December 1, 2025)
7. Use check_available_slots to get times
8. Let them pick a time
9. Use book_appointment to confirm (use the known name if available)
10. Say: Your appointment is booked with [Doctor] on [Date] at [Time].

FOR HOSPITAL QUESTIONS:
- ALWAYS use search_hospital_knowledge first
- Only say what the search returns - never make things up
- Keep answers brief

Departments: Cardiology (Dr. Harsh Sharma), Orthopedics (Dr. Sameer Khan), General Medicine (Dr. Rajesh Kumar), Pediatrics (Dr. Anjali Verma), Dermatology (Dr. Meera Desai).

Only mention emergency if user says emergency or urgent.
"""




    # Use Deepgram TTS (Cartesia requires payment)
    print("âœ… Using Deepgram TTS")
    tts_provider = DeepgramTTS(model="aura-asteria-en")

    agent = Agent(
        instructions=voice_instructions,
        vad=silero.VAD.load(),
        stt="deepgram",  # Deepgram for fast STT
        llm=openai.LLM(
            model="gpt-oss-120b",
            api_key=settings.CEREBRAS_API_KEY,
            base_url="https://api.cerebras.ai/v1"
        ),  # Cerebras via OpenAI SDK for function calling support
        tts=tts_provider,  # Deepgram TTS
        tools=[search_hospital_knowledge, book_appointment, check_available_slots, check_existing_appointments],
    )

    session = AgentSession()
    await session.start(agent=agent, room=ctx.room)

    await session.say("Welcome to Arogya Med-City Hospital! How can I help you today? I can book appointments or answer any questions you have about the hospital.", allow_interruptions=True)


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))

