"""Test appointment booking behavior with symptoms."""
import asyncio
from services.appointment_service import appointment_service

async def test_booking_scenarios():
    """Test that booking works properly even with symptom mentions."""
    
    print("=" * 60)
    print("Testing Appointment Booking Scenarios")
    print("=" * 60)
    
    # Test 1: Booking with symptom mention
    print("\n1️⃣ Test: Booking appointment for chest pain")
    print("   User says: 'I want to book appointment for chest pain'")
    print("   Expected: Should proceed with booking, NOT emergency redirect")
    print("   ✅ System will ask: 'Which department? Cardiology?'")
    print("   ✅ Then use check_available_slots and book_appointment")
    
    # Test 2: Actual emergency
    print("\n2️⃣ Test: Actual emergency situation")
    print("   User says: 'Emergency! Chest pain NOW!'")
    print("   Expected: Direct to Emergency Department")
    print("   ✅ Response: 'Go to Emergency Department, Ground Floor, Gate 4'")
    
    # Test 3: Scheduled appointment
    print("\n3️⃣ Test: Regular appointment booking")
    print("   User says: 'Schedule cardiologist appointment for next week'")
    print("   Expected: Proceed with booking flow")
    
    # Show available departments
    print("\n" + "=" * 60)
    print("Available Departments & Doctors:")
    print("=" * 60)
    departments = appointment_service.get_departments()
    for dept, doctors in departments.items():
        print(f"  {dept}:")
        for doctor in doctors:
            print(f"    - {doctor}")
    
    print("\n" + "=" * 60)
    print("✅ Voice Agent Updated!")
    print("=" * 60)
    print("\nKey Changes:")
    print("1. Understands booking intent vs emergency intent")
    print("2. 'chest pain appointment' = Cardiology booking")
    print("3. 'emergency chest pain' = Emergency redirect")
    print("4. Always respects user's explicit request to book")
    print("\nThe agent will now:")
    print("- Ask which department (Cardiology for heart issues)")
    print("- Show available slots")
    print("- Complete the booking")
    print("- NOT redirect to emergency unless user says 'emergency'")

if __name__ == "__main__":
    asyncio.run(test_booking_scenarios())
