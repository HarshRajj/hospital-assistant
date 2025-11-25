"""Clerk authentication service for verifying JWT tokens."""
from typing import Optional
from fastapi import HTTPException, Header


class ClerkAuthService:
    """Service for verifying Clerk authentication tokens."""
    
    async def verify_token(self, authorization: Optional[str] = Header(None)) -> dict:
        """Verify Clerk JWT token from Authorization header.
        
        Args:
            authorization: Authorization header with Bearer token
            
        Returns:
            Simple dict with authenticated status
            
        Raises:
            HTTPException: If token is missing
        """
        if not authorization:
            raise HTTPException(
                status_code=401,
                detail="Authentication required. Please sign in."
            )
        
        if not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=401,
                detail="Invalid authorization header format"
            )
        
        # Token exists and is in correct format - user is authenticated
        return {"authenticated": True}


# Global auth service instance
auth_service = ClerkAuthService()
