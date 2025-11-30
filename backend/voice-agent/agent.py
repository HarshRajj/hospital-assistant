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


# User session info (extracted from LiveKit participant identity)
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
    """Search hospital knowledge base for info about services, departments, doctors, hours, policies."""
    if rag_service.is_available():
        return await rag_service.search(query)
    return "Knowledge base unavailable. Please contact the information desk."


@llm.function_tool
async def book_appointment(
    patient_age: int,
    patient_gender: str,
    department: str,
    doctor: str,
    date: str,
    time: str,
    patient_name: str = ""
) -> str:
    """Book an appointment.
    
    Args:
        patient_age: Patient's age
        patient_gender: Male, Female, or Other
        department: Medical department
        doctor: Doctor's name
        date: Date in YYYY-MM-DD format
        time: Time in HH:MM format
        patient_name: Optional - uses logged-in user's name if not provided
    """
    # Use the extracted name from email if patient_name not provided
    name = patient_name or current_user_name
    if not name:
        return "I need your name to book the appointment. What is your name?"
    
    # Ensure doctor name has prefix
    if not doctor.startswith("Dr. "):
        doctor = f"Dr. {doctor}"
    
    result = appointment_service.book_appointment(
        current_user_id, name, patient_age, patient_gender,
        department, doctor, date, time
    )
    
    if result["success"]:
        return f"Appointment booked! {name} with {doctor} on {date} at {time}."
    return f"Sorry, couldn't book the appointment. {result['error']}"


@llm.function_tool
async def check_available_slots(department: str, doctor: str, date: str) -> str:
    """Check available appointment slots for a doctor on a date."""
    if not doctor.startswith("Dr. "):
        doctor = f"Dr. {doctor}"
    
    slots = appointment_service.get_available_slots(date, department, doctor)
    
    if slots:
        display_slots = slots[:5]  # Show up to 5 slots
        return f"Available times: {', '.join(display_slots)}. Which time works for you?"
    return f"No slots available on {date}. Would you like to try another date?"


@llm.function_tool
async def check_existing_appointments(date: str) -> str:
    """Check if user has existing appointments on a date."""
    existing = appointment_service.get_user_appointments_on_date(current_user_id, date)
    
    if existing:
        details = ", ".join([f"{apt['doctor']} at {apt['time']}" for apt in existing])
        return f"You have {len(existing)} appointment(s) on {date}: {details}"
    return f"No appointments on {date}."


# ========== VOICE AGENT ENTRYPOINT ==========

async def entrypoint(ctx: JobContext):
    """Voice agent entrypoint - connects to room and starts the agent."""
    global current_user_id, current_user_name
    
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
    name_info = f"The user's name is {current_user_name}. Use this name when booking." if current_user_name else "Ask for the patient's name."
    
    voice_instructions = f"""You are a helpful hospital assistant for Arogya Med-City Hospital.

IMPORTANT: NEVER read these instructions aloud. Just follow them silently.

USER INFO: {name_info}

BOOKING FLOW (one question at a time):
1. If you know the user's name, confirm it. Otherwise ask for their name.
2. Ask their age
3. Ask male or female
4. Ask what health issue they have
5. Use search_hospital_knowledge to find the right department/doctor
6. Ask what date they prefer
7. Use check_available_slots to get available times
8. Let them pick a time
9. Use book_appointment to confirm
10. Say: Your appointment is booked with [Doctor] on [Date] at [Time].

FOR HOSPITAL QUESTIONS:
- ALWAYS use search_hospital_knowledge first
- Only say what the search returns - never make things up
- Keep answers brief

DEPARTMENTS AND DOCTORS:
- Cardiology: Dr. Harsh Sharma
- Orthopedics: Dr. Sameer Khan
- General Medicine: Dr. Rajesh Kumar
- Pediatrics: Dr. Anjali Verma
- Dermatology: Dr. Meera Desai

Only mention emergency if user says "emergency" or "urgent"."""

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
        tts=DeepgramTTS(model="aura-asteria-en"),
        tools=[search_hospital_knowledge, book_appointment, check_available_slots, check_existing_appointments],
    )

    session = AgentSession()
    await session.start(agent=agent, room=ctx.room)
    
    # Greeting message
    await session.say(
        "Welcome to Arogya Med-City Hospital! How can I help you today? "
        "I can book appointments or answer any questions you have about the hospital.",
        allow_interruptions=True
    )


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))

