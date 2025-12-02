"""
Input validation utilities.
Provides validation functions for user inputs.
"""

import re
from typing import Optional


def validate_name(name: str) -> tuple[bool, Optional[str]]:
    """
    Validate first or last name.
    Names must contain only letters and spaces, 2-50 characters.
    
    Args:
        name: Name to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not name or not isinstance(name, str):
        return False, "Name is required"
    
    if len(name) < 2 or len(name) > 50:
        return False, "Name must be between 2 and 50 characters"
    
    # Only letters and spaces allowed
    if not re.match(r'^[a-zA-Z\s]+$', name):
        return False, "Name can only contain letters and spaces"
    
    return True, None


def validate_phone_number(phone: str) -> tuple[bool, Optional[str]]:
    """
    Validate phone number.
    Phone numbers should be 10-15 digits (after removing formatting).
    
    Args:
        phone: Phone number to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not phone or not isinstance(phone, str):
        return False, "Phone number is required"
    
    # Remove common formatting characters
    cleaned_phone = re.sub(r'[\s\-\(\)\+]', '', phone)
    
    # Check if it's all digits
    if not cleaned_phone.isdigit():
        return False, "Phone number must contain only digits"
    
    # Check length (10-15 digits)
    if len(cleaned_phone) < 10 or len(cleaned_phone) > 15:
        return False, "Phone number must be between 10 and 15 digits"
    
    return True, None


def validate_password_strength(password: str) -> tuple[bool, Optional[str]]:
    """
    Validate password strength.
    Password must be at least 8 characters and contain:
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    
    Args:
        password: Password to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not password or not isinstance(password, str):
        return False, "Password is required"
    
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    # Check for uppercase letter
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    # Check for lowercase letter
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    # Check for digit
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    
    # Check for special character
    if not re.search(r'[!@#$%^&*(),.?":{}|<>\[\]\\/]', password):
        return False, "Password must contain at least one special character"
    
    return True, None


def sanitize_phone_number(phone: str) -> str:
    """
    Sanitize phone number by removing formatting characters.
    
    Args:
        phone: Phone number to sanitize
        
    Returns:
        str: Sanitized phone number
    """
    return re.sub(r'[\s\-\(\)\+]', '', phone)

