"""Doctor configuration - maps email addresses to doctor profiles."""

# Doctor credentials mapping
# Format: email -> doctor_info
DOCTORS = {
    "harsh.raj.cseiot.2022@miet.ac.in": {
        "name": "Dr. Harsh Sharma",
        "department": "Cardiology",
        "email": "harsh.raj.cseiot.2022@miet.ac.in",
        "specialization": "Interventional Cardiology",
        "phone": "(555) 100-2001"
    }
}


def is_doctor(email: str) -> bool:
    """Check if an email belongs to a registered doctor."""
    if not email:
        return False
    return email.lower().strip() in DOCTORS


def get_doctor_info(email: str) -> dict:
    """Get doctor information by email."""
    if not email:
        return None
    return DOCTORS.get(email.lower().strip())


def get_doctor_name_from_email(email: str) -> str:
    """Get doctor's full name from email."""
    if not email:
        return None
    doctor = DOCTORS.get(email.lower().strip())
    return doctor["name"] if doctor else None
