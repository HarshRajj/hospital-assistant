"use client";

import { useState, useEffect } from "react";
import { useAuth } from "@clerk/nextjs";
import { SignedIn, SignedOut, SignUpButton } from "@clerk/nextjs";
import Link from "next/link";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

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

export default function AppointmentsPage() {
  const { getToken } = useAuth();
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);

  useEffect(() => {
    fetchAppointments();
  }, []);

  const fetchAppointments = async () => {
    try {
      const token = await getToken();
      if (!token) {
        setLoading(false);
        return;
      }

      const response = await fetch(`${BACKEND_URL}/appointments/my`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setAppointments(data.appointments || []);
      }
    } catch (error) {
      console.error("Failed to fetch appointments:", error);
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
        fetchAppointments();
      } else {
        const data = await response.json();
        setMessage({ type: "error", text: data.detail || "Failed to cancel appointment" });
      }
    } catch (error) {
      setMessage({ type: "error", text: "Network error. Please try again." });
    }
  };

  // Separate upcoming and past appointments
  const now = new Date();
  const upcomingAppointments = appointments.filter(apt => {
    const aptDate = new Date(`${apt.date}T${apt.time}`);
    return aptDate >= now && apt.status !== "expired";
  });
  const pastAppointments = appointments.filter(apt => {
    const aptDate = new Date(`${apt.date}T${apt.time}`);
    return aptDate < now || apt.status === "expired";
  });

  return (
    <div className="min-h-screen bg-gray-50/50">
      <main className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Breadcrumb */}
        <nav className="mb-8">
          <ol className="flex items-center gap-2 text-sm text-gray-500">
            <li>
              <Link href="/" className="hover:text-blue-600 transition-colors">
                Home
              </Link>
            </li>
            <li>
              <span className="mx-2">/</span>
            </li>
            <li className="text-gray-900 font-medium">My Appointments</li>
          </ol>
        </nav>

        {/* Page Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">My Appointments</h1>
            <p className="text-gray-500">View and manage your scheduled appointments</p>
          </div>
          <Link
            href="/book"
            className="px-6 py-3 bg-blue-600 text-white font-semibold rounded-xl hover:bg-blue-700 transition-all shadow-lg shadow-blue-600/20 flex items-center gap-2"
          >
            <span>+</span>
            Book New
          </Link>
        </div>

        <SignedIn>
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

          {loading ? (
            <div className="bg-white rounded-2xl p-12 text-center border border-gray-100">
              <div className="animate-spin w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full mx-auto mb-4"></div>
              <p className="text-gray-500">Loading appointments...</p>
            </div>
          ) : appointments.length === 0 ? (
            <div className="bg-white rounded-2xl p-12 text-center border border-gray-100">
              <div className="inline-flex items-center justify-center w-20 h-20 bg-blue-50 rounded-full mb-6">
                <div className="text-4xl">📅</div>
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-3">No Appointments Yet</h2>
              <p className="text-gray-500 mb-8">You haven't booked any appointments. Schedule your first visit today!</p>
              <Link
                href="/book"
                className="inline-flex px-8 py-4 bg-blue-600 text-white font-semibold rounded-xl hover:bg-blue-700 transition-all shadow-lg shadow-blue-600/20"
              >
                Book Your First Appointment
              </Link>
            </div>
          ) : (
            <div className="space-y-8">
              {/* Upcoming Appointments */}
              {upcomingAppointments.length > 0 && (
                <div className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm">
                  <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                    <span className="w-3 h-3 bg-green-500 rounded-full"></span>
                    Upcoming Appointments ({upcomingAppointments.length})
                  </h2>
                  <div className="space-y-4">
                    {upcomingAppointments.map((apt) => (
                      <div
                        key={apt.id}
                        className="flex items-center justify-between p-5 border border-gray-200 rounded-xl hover:border-blue-200 transition-colors"
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
                            <span className="flex items-center gap-2">🕒 {apt.time}</span>
                            <span className="px-3 py-1 rounded-full text-xs font-medium bg-green-50 text-green-700">
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
                </div>
              )}

              {/* Past Appointments */}
              {pastAppointments.length > 0 && (
                <div className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm">
                  <h2 className="text-xl font-bold text-gray-500 mb-4 flex items-center gap-2">
                    <span className="w-3 h-3 bg-gray-400 rounded-full"></span>
                    Past Appointments ({pastAppointments.length})
                  </h2>
                  <div className="space-y-4">
                    {pastAppointments.map((apt) => (
                      <div
                        key={apt.id}
                        className="flex items-center justify-between p-5 border border-gray-200 rounded-xl bg-gray-50 opacity-75"
                      >
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-2">
                            <span className="text-lg font-bold text-gray-500">{apt.patient_name}</span>
                            <span className="text-sm text-gray-400">•</span>
                            <span className="text-sm text-gray-500">{apt.patient_age} yrs, {apt.patient_gender}</span>
                          </div>
                          <div className="flex items-center gap-3 mb-2">
                            <span className="font-medium text-gray-500">{apt.department}</span>
                            <span className="text-sm text-gray-400">•</span>
                            <span className="text-sm text-gray-500">{apt.doctor}</span>
                          </div>
                          <div className="flex items-center gap-4 text-sm text-gray-400">
                            <span className="flex items-center gap-2">
                              📅 {new Date(apt.date).toLocaleDateString("en-US", {
                                weekday: "short",
                                month: "short",
                                day: "numeric"
                              })}
                            </span>
                            <span className="flex items-center gap-2">🕒 {apt.time}</span>
                            <span className="px-3 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-500">
                              {apt.status}
                            </span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </SignedIn>

        <SignedOut>
          <div className="bg-white rounded-2xl p-12 text-center border border-gray-100 shadow-sm">
            <div className="inline-flex items-center justify-center w-20 h-20 bg-blue-50 rounded-full mb-6">
              <div className="text-4xl">🔒</div>
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-3">Sign In Required</h2>
            <p className="text-gray-500 text-sm leading-relaxed max-w-md mx-auto mb-8">
              Please sign in to view your appointments.
            </p>
            <SignUpButton mode="modal">
              <button className="px-8 py-4 text-base font-semibold text-white bg-blue-600 rounded-xl hover:bg-blue-700 shadow-lg shadow-blue-600/20 transition-all hover:scale-105">
                Sign In
              </button>
            </SignUpButton>
          </div>
        </SignedOut>
      </main>
    </div>
  );
}
