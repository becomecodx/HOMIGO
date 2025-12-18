"""
Firebase token decoding.

Simple JWT decode to extract firebase_id from Firebase ID tokens.
No Admin SDK credentials required - just decodes the JWT payload.
"""
from typing import Dict, Any
import base64
import json
from fastapi import HTTPException, status

from app.config.settings import settings


def init_firebase() -> None:
    """
    Initialize Firebase (no-op for simple JWT decode approach).
    Kept for compatibility with existing code.
    """
    print("✓ Firebase token decoder ready (simple JWT decode mode)")


def decode_firebase_token(id_token: str) -> Dict[str, Any]:
    """
    Decode a Firebase ID token (JWT) to extract claims.
    
    Firebase ID tokens are JWTs with 3 parts: header.payload.signature
    We decode the payload to get user info including 'user_id' (firebase uid).
    
    Args:
        id_token: The Firebase ID token (JWT string)
        
    Returns:
        Dict containing the decoded token claims
        
    Raises:
        HTTPException: If token format is invalid
    """
    try:
        # Split JWT into parts
        parts = id_token.split('.')
        if len(parts) != 3:
            raise ValueError("Invalid JWT format")
        
        # Decode the payload (second part)
        # Add padding if needed for base64 decode
        payload = parts[1]
        padding = 4 - len(payload) % 4
        if padding != 4:
            payload += '=' * padding
        
        decoded_bytes = base64.urlsafe_b64decode(payload)
        claims = json.loads(decoded_bytes.decode('utf-8'))
        
        return claims
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token format: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


def verify_firebase_token(id_token: str) -> Dict[str, Any]:
    """
    Verify/decode a Firebase ID token and return claims.
    
    Args:
        id_token: The Firebase ID token to verify
        
    Returns:
        Dict containing the decoded token claims, including 'uid' (firebase_id)
        
    Raises:
        HTTPException: If token is invalid
    """
    claims = decode_firebase_token(id_token)
    
    # Firebase tokens use 'user_id' or 'sub' for the UID
    uid = claims.get('user_id') or claims.get('sub')
    
    if not uid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing user_id",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Add 'uid' key for consistency (Firebase Admin SDK uses this)
    claims['uid'] = uid
    
    return claims


def get_firebase_app():
    """Get Firebase app instance (returns None for simple decode mode)."""
    return None
