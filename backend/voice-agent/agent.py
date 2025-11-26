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
    patient_name: str,
    patient_age: int,
    patient_gender: str,
    department: str,
    doctor: str,
    date: str,
    time: str
) -> str:
    """Book a medical appointment for the user.
    
    Use this when the user wants to schedule an appointment, book a consultation, or see a doctor.
    ONLY call this ONCE after collecting all patient information and user confirms the time slot.
    
    Args:
        patient_name: Patient's full name
        patient_age: Patient's age in years (must be a number)
        patient_gender: Patient's gender (Male, Female, or Other)
        department: The medical department (e.g., Cardiology, Pediatrics)
        doctor: The doctor's FULL name exactly as shown in available slots (e.g., Dr. Harsh Sharma)
        date: Appointment date in YYYY-MM-DD format
        time: Appointment time in HH:MM format (24-hour)
    """
    # Normalize doctor name - handle partial names like "Harsh Sharma"
    if not doctor.startswith("Dr. "):
        doctor = f"Dr. {doctor}"
    
    result = appointment_service.book_appointment(
        user_id="demo_user",
        patient_name=patient_name,
        patient_age=patient_age,
        patient_gender=patient_gender,
        department=department,
        doctor=doctor,
        date=date,
        time=time
    )
    
    if result["success"]:
        # Clear success confirmation
        return f"Perfect! Appointment confirmed for {patient_name} with {doctor} in {department} on {date} at {time}."
    else:
        return f"I'm sorry, I couldn't book that. {result['error']}. Would you like to try again?"


@llm.function_tool
async def check_available_slots(
    department: str,
    doctor: str,
    date: str
) -> str:
    """Check available appointment time slots.
    
    Use this ONLY ONCE when user asks for available times.
    Then WAIT for user to pick a time before calling book_appointment.
    DO NOT call this multiple times or try multiple doctors automatically.
    
    Args:
        department: The medical department
        doctor: The doctor's FULL name (e.g., Dr. Harsh Sharma)
        date: Date to check in YYYY-MM-DD format
    """
    # Normalize doctor name
    if not doctor.startswith("Dr. "):
        doctor = f"Dr. {doctor}"
    
    slots = appointment_service.get_available_slots(date, department, doctor)
    
    if slots:
        # Format nicely for voice - show first 3 options
        if len(slots) > 3:
            slot_list = ", ".join(slots[:3])
            return f"I have several openings on {date}. The earliest are {slot_list}. Which time works best for you?"
        else:
            slot_list = ", ".join(slots)
            return f"Available times on {date}: {slot_list}. Which would you prefer?"
    else:
        return f"I'm sorry, {doctor} has no availability on {date}. Would you like to try a different date?"


async def entrypoint(ctx: JobContext):
    """Voice agent entrypoint - connects to room and starts the agent."""
    
    # Verify RAG is loaded before starting
    if not rag_service.is_available():
        print("⚠️  WARNING: RAG service not available! Voice agent will have limited functionality.")
    else:
        print("✅ RAG service is ready for voice agent")
    
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    # Voice-specific instruction addition to system prompt (fresh timestamp each session)
    base_prompt = get_system_prompt()
    voice_instructions = f"""{base_prompt}

### CRITICAL TOOL USAGE RULES - PREVENT INFINITE LOOPS!
* **BOOKING PRIORITY:** If user asks to "book", "schedule", or "make appointment" - ALWAYS use booking tools, even if they mention symptoms
* **ALWAYS use search_hospital_knowledge() for:**
  - Hospital departments, doctors, services, facilities
  - Operating hours, visiting hours, cafeteria hours  
  - Policies, procedures, locations, contact information
  - Finding which doctor to see for specific conditions

### APPOINTMENT BOOKING FLOW (FOLLOW EXACTLY!):
1. **User wants appointment** -> Ask for PATIENT INFO first: "May I have the patient's name, age, and gender?"
2. **Got patient info** -> Ask: "Which department?" or suggest based on symptoms
3. **User picks department** -> Call search_hospital_knowledge("[department] doctors") to get doctor name
4. **You have doctor name** -> Ask: "What date works for you?"
5. **User provides date** -> Call check_available_slots() ONCE. Show 2-3 options. WAIT for user response.
6. **User picks time** -> Call book_appointment() with ALL info (patient_name, patient_age, patient_gender, department, doctor, date, time). Confirm booking. STOP.

### PATIENT INFO COLLECTION (REQUIRED BEFORE BOOKING!):
* You MUST collect: patient name, age (number), and gender (Male/Female/Other)
* Ask naturally: "Before I book, may I have the patient's name?" then "And their age and gender?"
* If booking for self: "Is this appointment for yourself? May I have your name, age, and gender?"

### CRITICAL: STOP AFTER BOOKING!
* After successful book_appointment(), say confirmation and ASK if they need anything else
* DO NOT automatically check more slots or try other doctors
* DO NOT call tools in loops - ONE tool call per user response
* If booking fails, explain why and ask user what they'd like to do

### EMERGENCY OVERRIDE:
* **DO NOT redirect to emergency** unless user explicitly says "emergency", "urgent now", or "critical help"
* **Symptoms + Booking = Book appointment** (e.g., "chest pain appointment" = Cardiology booking)

### VOICE OUTPUT CONSTRAINTS (CRITICAL FOR TTS)
* **Length:** Maximum 2-3 sentences per response
* **Style:** Natural, conversational spoken English
* **Formatting:** NO lists, NO markdown, NO asterisks, NO special characters, NO bullet points
* **Readability:** This text goes to Text-to-Speech - write for listening, not reading
* **Numbers:** Spell out numbers (e.g., "two PM" not "14:00")
* **Pronunciation:** Use phonetically clear language

### EXAMPLES
❌ WRONG: "You have chest pain, go to emergency immediately"
✅ RIGHT: "I can help you book a Cardiology appointment for your chest pain. Which doctor would you prefer?"

❌ WRONG: "Let me check if we have that information" [without calling tool]
✅ RIGHT: [Calls search_hospital_knowledge then provides answer]
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