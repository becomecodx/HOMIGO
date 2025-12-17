"""
Firebase Admin SDK initialization and token verification.
"""
import os
from typing import Optional, Dict, Any
import firebase_admin
from firebase_admin import credentials, auth
from fastapi import HTTPException, status


_firebase_app: Optional[firebase_admin.App] = None


def init_firebase() -> None:
    """
    Initialize Firebase Admin SDK with service account credentials.
    
    Reads the service account path from environment variable FIREBASE_SERVICE_ACCOUNT_PATH.
    If not set, attempts to use default credentials.
    """
    global _firebase_app
    
    if _firebase_app is not None:
        return  # Already initialized
    
    service_account_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH")
    
    try:
        if service_account_path and os.path.exists(service_account_path):
            cred = credentials.Certificate(service_account_path)
            _firebase_app = firebase_admin.initialize_app(cred)
            print(f"✓ Firebase initialized with service account: {service_account_path}")
        else:
            # Try default credentials (useful for Cloud Run, etc.)
            _firebase_app = firebase_admin.initialize_app()
            print("✓ Firebase initialized with default credentials")
    except Exception as e:
        print(f"⚠ Firebase initialization failed: {e}")
        raise


def verify_firebase_token(id_token: str) -> Dict[str, Any]:
    """
    Verify a Firebase ID token and return the decoded claims.
    
    Args:
        id_token: The Firebase ID token to verify
        
    Returns:
        Dict containing the decoded token claims, including 'uid' (firebase_id)
        
    Raises:
        HTTPException: If token is invalid or verification fails
    """
    if _firebase_app is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Firebase not initialized"
        )
    
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except auth.InvalidIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Firebase ID token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except auth.ExpiredIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Firebase ID token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token verification failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_firebase_app() -> Optional[firebase_admin.App]:
    """Get the initialized Firebase app instance."""
    return _firebase_app
