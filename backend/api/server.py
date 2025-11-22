"""FastAPI server for hospital voice assistant."""
import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from services.token_service import token_service


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


if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Hospital Voice Assistant API...")
    print(f"📍 API will be available at: http://{settings.API_HOST}:{settings.API_PORT}")
    print(f"🔗 LiveKit URL: {settings.LIVEKIT_URL}")
    uvicorn.run(app, host=settings.API_HOST, port=settings.API_PORT)
