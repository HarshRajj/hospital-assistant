"""Appointment booking service with JSON file persistence."""
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List
from pydantic import BaseModel


class Appointment(BaseModel):
    """Appointment data model."""
    id: str
    user_id: str
    patient_name: str
    patient_age: int
    patient_gender: str
    department: str
    doctor: str
    date: str
    time: str
    status: str = "confirmed"
    created_at: str


class AppointmentService:
    """Service for managing appointments with JSON file persistence."""
    
    DEPARTMENTS = {
        "Cardiology": ["Dr. Harsh Sharma"],
        "Pediatrics": ["Dr. Arjun Gupta"],
        "Orthopedics": ["Dr. Sameer Khan"],
        "Neurology": ["Dr. Ananya Reddy"],
        "Oncology": ["Dr. Fatima Ahmed"],
        "Dermatology": ["Dr. Meera Desai", "Dr. Rohit Malhotra"],
        "General Surgery": ["Dr. Vikram Singh", "Dr. Anjali Mehta"],
        "General Medicine": ["Dr. Rajesh Kumar", "Dr. Kavita Joshi", "Dr. Suresh Iyer"],
        "Gastroenterology": ["Dr. Anil Verma"],
        "Nephrology": ["Dr. Pooja Nair"],
        "OB-GYN": ["Dr. Sneha Pillai", "Dr. Ritu Kapoor"],
    }
    
    TIME_SLOTS = [
        "09:00", "09:30", "10:00", "10:30", "11:00", "11:30",
        "12:00", "12:30", "13:00", "13:30", "14:00", "14:30",
        "15:00", "15:30", "16:00", "16:30", "17:00"
    ]
    
    def __init__(self):
        self.data_file = Path(__file__).parent.parent / "data" / "appointments.json"
        self.data_file.parent.mkdir(exist_ok=True)
        self.appointments: Dict[str, Appointment] = {}
        self._counter = 0
        self._load_from_file()
    
    def _load_from_file(self):
        """Load appointments from JSON file."""
        if self.data_file.exists():
            try:
                with open(self.data_file, "r") as f:
                    data = json.load(f)
                self._counter = data.get("counter", 0)
                for apt_id, apt_data in data.get("appointments", {}).items():
                    # Handle old schema migration
                    if "patient_name" not in apt_data:
                        apt_data["patient_name"] = apt_data.get("user_name", "Unknown")
                        apt_data["patient_age"] = apt_data.get("patient_age", 0)
                        apt_data["patient_gender"] = apt_data.get("patient_gender", "Other")
                    self.appointments[apt_id] = Appointment(**apt_data)
            except Exception as e:
                print(f"Error loading appointments: {e}")
    
    def _save_to_file(self):
        """Save appointments to JSON file."""
        data = {
            "appointments": {k: v.model_dump() for k, v in self.appointments.items()},
            "counter": self._counter,
            "last_updated": datetime.now().isoformat()
        }
        with open(self.data_file, "w") as f:
            json.dump(data, f, indent=2)
    
    def get_available_slots(self, date: str, department: str, doctor: str) -> List[str]:
        """Get available time slots for a specific date, department, and doctor."""
        self._load_from_file()  # Reload to get latest appointments
        
        booked_slots = [
            apt.time for apt in self.appointments.values()
            if apt.date == date and apt.department == department 
            and apt.doctor == doctor and apt.status == "confirmed"
        ]
        
        available = [slot for slot in self.TIME_SLOTS if slot not in booked_slots]
        
        try:
            appointment_date = datetime.strptime(date, "%Y-%m-%d").date()
            today = datetime.now().date()
            if appointment_date == today:
                current_time = datetime.now().strftime("%H:%M")
                available = [slot for slot in available if slot > current_time]
            elif appointment_date < today:
                return []
        except ValueError:
            pass
        
        return available
    
    def book_appointment(self, user_id: str, patient_name: str, patient_age: int,
                        patient_gender: str, department: str, doctor: str, date: str, time: str) -> Dict:
        """Book a new appointment."""
        # Validate inputs
        if department not in self.DEPARTMENTS:
            return {"success": False, "error": f"Invalid department"}
        if doctor not in self.DEPARTMENTS[department]:
            return {"success": False, "error": f"Doctor not in {department}"}
        if time not in self.TIME_SLOTS:
            return {"success": False, "error": "Invalid time slot"}
        
        try:
            if datetime.strptime(date, "%Y-%m-%d").date() < datetime.now().date():
                return {"success": False, "error": "Cannot book in the past"}
        except ValueError:
            return {"success": False, "error": "Invalid date format (YYYY-MM-DD)"}
        
        if time not in self.get_available_slots(date, department, doctor):
            return {"success": False, "error": f"Slot {time} not available"}
        
        if not patient_name or len(patient_name.strip()) < 2:
            return {"success": False, "error": "Invalid patient name"}
        if not isinstance(patient_age, int) or patient_age < 0 or patient_age > 150:
            return {"success": False, "error": "Invalid age"}
        if patient_gender not in ["Male", "Female", "Other"]:
            return {"success": False, "error": "Gender must be Male, Female, or Other"}
        
        # Check if user already has an appointment on this date
        existing_on_date = [
            apt for apt in self.appointments.values()
            if apt.user_id == user_id and apt.date == date and apt.status == "confirmed"
        ]
        
        # Create and save appointment
        self._counter += 1
        apt_id = f"APT-{datetime.now().strftime('%Y%m%d')}-{self._counter:04d}"
        
        appointment = Appointment(
            id=apt_id, user_id=user_id, patient_name=patient_name.strip(),
            patient_age=patient_age, patient_gender=patient_gender,
            department=department, doctor=doctor, date=date, time=time,
            status="confirmed", created_at=datetime.now().isoformat()
        )
        
        self.appointments[apt_id] = appointment
        self._save_to_file()
        
        # Add note if multiple appointments on same day
        message = f"Booked {patient_name} with {doctor} on {date} at {time}"
        if existing_on_date:
            existing_details = ", ".join([f"{apt.doctor} at {apt.time}" for apt in existing_on_date])
            message += f". Note: You already have appointment(s) on this date with {existing_details}"
        
        return {"success": True, "appointment": appointment.model_dump(), "message": message}
    
    def get_user_appointments(self, user_id: str) -> List[Dict]:
        """Get all appointments for a user."""
        self._load_from_file()
        apts = [apt.model_dump() for apt in self.appointments.values()
                if apt.user_id == user_id and apt.status == "confirmed"]
        apts.sort(key=lambda x: (x["date"], x["time"]))
        return apts
    
    def get_user_appointments_on_date(self, user_id: str, date: str) -> List[Dict]:
        """Get user's appointments on a specific date."""
        self._load_from_file()
        apts = [apt.model_dump() for apt in self.appointments.values()
                if apt.user_id == user_id and apt.date == date and apt.status == "confirmed"]
        apts.sort(key=lambda x: x["time"])
        return apts
    
    def cancel_appointment(self, appointment_id: str, user_id: str) -> Dict:
        """Cancel an appointment."""
        self._load_from_file()
        if appointment_id not in self.appointments:
            return {"success": False, "error": "Appointment not found"}
        
        apt = self.appointments[appointment_id]
        if apt.user_id != user_id:
            return {"success": False, "error": "Unauthorized"}
        
        apt.status = "cancelled"
        self._save_to_file()
        return {"success": True, "message": f"Appointment {appointment_id} cancelled"}
    
    def get_all_appointments(self) -> List[Dict]:
        """Get all confirmed appointments."""
        self._load_from_file()
        apts = [apt.model_dump() for apt in self.appointments.values() if apt.status == "confirmed"]
        apts.sort(key=lambda x: (x["date"], x["time"]))
        return apts
    
    def get_departments(self) -> Dict[str, List[str]]:
        """Get all departments with their doctors."""
        return self.DEPARTMENTS.copy()


appointment_service = AppointmentService()
