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
        "Ophthalmology": ["Dr. Manish Agarwal"],
        "ENT": ["Dr. Deepak Rao"],
        "Psychiatry": ["Dr. Shalini Gupta", "Dr. Aryan Choudhury"],
        "Pulmonology": ["Dr. Karan Bhatia"],
        "Endocrinology": ["Dr. Nisha Patel"],
        "Urology": ["Dr. Abhishek Jain"],
        "Rheumatology": ["Dr. Priyanka Sharma"],
    }
    
    # Doctor working hours and days from Knowledgebase
    DOCTOR_SCHEDULE = {
        # Cardiology
        "Dr. Harsh Sharma": {"days": [0, 1, 2, 3, 4], "start": "09:00", "end": "17:00"},  # Mon-Fri, 9AM-5PM
        # Pediatrics
        "Dr. Arjun Gupta": {"days": [0, 2, 4], "start": "10:00", "end": "18:00"},  # Mon, Wed, Fri, 10AM-6PM
        # Orthopedics
        "Dr. Sameer Khan": {"days": [1, 3, 5], "start": "08:00", "end": "16:00"},  # Tue, Thu, Sat, 8AM-4PM
        # Neurology
        "Dr. Ananya Reddy": {"days": [0, 1, 2, 3], "start": "11:00", "end": "19:00"},  # Mon-Thu, 11AM-7PM
        # Oncology
        "Dr. Fatima Ahmed": {"days": [0, 1, 2, 3, 4], "start": "09:00", "end": "17:00"},  # By appointment
        # Dermatology
        "Dr. Meera Desai": {"days": [0, 2, 4], "start": "09:00", "end": "17:00"},  # Mon, Wed, Fri, 9AM-5PM
        "Dr. Rohit Malhotra": {"days": [1, 3, 5], "start": "10:00", "end": "16:00"},  # Tue, Thu, Sat, 10AM-4PM
        # General Surgery
        "Dr. Vikram Singh": {"days": [0, 1, 2, 3, 4], "start": "07:00", "end": "15:00"},  # Mon-Fri, 7AM-3PM
        "Dr. Anjali Mehta": {"days": [1, 2, 4], "start": "09:00", "end": "17:00"},  # Tue, Wed, Fri, 9AM-5PM
        # General Medicine
        "Dr. Rajesh Kumar": {"days": [0, 1, 2, 3, 4, 5], "start": "08:00", "end": "14:00"},  # Mon-Sat, 8AM-2PM
        "Dr. Kavita Joshi": {"days": [0, 2, 3, 4], "start": "14:00", "end": "20:00"},  # Mon, Wed, Thu, Fri, 2PM-8PM
        "Dr. Suresh Iyer": {"days": [1, 3, 5], "start": "09:00", "end": "15:00"},  # Tue, Thu, Sat, 9AM-3PM
        # Gastroenterology
        "Dr. Anil Verma": {"days": [0, 2, 4], "start": "10:00", "end": "18:00"},  # Mon, Wed, Fri, 10AM-6PM
        # Nephrology
        "Dr. Pooja Nair": {"days": [1, 3, 5], "start": "09:00", "end": "16:00"},  # Tue, Thu, Sat, 9AM-4PM
        # OB-GYN
        "Dr. Sneha Pillai": {"days": [0, 1, 2, 3, 4], "start": "09:00", "end": "17:00"},  # Mon-Fri, 9AM-5PM
        "Dr. Ritu Kapoor": {"days": [0, 2, 3], "start": "10:00", "end": "18:00"},  # Mon, Wed, Thu, 10AM-6PM
        # Ophthalmology
        "Dr. Manish Agarwal": {"days": [0, 1, 3, 4], "start": "08:00", "end": "16:00"},  # Mon, Tue, Thu, Fri, 8AM-4PM
        # ENT
        "Dr. Deepak Rao": {"days": [0, 2, 4], "start": "09:00", "end": "17:00"},  # Mon, Wed, Fri, 9AM-5PM
        # Psychiatry
        "Dr. Shalini Gupta": {"days": [0, 1, 2, 3, 4], "start": "10:00", "end": "18:00"},  # Mon-Fri, 10AM-6PM
        "Dr. Aryan Choudhury": {"days": [1, 3, 5], "start": "11:00", "end": "17:00"},  # Tue, Thu, Sat, 11AM-5PM
        # Pulmonology
        "Dr. Karan Bhatia": {"days": [0, 2, 4], "start": "09:00", "end": "16:00"},  # Mon, Wed, Fri, 9AM-4PM
        # Endocrinology
        "Dr. Nisha Patel": {"days": [1, 3], "start": "10:00", "end": "17:00"},  # Tue, Thu, 10AM-5PM
        # Urology
        "Dr. Abhishek Jain": {"days": [0, 1, 3], "start": "08:00", "end": "15:00"},  # Mon, Tue, Thu, 8AM-3PM
        # Rheumatology
        "Dr. Priyanka Sharma": {"days": [2, 4], "start": "10:00", "end": "16:00"},  # Wed, Fri, 10AM-4PM
    }
    
    # Default time slots (30-min intervals)
    ALL_TIME_SLOTS = [
        "07:00", "07:30", "08:00", "08:30", "09:00", "09:30", "10:00", "10:30", 
        "11:00", "11:30", "12:00", "12:30", "13:00", "13:30", "14:00", "14:30",
        "15:00", "15:30", "16:00", "16:30", "17:00", "17:30", "18:00", "18:30", "19:00", "19:30"
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
    
    def _get_doctor_time_slots(self, doctor: str, date: str) -> List[str]:
        """Get valid time slots for a doctor on a specific date based on their schedule."""
        schedule = self.DOCTOR_SCHEDULE.get(doctor)
        if not schedule:
            # Default 9AM-5PM Mon-Fri if doctor not in schedule
            return [s for s in self.ALL_TIME_SLOTS if "09:00" <= s < "17:00"]
        
        # Check if doctor works on this day of week
        try:
            appointment_date = datetime.strptime(date, "%Y-%m-%d").date()
            day_of_week = appointment_date.weekday()  # 0=Monday, 6=Sunday
            
            if day_of_week not in schedule["days"]:
                return []  # Doctor doesn't work this day
            
            # Filter slots within doctor's working hours
            start = schedule["start"]
            end = schedule["end"]
            return [s for s in self.ALL_TIME_SLOTS if start <= s < end]
        except ValueError:
            return []
    
    def get_available_slots(self, date: str, department: str, doctor: str) -> List[str]:
        """Get available time slots for a specific date, department, and doctor."""
        self._load_from_file()  # Reload to get latest appointments
        
        # Get doctor's working slots for this date
        doctor_slots = self._get_doctor_time_slots(doctor, date)
        if not doctor_slots:
            return []  # Doctor doesn't work this day
        
        # Remove already booked slots
        booked_slots = [
            apt.time for apt in self.appointments.values()
            if apt.date == date and apt.department == department 
            and apt.doctor == doctor and apt.status == "confirmed"
        ]
        
        available = [slot for slot in doctor_slots if slot not in booked_slots]
        
        # If today, filter out past times
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
        # Reload to get latest appointments (prevent race conditions)
        self._load_from_file()
        
        # Validate inputs
        if department not in self.DEPARTMENTS:
            return {"success": False, "error": f"Invalid department"}
        if doctor not in self.DEPARTMENTS[department]:
            return {"success": False, "error": f"Doctor not in {department}"}
        
        # Check if time is valid for this doctor's schedule
        doctor_slots = self._get_doctor_time_slots(doctor, date)
        if not doctor_slots:
            return {"success": False, "error": f"{doctor} is not available on this day"}
        if time not in doctor_slots:
            return {"success": False, "error": f"Invalid time - {doctor} works {self.DOCTOR_SCHEDULE.get(doctor, {}).get('start', '09:00')} to {self.DOCTOR_SCHEDULE.get(doctor, {}).get('end', '17:00')}"}
        
        try:
            if datetime.strptime(date, "%Y-%m-%d").date() < datetime.now().date():
                return {"success": False, "error": "Cannot book in the past"}
        except ValueError:
            return {"success": False, "error": "Invalid date format (YYYY-MM-DD)"}
        
        if not patient_name or len(patient_name.strip()) < 2:
            return {"success": False, "error": "Invalid patient name"}
        if not isinstance(patient_age, int) or patient_age < 0 or patient_age > 150:
            return {"success": False, "error": "Invalid age"}
        if patient_gender not in ["Male", "Female", "Other"]:
            return {"success": False, "error": "Gender must be Male, Female, or Other"}
        
        # CHECK 1: Is the doctor's slot already taken by ANY user?
        doctor_booked_at_time = [
            apt for apt in self.appointments.values()
            if apt.doctor == doctor and apt.date == date and apt.time == time and apt.status == "confirmed"
        ]
        if doctor_booked_at_time:
            return {"success": False, "error": f"{doctor} already has an appointment at {time} on {date}. Please choose a different time."}
        
        # CHECK 2: Does THIS user already have an appointment at the same time (any doctor)?
        user_booked_at_time = [
            apt for apt in self.appointments.values()
            if apt.user_id == user_id and apt.date == date and apt.time == time and apt.status == "confirmed"
        ]
        if user_booked_at_time:
            existing = user_booked_at_time[0]
            return {"success": False, "error": f"You already have an appointment with {existing.doctor} at {time} on {date}. Please choose a different time."}
        
        # CHECK 3: Does THIS user already have an appointment with the SAME doctor on the SAME day?
        user_same_doctor_same_day = [
            apt for apt in self.appointments.values()
            if apt.user_id == user_id and apt.doctor == doctor and apt.date == date and apt.status == "confirmed"
        ]
        if user_same_doctor_same_day:
            existing = user_same_doctor_same_day[0]
            return {"success": False, "error": f"You already have an appointment with {doctor} at {existing.time} on {date}. You can only book one appointment per doctor per day."}
        
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
        
        # Check if user has other appointments on same day (for info only)
        other_appointments = [
            apt for apt in self.appointments.values()
            if apt.user_id == user_id and apt.date == date and apt.id != apt_id and apt.status == "confirmed"
        ]
        
        message = f"Booked {patient_name} with {doctor} on {date} at {time}"
        if other_appointments:
            existing_details = ", ".join([f"{apt.doctor} at {apt.time}" for apt in other_appointments])
            message += f". Note: You also have appointment(s) on this date with {existing_details}"
        
        return {"success": True, "appointment": appointment.model_dump(), "message": message}
    
    def _mark_expired_status(self, appointment: Dict) -> Dict:
        """Mark appointment as expired if it's in the past."""
        try:
            apt_datetime = datetime.strptime(f"{appointment['date']} {appointment['time']}", "%Y-%m-%d %H:%M")
            if apt_datetime < datetime.now():
                appointment["status"] = "expired"
        except ValueError:
            pass
        return appointment
    
    def get_user_appointments(self, user_id: str) -> List[Dict]:
        """Get all appointments for a user with expired status for past ones."""
        self._load_from_file()
        apts = []
        for apt in self.appointments.values():
            if apt.user_id == user_id and apt.status in ["confirmed", "expired"]:
                apt_dict = apt.model_dump()
                apt_dict = self._mark_expired_status(apt_dict)
                apts.append(apt_dict)
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
        """Cancel an appointment (by patient)."""
        self._load_from_file()
        if appointment_id not in self.appointments:
            return {"success": False, "error": "Appointment not found"}
        
        apt = self.appointments[appointment_id]
        if apt.user_id != user_id:
            return {"success": False, "error": "Unauthorized"}
        
        apt.status = "cancelled"
        self._save_to_file()
        return {"success": True, "message": f"Appointment {appointment_id} cancelled"}
    
    def cancel_appointment_by_doctor(self, appointment_id: str, doctor_name: str, reason: str = "") -> Dict:
        """Cancel an appointment (by doctor)."""
        self._load_from_file()
        if appointment_id not in self.appointments:
            return {"success": False, "error": "Appointment not found"}
        
        apt = self.appointments[appointment_id]
        if apt.doctor != doctor_name:
            return {"success": False, "error": "Unauthorized - this appointment is not with you"}
        
        if apt.status != "confirmed":
            return {"success": False, "error": f"Cannot cancel - appointment is already {apt.status}"}
        
        apt.status = "cancelled_by_doctor"
        self._save_to_file()
        
        message = f"Appointment {appointment_id} with {apt.patient_name} on {apt.date} at {apt.time} has been cancelled"
        if reason:
            message += f". Reason: {reason}"
        
        return {"success": True, "message": message, "patient_user_id": apt.user_id}
    
    def get_all_appointments(self) -> List[Dict]:
        """Get all confirmed appointments."""
        self._load_from_file()
        apts = [apt.model_dump() for apt in self.appointments.values() if apt.status == "confirmed"]
        apts.sort(key=lambda x: (x["date"], x["time"]))
        return apts
    
    def get_departments(self) -> Dict[str, List[str]]:
        """Get all departments with their doctors."""
        return self.DEPARTMENTS.copy()
    
    def get_doctor_appointments_today(self, doctor_name: str) -> List[Dict]:
        """Get today's appointments for a specific doctor."""
        self._load_from_file()
        today = datetime.now().date().isoformat()
        
        apts = []
        for apt in self.appointments.values():
            if apt.doctor == doctor_name and apt.date == today and apt.status in ["confirmed", "expired"]:
                apt_dict = apt.model_dump()
                apt_dict = self._mark_expired_status(apt_dict)
                apts.append(apt_dict)
        apts.sort(key=lambda x: x["time"])
        return apts
    
    def get_doctor_all_appointments(self, doctor_name: str) -> List[Dict]:
        """Get all future appointments for a specific doctor."""
        self._load_from_file()
        today = datetime.now().date().isoformat()
        
        apts = [apt.model_dump() for apt in self.appointments.values()
                if apt.doctor == doctor_name and apt.date >= today and apt.status == "confirmed"]
        apts.sort(key=lambda x: (x["date"], x["time"]))
        return apts
    
    def get_doctor_past_week_appointments(self, doctor_name: str) -> List[Dict]:
        """Get past week's appointments for a specific doctor."""
        from datetime import timedelta
        
        self._load_from_file()
        today = datetime.now().date()
        week_ago = (today - timedelta(days=7)).isoformat()
        today_str = today.isoformat()
        
        apts = []
        for apt in self.appointments.values():
            if apt.doctor == doctor_name and week_ago <= apt.date <= today_str and apt.status in ["confirmed", "expired"]:
                apt_dict = apt.model_dump()
                apt_dict = self._mark_expired_status(apt_dict)
                apts.append(apt_dict)
        apts.sort(key=lambda x: (x["date"], x["time"]), reverse=True)
        return apts


appointment_service = AppointmentService()
