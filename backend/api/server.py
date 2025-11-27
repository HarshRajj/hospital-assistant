"""FastAPI server for hospital voice assistant."""
import sys
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel

backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from services.token_service import token_service
from services.chat_service import chat_service
from services.appointment_service import appointment_service
import jwt


# Inline auth - decode Clerk JWT to get user_id
async def verify_token(authorization: Optional[str] = Header(None)) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Authentication required")
    
    token = authorization.replace("Bearer ", "")
    
    # For demo/test tokens, use demo_user
    if token == "test" or token == "demo":
        return {"authenticated": True, "user_id": "demo_user"}
    
    # Decode Clerk JWT to get user_id
    try:
        decoded = jwt.decode(token, options={"verify_signature": False})
        user_id = decoded.get("sub")
        
        if not user_id:
            raise HTTPException(401, "Invalid token: no user ID")
        
        return {"authenticated": True, "user_id": user_id}
    except Exception as e:
        raise HTTPException(401, f"Invalid token: {str(e)}")


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
    patient_name: str
    patient_age: int
    patient_gender: str  # Male, Female, Other
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
async def connect(_: dict = Depends(verify_token)):
    """Generate LiveKit token (auth required)."""
    if not token_service.is_configured():
        raise HTTPException(500, "LiveKit not configured")
    return token_service.generate_connection()


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, user: dict = Depends(verify_token)):
    """Chat with RAG support (auth required)."""
    try:
        history = [{"role": m.role, "content": m.content} for m in request.conversation_history] if request.conversation_history else None
        user_id = user.get("user_id", "demo_user")
        return ChatResponse(**await chat_service.chat(request.message, history, user_id))
    except Exception as e:
        raise HTTPException(500, f"Chat error: {e}")


@app.get("/appointments/departments")
async def get_departments():
    return appointment_service.get_departments()


@app.get("/appointments/slots")
async def get_available_slots(date: str, department: str, doctor: str):
    return {"date": date, "department": department, "doctor": doctor, 
            "available_slots": appointment_service.get_available_slots(date, department, doctor)}


@app.get("/appointments/my")
async def get_my_appointments(user: dict = Depends(verify_token)):
    """Get user's appointments (auth required)."""
    user_id = user.get("user_id", "demo_user")
    return {"appointments": appointment_service.get_user_appointments(user_id)}


@app.post("/appointments/book")
async def book_appointment(request: BookAppointmentRequest, user: dict = Depends(verify_token)):
    """Book appointment (auth required)."""
    user_id = user.get("user_id", "demo_user")
    result = appointment_service.book_appointment(
        user_id, request.patient_name, request.patient_age, request.patient_gender,
        request.department, request.doctor, request.date, request.time
    )
    if not result["success"]:
        raise HTTPException(400, result["error"])
    return result


@app.delete("/appointments/{appointment_id}")
async def cancel_appointment(appointment_id: str, user: dict = Depends(verify_token)):
    """Cancel appointment (auth required)."""
    user_id = user.get("user_id", "demo_user")
    result = appointment_service.cancel_appointment(appointment_id, user_id)
    if not result["success"]:
        raise HTTPException(400, result["error"])
    return result


if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Hospital Voice Assistant API...")
    print(f"📍 API will be available at: http://{settings.API_HOST}:{settings.API_PORT}")
    print(f"🔗 LiveKit URL: {settings.LIVEKIT_URL}")
    uvicorn.run(app, host=settings.API_HOST, port=settings.API_PORT)
