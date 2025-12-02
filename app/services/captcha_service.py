"""
CAPTCHA service.
Handles generation and verification of CAPTCHA challenges.
Uses in-memory storage with expiration.
"""

import uuid
import string
import random
import base64
import io
from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict
from captcha.image import ImageCaptcha
from app.config.settings import settings
import threading
import logging

logger = logging.getLogger(__name__)


class CaptchaStore:
    """Thread-safe in-memory CAPTCHA storage."""
    
    def __init__(self):
        self._store: Dict[str, Dict] = {}
        self._lock = threading.Lock()
    
    def add(self, captcha_id: str, answer: str, expires_at: datetime) -> None:
        """Add a CAPTCHA to the store."""
        with self._lock:
            self._store[captcha_id] = {
                "answer": answer.upper(),
                "expires_at": expires_at,
                "used": False
            }
    
    def verify(self, captcha_id: str, answer: str) -> bool:
        """
        Verify a CAPTCHA answer.
        Returns True if valid, False otherwise.
        Removes CAPTCHA after verification (one-time use).
        """
        with self._lock:
            if captcha_id not in self._store:
                return False
            
            captcha_data = self._store[captcha_id]
            
            # Check if already used
            if captcha_data["used"]:
                logger.warning(f"CAPTCHA {captcha_id} already used")
                return False
            
            # Check if expired
            if datetime.utcnow() > captcha_data["expires_at"]:
                logger.warning(f"CAPTCHA {captcha_id} expired")
                del self._store[captcha_id]
                return False
            
            # Verify answer (case-insensitive)
            is_valid = captcha_data["answer"] == answer.upper()
            
            # Mark as used and remove (one-time use)
            if is_valid:
                del self._store[captcha_id]
            
            return is_valid
    
    def remove(self, captcha_id: str) -> None:
        """Remove a CAPTCHA from the store."""
        with self._lock:
            self._store.pop(captcha_id, None)
    
    def cleanup_expired(self) -> None:
        """Remove expired CAPTCHAs from the store."""
        now = datetime.utcnow()
        with self._lock:
            expired_ids = [
                captcha_id
                for captcha_id, data in self._store.items()
                if now > data["expires_at"]
            ]
            for captcha_id in expired_ids:
                del self._store[captcha_id]
    
    def count(self) -> int:
        """Get the number of active CAPTCHAs."""
        with self._lock:
            return len(self._store)


# Global CAPTCHA store instance
captcha_store = CaptchaStore()


def generate_captcha_text(length: int = 6) -> str:
    """
    Generate random CAPTCHA text.
    
    Args:
        length: Length of CAPTCHA text (default: 6)
        
    Returns:
        str: Random alphanumeric string (uppercase)
    """
    characters = string.ascii_uppercase + string.digits
    # Exclude similar-looking characters (0, O, I, 1)
    characters = characters.replace('0', '').replace('O', '').replace('I', '').replace('1', '')
    return ''.join(random.choices(characters, k=length))


def generate_captcha_image(text: str) -> str:
    """
    Generate CAPTCHA image as base64-encoded PNG.
    
    Args:
        text: CAPTCHA text to render
        
    Returns:
        str: Base64-encoded PNG image with data URI prefix
    """
    try:
        # Create CAPTCHA image generator
        image = ImageCaptcha(width=280, height=90)
        
        # Generate image bytes
        image_bytes = image.generate(text)
        
        # Convert to base64
        base64_image = base64.b64encode(image_bytes.read()).decode('utf-8')
        
        # Return as data URI
        return f"data:image/png;base64,{base64_image}"
    
    except Exception as e:
        logger.error(f"Failed to generate CAPTCHA image: {e}")
        raise ValueError("Failed to generate CAPTCHA image")


def create_captcha() -> Tuple[str, str]:
    """
    Create a new CAPTCHA challenge.
    
    Returns:
        Tuple[str, str]: (captcha_id, captcha_image_base64)
    """
    try:
        # Clean up expired CAPTCHAs periodically
        captcha_store.cleanup_expired()
        
        # Generate CAPTCHA text
        captcha_text = generate_captcha_text()
        
        # Generate unique ID
        captcha_id = str(uuid.uuid4())
        
        # Set expiration time
        expires_at = datetime.utcnow() + timedelta(seconds=settings.captcha_expiry_seconds)
        
        # Store CAPTCHA
        captcha_store.add(captcha_id, captcha_text, expires_at)
        
        # Generate image
        captcha_image = generate_captcha_image(captcha_text)
        
        logger.debug(f"Created CAPTCHA {captcha_id}")
        
        return captcha_id, captcha_image
    
    except Exception as e:
        logger.error(f"Failed to create CAPTCHA: {e}")
        raise ValueError("Failed to create CAPTCHA")


def verify_captcha(captcha_id: str, answer: str) -> bool:
    """
    Verify a CAPTCHA answer.
    
    Args:
        captcha_id: CAPTCHA identifier
        answer: User's answer
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not captcha_id or not answer:
        return False
    
    return captcha_store.verify(captcha_id, answer)


def get_active_captcha_count() -> int:
    """
    Get the number of active CAPTCHAs.
    
    Returns:
        int: Number of active CAPTCHAs
    """
    return captcha_store.count()

