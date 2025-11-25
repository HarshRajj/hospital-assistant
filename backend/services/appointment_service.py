"""In-memory appointment booking service."""
from datetime import datetime, time, timedelta
from typing import Dict, List, Optional
from pydantic import BaseModel


class Appointment(BaseModel):
    """Appointment data model."""
    id: str
    user_id: str
    user_name: str
    department: str
    doctor: str
    date: str  # YYYY-MM-DD format
    time: str  # HH:MM format
    status: str = "confirmed"  # confirmed, cancelled
    created_at: str


class AppointmentService:
    """Service for managing appointments in-memory."""
    
    # Available departments with doctors
    DEPARTMENTS = {
        "Cardiology": ["Dr. Sarah Johnson", "Dr. Michael Chen"],
        "Pediatrics": ["Dr. Emily Williams", "Dr. James Martinez"],
        "Orthopedics": ["Dr. Robert Brown", "Dr. Lisa Anderson"],
        "Neurology": ["Dr. David Wilson", "Dr. Jennifer Taylor"],
        "Oncology": ["Dr. Christopher Lee", "Dr. Amanda White"],
        "Ophthalmology": ["Dr. Thomas Garcia", "Dr. Maria Rodriguez"],
        "General Medicine": ["Dr. Daniel Thompson", "Dr. Patricia Moore"],
    }
    
    # Available time slots (30-min intervals, 9 AM - 5 PM)
    TIME_SLOTS = [
        "09:00", "09:30", "10:00", "10:30", "11:00", "11:30",
        "12:00", "12:30", "13:00", "13:30", "14:00", "14:30",
        "15:00", "15:30", "16:00", "16:30", "17:00"
    ]
    
    def __init__(self):
        """Initialize appointment service with empty storage."""
        self.appointments: Dict[str, Appointment] = {}
        self._counter = 0
    
    def _generate_id(self) -> str:
        """Generate unique appointment ID."""
        self._counter += 1
        timestamp = datetime.now().strftime("%Y%m%d")
        return f"APT-{timestamp}-{self._counter:04d}"
    
    def get_available_slots(self, date: str, department: str, doctor: str) -> List[str]:
        """Get available time slots for a specific date, department, and doctor.
        
        Args:
            date: Date in YYYY-MM-DD format
            department: Department name
            doctor: Doctor name
            
        Returns:
            List of available time slots
        """
        # Get all booked slots for this date, department, and doctor
        booked_slots = [
            apt.time for apt in self.appointments.values()
            if apt.date == date and apt.department == department 
            and apt.doctor == doctor and apt.status == "confirmed"
        ]
        
        # Return available slots
        return [slot for slot in self.TIME_SLOTS if slot not in booked_slots]
    
    def book_appointment(
        self,
        user_id: str,
        user_name: str,
        department: str,
        doctor: str,
        date: str,
        time: str
    ) -> Dict:
        """Book a new appointment.
        
        Args:
            user_id: User ID from authentication
            user_name: User's display name
            department: Department name
            doctor: Doctor name
            date: Date in YYYY-MM-DD format
            time: Time in HH:MM format
            
        Returns:
            Dictionary with success status and appointment details or error message
        """
        # Validate department
        if department not in self.DEPARTMENTS:
            return {
                "success": False,
                "error": f"Invalid department. Available: {', '.join(self.DEPARTMENTS.keys())}"
            }
        
        # Validate doctor
        if doctor not in self.DEPARTMENTS[department]:
            return {
                "success": False,
                "error": f"Doctor not available in {department}. Available: {', '.join(self.DEPARTMENTS[department])}"
            }
        
        # Validate time slot
        if time not in self.TIME_SLOTS:
            return {
                "success": False,
                "error": f"Invalid time slot. Available: {', '.join(self.TIME_SLOTS)}"
            }
        
        # Validate date (must be today or future)
        try:
            appointment_date = datetime.strptime(date, "%Y-%m-%d").date()
            if appointment_date < datetime.now().date():
                return {
                    "success": False,
                    "error": "Cannot book appointments in the past"
                }
        except ValueError:
            return {
                "success": False,
                "error": "Invalid date format. Use YYYY-MM-DD"
            }
        
        # Check if slot is available
        available_slots = self.get_available_slots(date, department, doctor)
        if time not in available_slots:
            return {
                "success": False,
                "error": f"Time slot {time} is not available. Available slots: {', '.join(available_slots)}"
            }
        
        # Create appointment
        appointment = Appointment(
            id=self._generate_id(),
            user_id=user_id,
            user_name=user_name,
            department=department,
            doctor=doctor,
            date=date,
            time=time,
            status="confirmed",
            created_at=datetime.now().isoformat()
        )
        
        self.appointments[appointment.id] = appointment
        
        return {
            "success": True,
            "appointment": appointment.model_dump(),
            "message": f"Appointment booked with {doctor} in {department} on {date} at {time}"
        }
    
    def get_user_appointments(self, user_id: str) -> List[Dict]:
        """Get all appointments for a user.
        
        Args:
            user_id: User ID from authentication
            
        Returns:
            List of user's appointments
        """
        user_appointments = [
            apt.model_dump() for apt in self.appointments.values()
            if apt.user_id == user_id and apt.status == "confirmed"
        ]
        # Sort by date and time
        user_appointments.sort(key=lambda x: (x["date"], x["time"]))
        return user_appointments
    
    def cancel_appointment(self, appointment_id: str, user_id: str) -> Dict:
        """Cancel an appointment.
        
        Args:
            appointment_id: Appointment ID
            user_id: User ID from authentication
            
        Returns:
            Dictionary with success status and message
        """
        if appointment_id not in self.appointments:
            return {
                "success": False,
                "error": "Appointment not found"
            }
        
        appointment = self.appointments[appointment_id]
        
        # Verify user owns this appointment
        if appointment.user_id != user_id:
            return {
                "success": False,
                "error": "Unauthorized to cancel this appointment"
            }
        
        # Cancel appointment
        appointment.status = "cancelled"
        
        return {
            "success": True,
            "message": f"Appointment {appointment_id} cancelled successfully"
        }
    
    def get_all_appointments(self) -> List[Dict]:
        """Get all confirmed appointments (admin view).
        
        Returns:
            List of all confirmed appointments
        """
        confirmed = [
            apt.model_dump() for apt in self.appointments.values()
            if apt.status == "confirmed"
        ]
        confirmed.sort(key=lambda x: (x["date"], x["time"]))
        return confirmed
    
    def get_departments(self) -> Dict[str, List[str]]:
        """Get all departments with their doctors.
        
        Returns:
            Dictionary mapping departments to doctors
        """
        return self.DEPARTMENTS.copy()


# Singleton instance
appointment_service = AppointmentService()
