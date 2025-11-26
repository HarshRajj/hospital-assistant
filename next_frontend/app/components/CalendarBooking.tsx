"use client";

import { useState, useEffect } from "react";
import { useAuth } from "@clerk/nextjs";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

interface Department {
  [key: string]: string[];
}

interface Appointment {
  id: string;
  patient_name: string;
  patient_age: number;
  patient_gender: string;
  department: string;
  doctor: string;
  date: string;
  time: string;
  status: string;
}

export default function CalendarBooking() {
  const { getToken } = useAuth();
  const [departments, setDepartments] = useState<Department>({});
  const [patientName, setPatientName] = useState<string>("");
  const [patientAge, setPatientAge] = useState<string>("");
  const [patientGender, setPatientGender] = useState<string>("");
  const [selectedDepartment, setSelectedDepartment] = useState<string>("");
  const [selectedDoctor, setSelectedDoctor] = useState<string>("");
  const [selectedDate, setSelectedDate] = useState<string>("");
  const [selectedTime, setSelectedTime] = useState<string>("");
  const [availableSlots, setAvailableSlots] = useState<string[]>([]);
  const [myAppointments, setMyAppointments] = useState<Appointment[]>([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);

  // Fetch departments on mount
  useEffect(() => {
    fetchDepartments();
    fetchMyAppointments();
    
    // Auto-refresh appointments every 5 seconds to catch bookings from chat/voice
    const interval = setInterval(() => {
      fetchMyAppointments();
    }, 5000);
    
    return () => clearInterval(interval);
  }, []);

  // Fetch available slots when department, doctor, or date changes
  useEffect(() => {
    if (selectedDepartment && selectedDoctor && selectedDate) {
      fetchAvailableSlots();
    }
  }, [selectedDepartment, selectedDoctor, selectedDate]);

  const fetchDepartments = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/appointments/departments`);
      const data = await response.json();
      setDepartments(data);
    } catch (error) {
      console.error("Failed to fetch departments:", error);
    }
  };

  const fetchAvailableSlots = async () => {
    try {
      const response = await fetch(
        `${BACKEND_URL}/appointments/slots?date=${selectedDate}&department=${encodeURIComponent(
          selectedDepartment
        )}&doctor=${encodeURIComponent(selectedDoctor)}`
      );
      const data = await response.json();
      setAvailableSlots(data.available_slots || []);
    } catch (error) {
      console.error("Failed to fetch slots:", error);
      setAvailableSlots([]);
    }
  };

  const fetchMyAppointments = async () => {
    try {
      const token = await getToken();
      const response = await fetch(`${BACKEND_URL}/appointments/my`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
        cache: 'no-store', // Prevent caching to always get fresh data
      });
      const data = await response.json();
      setMyAppointments(data.appointments || []);
    } catch (error) {
      console.error("Failed to fetch appointments:", error);
    }
  };

  const handleBookAppointment = async () => {
    if (!patientName || !patientAge || !patientGender || !selectedDepartment || !selectedDoctor || !selectedDate || !selectedTime) {
      setMessage({ type: "error", text: "Please fill in all fields including patient information" });
      return;
    }

    const age = parseInt(patientAge);
    if (isNaN(age) || age < 0 || age > 150) {
      setMessage({ type: "error", text: "Please enter a valid age (0-150)" });
      return;
    }

    setLoading(true);
    setMessage(null);

    try {
      const token = await getToken();
      const response = await fetch(`${BACKEND_URL}/appointments/book`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          patient_name: patientName,
          patient_age: age,
          patient_gender: patientGender,
          department: selectedDepartment,
          doctor: selectedDoctor,
          date: selectedDate,
          time: selectedTime,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        setMessage({ type: "success", text: data.message });
        // Reset form
        setPatientName("");
        setPatientAge("");
        setPatientGender("");
        setSelectedDepartment("");
        setSelectedDoctor("");
        setSelectedDate("");
        setSelectedTime("");
        setAvailableSlots([]);
        // Refresh appointments
        fetchMyAppointments();
      } else {
        setMessage({ type: "error", text: data.detail || "Failed to book appointment" });
      }
    } catch (error) {
      setMessage({ type: "error", text: "Network error. Please try again." });
    } finally {
      setLoading(false);
    }
  };

  const handleCancelAppointment = async (appointmentId: string) => {
    if (!confirm("Are you sure you want to cancel this appointment?")) {
      return;
    }

    try {
      const token = await getToken();
      const response = await fetch(`${BACKEND_URL}/appointments/${appointmentId}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        setMessage({ type: "success", text: "Appointment cancelled successfully" });
        fetchMyAppointments();
      } else {
        const data = await response.json();
        setMessage({ type: "error", text: data.detail || "Failed to cancel appointment" });
      }
    } catch (error) {
      setMessage({ type: "error", text: "Network error. Please try again." });
    }
  };

  // Get minimum date (today)
  const today = new Date().toISOString().split("T")[0];

  return (
    <div className="space-y-8">
      {/* Booking Form */}
      <div className="bg-white rounded-2xl p-8 border border-gray-100 shadow-sm">
        <h3 className="text-2xl font-bold text-gray-900 mb-6">Book an Appointment</h3>

        {message && (
          <div
            className={`mb-6 p-4 rounded-lg ${
              message.type === "success"
                ? "bg-green-50 border border-green-200 text-green-700"
                : "bg-red-50 border border-red-200 text-red-700"
            }`}
          >
            {message.text}
          </div>
        )}

        <div className="grid md:grid-cols-2 gap-6">
          {/* Patient Name */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">Patient Name</label>
            <input
              type="text"
              value={patientName}
              onChange={(e) => setPatientName(e.target.value)}
              placeholder="Enter patient's full name"
              className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Patient Age */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">Age</label>
            <input
              type="number"
              value={patientAge}
              onChange={(e) => setPatientAge(e.target.value)}
              placeholder="Enter age"
              min="0"
              max="150"
              className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Patient Gender */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">Gender</label>
            <select
              value={patientGender}
              onChange={(e) => setPatientGender(e.target.value)}
              className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Select Gender</option>
              <option value="Male">Male</option>
              <option value="Female">Female</option>
              <option value="Other">Other</option>
            </select>
          </div>

          {/* Department Selection */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">Department</label>
            <select
              value={selectedDepartment}
              onChange={(e) => {
                setSelectedDepartment(e.target.value);
                setSelectedDoctor("");
                setSelectedTime("");
              }}
              className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Select Department</option>
              {Object.keys(departments).map((dept) => (
                <option key={dept} value={dept}>
                  {dept}
                </option>
              ))}
            </select>
          </div>

          {/* Doctor Selection */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">Doctor</label>
            <select
              value={selectedDoctor}
              onChange={(e) => {
                setSelectedDoctor(e.target.value);
                setSelectedTime("");
              }}
              disabled={!selectedDepartment}
              className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-50 disabled:cursor-not-allowed"
            >
              <option value="">Select Doctor</option>
              {selectedDepartment &&
                departments[selectedDepartment]?.map((doctor) => (
                  <option key={doctor} value={doctor}>
                    {doctor}
                  </option>
                ))}
            </select>
          </div>

          {/* Date Selection */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">Date</label>
            <input
              type="date"
              value={selectedDate}
              onChange={(e) => {
                setSelectedDate(e.target.value);
                setSelectedTime("");
              }}
              min={today}
              disabled={!selectedDoctor}
              className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-50 disabled:cursor-not-allowed"
            />
          </div>

          {/* Time Selection */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Time {availableSlots.length > 0 && `(${availableSlots.length} slots available)`}
            </label>
            <select
              value={selectedTime}
              onChange={(e) => setSelectedTime(e.target.value)}
              disabled={!selectedDate || availableSlots.length === 0}
              className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-50 disabled:cursor-not-allowed"
            >
              <option value="">Select Time</option>
              {availableSlots.map((slot) => (
                <option key={slot} value={slot}>
                  {slot}
                </option>
              ))}
            </select>
          </div>
        </div>

        <button
          onClick={handleBookAppointment}
          disabled={loading || !selectedTime}
          className="mt-6 w-full bg-blue-600 text-white font-semibold py-4 px-6 rounded-xl hover:bg-blue-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-blue-600/20"
        >
          {loading ? "Booking..." : "Book Appointment"}
        </button>
      </div>

      {/* My Appointments */}
      <div className="bg-white rounded-2xl p-8 border border-gray-100 shadow-sm">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-2xl font-bold text-gray-900">My Appointments</h3>
          <button
            onClick={fetchMyAppointments}
            className="px-4 py-2 text-sm font-medium text-blue-600 hover:bg-blue-50 rounded-lg transition-colors flex items-center gap-2"
          >
            <span>🔄</span>
            Refresh
          </button>
        </div>

        {myAppointments.length === 0 ? (
          <p className="text-gray-500 text-center py-8">No appointments booked yet</p>
        ) : (
          <div className="space-y-4">
            {myAppointments.map((apt) => (
              <div
                key={apt.id}
                className="flex items-center justify-between p-6 border border-gray-200 rounded-xl hover:border-blue-200 transition-colors"
              >
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <span className="text-lg font-bold text-gray-900">{apt.patient_name}</span>
                    <span className="text-sm text-gray-500">•</span>
                    <span className="text-sm text-gray-600">{apt.patient_age} yrs, {apt.patient_gender}</span>
                  </div>
                  <div className="flex items-center gap-3 mb-2">
                    <span className="font-medium text-blue-600">{apt.department}</span>
                    <span className="text-sm text-gray-500">•</span>
                    <span className="text-sm text-gray-600">{apt.doctor}</span>
                  </div>
                  <div className="flex items-center gap-4 text-sm text-gray-500">
                    <span className="flex items-center gap-2">
                      📅 {new Date(apt.date).toLocaleDateString("en-US", { 
                        weekday: "short", 
                        month: "short", 
                        day: "numeric" 
                      })}
                    </span>
                    <span className="flex items-center gap-2">
                      🕒 {apt.time}
                    </span>
                    <span className="px-3 py-1 bg-green-50 text-green-700 rounded-full text-xs font-medium">
                      {apt.status}
                    </span>
                  </div>
                </div>
                <button
                  onClick={() => handleCancelAppointment(apt.id)}
                  className="px-4 py-2 text-sm font-medium text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                >
                  Cancel
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
