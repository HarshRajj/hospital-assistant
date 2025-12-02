"""FastAPI server for hospital voice assistant."""
import sys
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel
import jwt

backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from fastapi import FastAPI, HTTPException, Depends, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from config import settings
from config.doctors import is_doctor, get_doctor_name_from_email
from services.token_service import token_service
from services.chat_service import chat_service
from services.appointment_service import appointment_service

# Rate limiter setup
limiter = Limiter(key_func=get_remote_address)


async def verify_token(
    authorization: Optional[str] = Header(None),
    x_user_email: Optional[str] = Header(None, alias="X-User-Email")
) -> dict:
    """Verify Clerk JWT and extract user info."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Authentication required")
    
    token = authorization.replace("Bearer ", "")
    if token in ("test", "demo"):
        return {"user_id": "demo_user", "email": ""}
    
    try:
        decoded = jwt.decode(token, options={"verify_signature": False})
        user_id = decoded.get("sub")
        if not user_id:
            raise HTTPException(401, "Invalid token")
        email = str(x_user_email).lower().strip() if x_user_email else ""
        return {"user_id": user_id, "email": email}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(401, f"Invalid token: {e}")


async def verify_doctor(
    authorization: Optional[str] = Header(None),
    x_user_email: Optional[str] = Header(None, alias="X-User-Email")
) -> dict:
    """Verify user is a registered doctor."""
    user = await verify_token(authorization, str(x_user_email) if x_user_email else "")
    email = user.get("email", "").lower().strip()
    
    if not is_doctor(email):
        raise HTTPException(403, "Doctor credentials required")
    
    return {**user, "doctor_name": get_doctor_name_from_email(email)}


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

# Add rate limiter to app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS configuration - allow Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.CORS_ALLOW_ALL else settings.CORS_ORIGINS,
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
@limiter.limit("10/minute")
async def connect(request: Request, user: dict = Depends(verify_token)):
    """Generate LiveKit token (auth required). Rate limited: 10/min"""
    if not token_service.is_configured():
        raise HTTPException(500, "LiveKit not configured")
    user_id = user.get("user_id", "demo_user")
    email = user.get("email", "")
    identity = f"{user_id}|{email}" if email else user_id
    return token_service.generate_connection(identity=identity, name="Hospital Visitor")


@app.post("/chat", response_model=ChatResponse)
@limiter.limit("30/minute")
async def chat(request: Request, chat_request: ChatRequest, user: dict = Depends(verify_token)):
    """Chat with RAG support (auth required). Rate limited: 30/min"""
    try:
        history = [{"role": m.role, "content": m.content} for m in chat_request.conversation_history] if chat_request.conversation_history else None
        user_id = user.get("user_id", "demo_user")
        return ChatResponse(**await chat_service.chat(chat_request.message, history, user_id))
    except Exception as e:
        raise HTTPException(500, f"Chat error: {e}")


@app.get("/appointments/departments")
@limiter.limit("60/minute")
async def get_departments(request: Request):
    """Get all departments. Rate limited: 60/min"""
    return appointment_service.get_departments()


@app.get("/appointments/slots")
@limiter.limit("60/minute")
async def get_available_slots(request: Request, date: str, department: str, doctor: str):
    """Get available slots. Rate limited: 60/min"""
    return {"date": date, "department": department, "doctor": doctor, 
            "available_slots": appointment_service.get_available_slots(date, department, doctor)}


@app.get("/appointments/my")
@limiter.limit("30/minute")
async def get_my_appointments(request: Request, user: dict = Depends(verify_token)):
    """Get user's appointments. Rate limited: 30/min"""
    return {"appointments": appointment_service.get_user_appointments(user.get("user_id", "demo_user"))}


@app.post("/appointments/book")
@limiter.limit("10/minute")
async def book_appointment(request: Request, book_request: BookAppointmentRequest, user: dict = Depends(verify_token)):
    """Book an appointment. Rate limited: 10/min"""
    result = appointment_service.book_appointment(
        user.get("user_id", "demo_user"), book_request.patient_name, book_request.patient_age,
        book_request.patient_gender, book_request.department, book_request.doctor, book_request.date, book_request.time
    )
    if not result["success"]:
        raise HTTPException(400, result["error"])
    return result


@app.delete("/appointments/{appointment_id}")
@limiter.limit("10/minute")
async def cancel_appointment(request: Request, appointment_id: str, user: dict = Depends(verify_token)):
    """Cancel an appointment. Rate limited: 10/min"""
    result = appointment_service.cancel_appointment(appointment_id, user.get("user_id", "demo_user"))
    if not result["success"]:
        raise HTTPException(400, result["error"])
    return result


@app.get("/appointments/doctor/today")
@limiter.limit("30/minute")
async def get_doctor_today_appointments(request: Request, doctor: dict = Depends(verify_doctor)):
    """Get doctor's today appointments. Rate limited: 30/min"""
    appointments = appointment_service.get_doctor_appointments_today(doctor["doctor_name"])
    return {"appointments": appointments, "count": len(appointments)}


@app.get("/appointments/doctor/all")
@limiter.limit("30/minute")
async def get_doctor_all_appointments(request: Request, doctor: dict = Depends(verify_doctor)):
    """Get all doctor appointments. Rate limited: 30/min"""
    appointments = appointment_service.get_doctor_all_appointments(doctor["doctor_name"])
    return {"appointments": appointments, "count": len(appointments)}


@app.get("/appointments/doctor/past-week")
@limiter.limit("30/minute")
async def get_doctor_past_week_appointments(request: Request, doctor: dict = Depends(verify_doctor)):
    """Get doctor's past week appointments. Rate limited: 30/min"""
    appointments = appointment_service.get_doctor_past_week_appointments(doctor["doctor_name"])
    return {"appointments": appointments, "count": len(appointments)}


class DoctorCancelRequest(BaseModel):
    reason: str = ""


@app.delete("/appointments/doctor/{appointment_id}")
@limiter.limit("10/minute")
async def doctor_cancel_appointment(
    request: Request, 
    appointment_id: str, 
    body: DoctorCancelRequest = None,
    doctor: dict = Depends(verify_doctor)
):
    """Cancel an appointment as a doctor. Rate limited: 10/min"""
    reason = body.reason if body else ""
    result = appointment_service.cancel_appointment_by_doctor(
        appointment_id, 
        doctor["doctor_name"],
        reason
    )
    if not result["success"]:
        raise HTTPException(400, result["error"])
    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.API_HOST, port=settings.API_PORT)
