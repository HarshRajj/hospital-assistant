from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from livekit import api
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="Hospital Voice Assistant API")

# CORS configuration - allow Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# LiveKit credentials from .env
LIVEKIT_URL = os.getenv("LIVEKIT_URL")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "ok", "message": "Hospital Voice Assistant API is running"}


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.post("/connect")
async def connect():
    """
    Generate a LiveKit token for the voice assistant.
    This keeps the API secret secure on the backend.
    """
    if not all([LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET]):
        return {
            "error": "LiveKit credentials not configured. Check your .env file."
        }, 500

    # Generate unique room name for this session
    import uuid
    room_name = f"hospital-assistant-{uuid.uuid4().hex[:8]}"
    
    # Generate token
    token = api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
    token.with_identity("user")
    token.with_name("Hospital Visitor")
    token.with_grants(
        api.VideoGrants(
            room_join=True,
            room=room_name,
        )
    )

    jwt_token = token.to_jwt()

    return {
        "token": jwt_token,
        "url": LIVEKIT_URL,
        "room": room_name,
    }


if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Hospital Voice Assistant API...")
    print(f"📍 API will be available at: http://localhost:8000")
    print(f"🔗 LiveKit URL: {LIVEKIT_URL}")
    uvicorn.run(app, host="0.0.0.0", port=8000)
