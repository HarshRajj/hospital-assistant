"""FastAPI server for hospital voice assistant."""
import sys
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from services.token_service import token_service
from services.chat_service import chat_service
from services.auth_service import auth_service
from services.appointment_service import appointment_service


# Request/Response models
class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    conversation_history: Optional[List[ChatMessage]] = None


class ChatResponse(BaseModel):
    response: str
    context_used: bool
    model: str


class BookAppointmentRequest(BaseModel):
    department: str
    doctor: str
    date: str  # YYYY-MM-DD
    time: str  # HH:MM


app = FastAPI(title="Hospital Voice Assistant API")

# CORS configuration - allow Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "message": "Hospital Voice Assistant API is running"}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/connect")
async def connect(user: dict = Depends(auth_service.verify_token)):
    """Generate a LiveKit token for the voice assistant (requires authentication).
    
    This endpoint ensures only authenticated users can access the voice assistant.
    
    Args:
        user: Authenticated user info from Clerk token
    
    Returns:
        Dictionary containing JWT token, LiveKit URL, and room name
        
    Raises:
        HTTPException: If LiveKit credentials are not configured or user not authenticated
    """
    if not token_service.is_configured():
        raise HTTPException(
            status_code=500,
            detail="LiveKit credentials not configured. Check your .env file."
        )
    
    try:
        connection = token_service.generate_connection()
        return connection
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Text-based chat endpoint with RAG support.
    
    This endpoint uses Cerebras LLM with hospital knowledge base for fast responses.
    
    Args:
        request: ChatRequest containing user message and optional conversation history
        
    Returns:
        ChatResponse with assistant's reply, context usage, and model info
        
    Raises:
        HTTPException: If chat service fails
    """
    try:
        # Convert Pydantic models to dicts for chat service
        history = None
        if request.conversation_history:
            history = [{"role": msg.role, "content": msg.content} for msg in request.conversation_history]
        
        result = await chat_service.chat(
            message=request.message,
            conversation_history=history
        )
        
        return ChatResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


@app.get("/appointments/departments")
async def get_departments():
    """Get all available departments and doctors.
    
    Returns:
        Dictionary mapping departments to their doctors
    """
    return appointment_service.get_departments()


@app.get("/appointments/slots")
async def get_available_slots(date: str, department: str, doctor: str):
    """Get available time slots for a specific date, department, and doctor.
    
    Args:
        date: Date in YYYY-MM-DD format
        department: Department name
        doctor: Doctor name
        
    Returns:
        List of available time slots
    """
    slots = appointment_service.get_available_slots(date, department, doctor)
    return {"date": date, "department": department, "doctor": doctor, "available_slots": slots}


@app.get("/appointments/my")
async def get_my_appointments(user: dict = Depends(auth_service.verify_token)):
    """Get all appointments for the authenticated user.
    
    Args:
        user: Authenticated user info from Clerk token
        
    Returns:
        List of user's appointments
    """
    # For demo purposes, use a static user ID
    # In production, extract from JWT token
    user_id = "demo_user"
    appointments = appointment_service.get_user_appointments(user_id)
    return {"appointments": appointments}


@app.post("/appointments/book")
async def book_appointment(
    request: BookAppointmentRequest,
    user: dict = Depends(auth_service.verify_token)
):
    """Book a new appointment (requires authentication).
    
    Args:
        request: Appointment booking details
        user: Authenticated user info from Clerk token
        
    Returns:
        Booking confirmation or error
    """
    # For demo purposes, use static user info
    # In production, extract from JWT token
    user_id = "demo_user"
    user_name = "Demo User"
    
    result = appointment_service.book_appointment(
        user_id=user_id,
        user_name=user_name,
        department=request.department,
        doctor=request.doctor,
        date=request.date,
        time=request.time
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


@app.delete("/appointments/{appointment_id}")
async def cancel_appointment(
    appointment_id: str,
    user: dict = Depends(auth_service.verify_token)
):
    """Cancel an appointment (requires authentication).
    
    Args:
        appointment_id: Appointment ID to cancel
        user: Authenticated user info from Clerk token
        
    Returns:
        Cancellation confirmation or error
    """
    # For demo purposes, use static user ID
    user_id = "demo_user"
    
    result = appointment_service.cancel_appointment(appointment_id, user_id)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Hospital Voice Assistant API...")
    print(f"📍 API will be available at: http://{settings.API_HOST}:{settings.API_PORT}")
    print(f"🔗 LiveKit URL: {settings.LIVEKIT_URL}")
    uvicorn.run(app, host=settings.API_HOST, port=settings.API_PORT)
