"""Service functions for Firebase-related auth actions.

For now this implements a simple static verification that checks the
provided project metadata against the values the user supplied.

Later this can be extended to call Firebase Admin SDK or REST APIs.
"""
from typing import Dict
import logging
from .models import (
    ProjectVerifyRequest,
    ProjectVerifyResponse,
    FirebaseSignupRequest,
    FirebaseSignupResponse,
    FirebaseLoginRequest,
    FirebaseLoginResponse,
)

logger = logging.getLogger(__name__)

# Project credentials the user supplied (used for verification)
_FIREBASE_PROJECT = {
    "project_name": "Homigo",
    "project_id": "homigo-26880",
    "project_number": "715785724568",
    "environment_type": "Unspecified",
    "public_facing_name": "project-715785724568",
}


def verify_project(request: ProjectVerifyRequest) -> ProjectVerifyResponse:
    """Verify provided project metadata against known values.

    This is intentionally simple: it performs a case-insensitive match on
    project_name and exact match on project_id and project_number.
    """
    logger.debug("Verifying project metadata: %s", request.dict())

    name_match = request.project_name.strip().lower() == _FIREBASE_PROJECT["project_name"].lower()
    id_match = request.project_id.strip() == _FIREBASE_PROJECT["project_id"]
    number_match = request.project_number.strip() == _FIREBASE_PROJECT["project_number"]

    matched = bool(name_match and id_match and number_match)

    message = "Project metadata matched" if matched else "Project metadata did not match"

    return ProjectVerifyResponse(
        success=matched,
        message=message,
        matched=matched,
        project_name=_FIREBASE_PROJECT["project_name"],
        project_id=_FIREBASE_PROJECT["project_id"],
        project_number=_FIREBASE_PROJECT["project_number"],
    )


def signup(request: FirebaseSignupRequest) -> FirebaseSignupResponse:
    """Placeholder signup using Firebase credentials.

    Currently this function just simulates user creation and returns a
    fake user id when the project is considered configured. In future this
    should call Firebase Admin SDK (create_user) or Firebase Authentication REST API.
    """
    logger.info("Simulated signup for %s", request.email)
    # NOTE: this is intentionally simple. Replace with real Firebase calls.
    fake_user_id = "firebase|simulated|" + request.email
    return FirebaseSignupResponse(success=True, message="User created (simulated)", user_id=fake_user_id)


def login(request: FirebaseLoginRequest) -> FirebaseLoginResponse:
    """Placeholder login that returns a simulated token.

    Replace later with Firebase custom token generation or verification flows.
    """
    logger.info("Simulated login for %s", request.email)
    fake_token = "simulated-token-for:" + request.email
    return FirebaseLoginResponse(success=True, message="Login successful (simulated)", token=fake_token)
