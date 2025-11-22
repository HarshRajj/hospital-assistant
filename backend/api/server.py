"""FastAPI server for hospital voice assistant."""
import sys
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from services.token_service import token_service
from services.chat_service import chat_service


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
async def connect():
    """Generate a LiveKit token for the voice assistant.
    
    This endpoint keeps the LiveKit API secret secure on the backend.
    
    Returns:
        Dictionary containing JWT token, LiveKit URL, and room name
        
    Raises:
        HTTPException: If LiveKit credentials are not configured
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


if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Hospital Voice Assistant API...")
    print(f"📍 API will be available at: http://{settings.API_HOST}:{settings.API_PORT}")
    print(f"🔗 LiveKit URL: {settings.LIVEKIT_URL}")
    uvicorn.run(app, host=settings.API_HOST, port=settings.API_PORT)
