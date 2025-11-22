"""LiveKit token generation service."""
import uuid
from typing import Optional
from livekit import api
from config import settings


class TokenService:
    """Service for generating LiveKit access tokens."""
    
    def __init__(self):
        """Initialize TokenService with LiveKit credentials from settings."""
        self.url = settings.LIVEKIT_URL
        self.api_key = settings.LIVEKIT_API_KEY
        self.api_secret = settings.LIVEKIT_API_SECRET
    
    def is_configured(self) -> bool:
        """Check if LiveKit credentials are properly configured."""
        return settings.validate_livekit()
    
    def generate_room_name(self, prefix: str = "hospital-assistant") -> str:
        """Generate a unique room name.
        
        Args:
            prefix: Room name prefix (default: "hospital-assistant")
            
        Returns:
            Unique room name with format: {prefix}-{random_hex}
        """
        return f"{prefix}-{uuid.uuid4().hex[:8]}"
    
    def create_token(
        self,
        room_name: str,
        identity: str = "user",
        name: Optional[str] = None
    ) -> dict[str, str]:
        """Generate a LiveKit access token for a room.
        
        Args:
            room_name: Name of the LiveKit room
            identity: User identity (default: "user")
            name: Display name for the user (default: "Hospital Visitor")
            
        Returns:
            Dictionary with token, url, and room name
            
        Raises:
            ValueError: If LiveKit credentials are not configured
        """
        if not self.is_configured():
            raise ValueError(
                "LiveKit credentials not configured. Check your .env file."
            )
        
        # Create access token
        token = api.AccessToken(self.api_key, self.api_secret)
        token.with_identity(identity)
        token.with_name(name or "Hospital Visitor")
        token.with_grants(
            api.VideoGrants(
                room_join=True,
                room=room_name,
            )
        )
        
        return {
            "token": token.to_jwt(),
            "url": self.url,
            "room": room_name,
        }
    
    def generate_connection(
        self,
        identity: str = "user",
        name: Optional[str] = None,
        room_prefix: str = "hospital-assistant"
    ) -> dict[str, str]:
        """Generate a complete LiveKit connection (room + token).
        
        Args:
            identity: User identity (default: "user")
            name: Display name for the user
            room_prefix: Prefix for generated room name
            
        Returns:
            Dictionary with token, url, and room name
        """
        room_name = self.generate_room_name(prefix=room_prefix)
        return self.create_token(room_name=room_name, identity=identity, name=name)


# Singleton instance
token_service = TokenService()
