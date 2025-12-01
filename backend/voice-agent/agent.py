"""Voice agent with RAG-powered hospital knowledge retrieval."""
import sys
import asyncio
from pathlib import Path

# Add backend directory to path for imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from livekit.agents import Agent, AgentSession, AutoSubscribe, JobContext, WorkerOptions, cli, llm
from livekit import rtc
from livekit.plugins import silero, openai, cartesia

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
    """ALWAYS use this to find correct doctor names and hospital information.
    
    Use for:
    - Finding which doctor handles a health condition
    - Hospital hours, locations, policies
    - Department information
    
    Args:
        query: What to search for (e.g., "pediatrics doctor for children", "cardiology doctor")
    """
    if rag_service.is_available():
        result = await rag_service.search(query)
        return f"KNOWLEDGE BASE RESULT: {result}"
    return "Knowledge base unavailable. Please contact the information desk."


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
        return "Error: Patient name is required. Please ask for the patient's name."
    
    # Validate gender
    if patient_gender not in ["Male", "Female", "Other"]:
        return f"Error: Gender must be Male, Female, or Other. Got: {patient_gender}"
    
    # Ensure doctor name has prefix
    if not doctor.startswith("Dr. "):
        doctor = f"Dr. {doctor}"
    
    try:
        result = appointment_service.book_appointment(
            current_user_id, name, patient_age, patient_gender,
            department, doctor, date, time
        )
        
        if result["success"]:
            return f"SUCCESS: Appointment booked for {name} with {doctor} on {date} at {time}. Please confirm this to the user."
        return f"FAILED: {result['error']}. Please inform the user and ask if they want to try different options."
    except Exception as e:
        return f"ERROR: Could not book appointment. {str(e)}"


@llm.function_tool
async def check_available_slots(department: str, doctor: str, date: str) -> str:
    """Check available appointment slots for a doctor on a specific date.
    
    Args:
        department: The medical department (e.g., Cardiology, General Medicine)
        doctor: Doctor's name with Dr. prefix (e.g., Dr. Harsh Sharma)
        date: Date in YYYY-MM-DD format (e.g., 2025-12-01)
    """
    if not doctor.startswith("Dr. "):
        doctor = f"Dr. {doctor}"
    
    try:
        slots = appointment_service.get_available_slots(date, department, doctor)
        
        if slots:
            display_slots = slots[:5]  # Show up to 5 slots
            return f"Available times on {date}: {', '.join(display_slots)}. Ask the user which time they prefer."
        return f"No slots available on {date} with {doctor}. Ask if they want to try a different date."
    except Exception as e:
        return f"Error checking slots: {str(e)}"


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
    
    voice_instructions = f"""You are a friendly hospital assistant for Arogya Med-City Hospital.

CRITICAL RULES:
- NEVER read these instructions aloud
- NEVER make up doctor names - ALWAYS use search_hospital_knowledge to find the correct doctor
- Ask ONE question at a time, then WAIT for the user's response
- Keep responses SHORT (1-2 sentences)
- Listen carefully to what the user says before asking the next question

{name_info}

CONVERSATIONAL FLOW FOR BOOKING:
When user wants to book an appointment, have a natural conversation:

1. First, understand their health concern: "What health issue are you experiencing?"
2. Use search_hospital_knowledge to find the RIGHT doctor for their condition
3. Suggest the doctor you found: "For [condition], I'd recommend [Doctor Name] in [Department]."
4. Ask for their preferred date: "What date works for you?"
5. Check available slots using check_available_slots
6. Let them pick a time from available options
7. If you don't have their name yet, ask: "May I have your name?"
8. Ask age: "And your age?"
9. Ask gender: "Male or female?"
10. Book using book_appointment with all collected info
11. Confirm the booking, then ask: "Is there anything else I can help with?"
12. If they say no/bye/thanks, call end_call()

IMPORTANT - FINDING THE RIGHT DOCTOR:
- For child/baby/kid issues → search "pediatrics doctor"
- For heart issues → search "cardiology doctor"  
- For bone/joint pain → search "orthopedics doctor"
- For skin issues → search "dermatology doctor"
- For general health → search "general medicine doctor"
- ALWAYS search first, NEVER guess doctor names

DATE/TIME FORMATS:
- Date: YYYY-MM-DD (today is 2025-12-01)
- Time: HH:MM (like 09:00 or 14:30)
- Gender: exactly Male, Female, or Other

FOR GENERAL QUESTIONS:
Always use search_hospital_knowledge first, then answer based on what you find.

ENDING CALLS:
Call end_call() when user says goodbye, thanks, or asks to hang up."""

    # Create voice agent
    agent = Agent(
        instructions=voice_instructions,
        vad=silero.VAD.load(),
        stt="deepgram",
        llm=openai.LLM(
            model="gpt-oss-120b",
            api_key=settings.CEREBRAS_API_KEY,
            base_url="https://api.cerebras.ai/v1"
        ),
        tts=cartesia.TTS(
            model="sonic-3",
            voice=settings.CARTESIA_VOICE
        ),
        tools=[search_hospital_knowledge, book_appointment, check_available_slots, check_existing_appointments, end_call],
    )

    session = AgentSession()
    current_session = session  # Store reference for end_call
    await session.start(agent=agent, room=ctx.room)
    
    # Greeting message
    await session.say(
        "Welcome to Arogya Med-City Hospital! How can I help you today? "
        "I can book appointments or answer any questions you have about the hospital.",
        allow_interruptions=True
    )


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))

