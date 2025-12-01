"use client";

import { useEffect, useState } from "react";
import { useAuth, useUser } from "@clerk/nextjs";
import { useRouter } from "next/navigation";
import { isUserDoctor } from "../components/DoctorRedirect";

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

export default function DoctorDashboard() {
  const { getToken } = useAuth();
  const { user } = useUser();
  const router = useRouter();
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"today" | "all" | "past">("today");
  
  const [todayAppointments, setTodayAppointments] = useState<Appointment[]>([]);
  const [allAppointments, setAllAppointments] = useState<Appointment[]>([]);
  const [pastWeekAppointments, setPastWeekAppointments] = useState<Appointment[]>([]);

  useEffect(() => {
    checkDoctorAccess();
  }, [user]);

  const checkDoctorAccess = async () => {
    if (!user) return;
    
    const email = user.primaryEmailAddress?.emailAddress;
    
    // Check if user is a doctor using the shared function
    if (!isUserDoctor(email)) {
      setError("Access Denied. Doctor credentials required.");
      setLoading(false);
      // Don't redirect immediately, show error message
      return;
    }

    // Fetch all appointment data
    await Promise.all([
      fetchTodayAppointments(),
      fetchAllAppointments(),
      fetchPastWeekAppointments(),
    ]);
    
    setLoading(false);
  };

  const fetchTodayAppointments = async () => {
    try {
      console.log("📅 Fetching today's appointments for doctor...");
      const token = await getToken();
      const email = user?.primaryEmailAddress?.emailAddress || "";
      const response = await fetch(`${BACKEND_URL}/appointments/doctor/today`, {
        headers: { 
          Authorization: `Bearer ${token}`,
          "X-User-Email": email
        },
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        console.error("❌ Failed to fetch today's appointments:", response.status, errorData);
        throw new Error("Failed to fetch today's appointments");
      }
      
      const data = await response.json();
      console.log("✅ Today's appointments received:", data.appointments?.length || 0, data);
      setTodayAppointments(data.appointments || []);
    } catch (err) {
      console.error("Error fetching today's appointments:", err);
    }
  };

  const fetchAllAppointments = async () => {
    try {
      console.log("📅 Fetching all appointments for doctor...");
      const token = await getToken();
      const email = user?.primaryEmailAddress?.emailAddress || "";
      const response = await fetch(`${BACKEND_URL}/appointments/doctor/all`, {
        headers: { 
          Authorization: `Bearer ${token}`,
          "X-User-Email": email
        },
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        console.error("❌ Failed to fetch all appointments:", response.status, errorData);
        throw new Error("Failed to fetch all appointments");
      }
      
      const data = await response.json();
      console.log("✅ All appointments received:", data.appointments?.length || 0, data);
      setAllAppointments(data.appointments || []);
    } catch (err) {
      console.error("Error fetching all appointments:", err);
    }
  };

  const fetchPastWeekAppointments = async () => {
    try {
      console.log("📅 Fetching past week appointments for doctor...");
      const token = await getToken();
      const email = user?.primaryEmailAddress?.emailAddress || "";
      const response = await fetch(`${BACKEND_URL}/appointments/doctor/past-week`, {
        headers: { 
          Authorization: `Bearer ${token}`,
          "X-User-Email": email
        },
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        console.error("❌ Failed to fetch past week appointments:", response.status, errorData);
        throw new Error("Failed to fetch past week appointments");
      }
      
      const data = await response.json();
      console.log("✅ Past week appointments received:", data.appointments?.length || 0, data);
      setPastWeekAppointments(data.appointments || []);
    } catch (err) {
      console.error("Error fetching past week appointments:", err);
    }
  };

  const refreshData = async () => {
    setLoading(true);
    await Promise.all([
      fetchTodayAppointments(),
      fetchAllAppointments(),
      fetchPastWeekAppointments(),
    ]);
    setLoading(false);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p className="mt-4 text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-white rounded-2xl p-8 shadow-lg max-w-md text-center">
          <div className="text-6xl mb-4">🚫</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Access Denied</h2>
          <p className="text-gray-600 mb-6">{error}</p>
          <p className="text-sm text-gray-500 mb-4">
            This page is only accessible to authorized doctors.
          </p>
          <button
            onClick={() => router.push("/")}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Return to Home
          </button>
        </div>
      </div>
    );
  }

  const currentAppointments = 
    activeTab === "today" ? todayAppointments :
    activeTab === "all" ? allAppointments :
    pastWeekAppointments;

  return (
    <div className="min-h-screen bg-gray-50/50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Doctor Dashboard</h1>
              <p className="text-gray-600 mt-1">Welcome, {user?.firstName || "Doctor"}</p>
            </div>
            <button
              onClick={refreshData}
              className="px-4 py-2 text-sm font-medium text-blue-600 hover:bg-blue-50 rounded-lg transition-colors flex items-center gap-2"
            >
              <span>🔄</span>
              Refresh
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Cards */}
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          <StatCard
            title="Today's Appointments"
            count={todayAppointments.length}
            icon="📅"
            color="blue"
          />
          <StatCard
            title="Upcoming Appointments"
            count={allAppointments.length}
            icon="📋"
            color="green"
          />
          <StatCard
            title="Past Week"
            count={pastWeekAppointments.length}
            icon="📊"
            color="purple"
          />
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
          <div className="border-b border-gray-200">
            <div className="flex gap-8 px-8 pt-6">
              <TabButton
                active={activeTab === "today"}
                onClick={() => setActiveTab("today")}
                label="Today's Appointments"
                count={todayAppointments.length}
              />
              <TabButton
                active={activeTab === "all"}
                onClick={() => setActiveTab("all")}
                label="All Upcoming"
                count={allAppointments.length}
              />
              <TabButton
                active={activeTab === "past"}
                onClick={() => setActiveTab("past")}
                label="Past Week"
                count={pastWeekAppointments.length}
              />
            </div>
          </div>

          {/* Appointments List */}
          <div className="p-8">
            {currentAppointments.length === 0 ? (
              <div className="text-center py-12">
                <div className="text-6xl mb-4">📭</div>
                <p className="text-gray-500 text-lg">No appointments found</p>
              </div>
            ) : (
              <div className="space-y-4">
                {currentAppointments.map((apt) => (
                  <AppointmentCard key={apt.id} appointment={apt} />
                ))}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

function StatCard({ title, count, icon, color }: { title: string; count: number; icon: string; color: string }) {
  const colorClasses = {
    blue: "bg-blue-50 text-blue-600 border-blue-100",
    green: "bg-green-50 text-green-600 border-green-100",
    purple: "bg-purple-50 text-purple-600 border-purple-100",
  };

  return (
    <div className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-3xl font-bold text-gray-900 mt-2">{count}</p>
        </div>
        <div className={`w-14 h-14 rounded-xl flex items-center justify-center text-2xl ${colorClasses[color as keyof typeof colorClasses]}`}>
          {icon}
        </div>
      </div>
    </div>
  );
}

function TabButton({ active, onClick, label, count }: { active: boolean; onClick: () => void; label: string; count: number }) {
  return (
    <button
      onClick={onClick}
      className={`pb-4 px-1 font-medium text-sm transition-colors relative ${
        active
          ? "text-blue-600"
          : "text-gray-500 hover:text-gray-700"
      }`}
    >
      {label} ({count})
      {active && (
        <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-blue-600"></div>
      )}
    </button>
  );
}

function AppointmentCard({ appointment }: { appointment: Appointment }) {
  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString("en-US", {
      weekday: "short",
      month: "short",
      day: "numeric",
      year: "numeric",
    });
  };

  const isExpired = appointment.status === "expired";

  return (
    <div className={`flex items-center justify-between p-6 border rounded-xl transition-all ${
      isExpired 
        ? "border-gray-200 bg-gray-50 opacity-75" 
        : "border-gray-200 hover:border-blue-200 hover:bg-blue-50/30"
    }`}>
      <div className="flex-1">
        <div className="flex items-center gap-4 mb-3">
          <h3 className={`text-lg font-bold ${isExpired ? "text-gray-500" : "text-gray-900"}`}>
            {appointment.patient_name}
          </h3>
          <span className={`px-3 py-1 rounded-full text-xs font-medium ${
            isExpired ? "bg-gray-100 text-gray-500" : "bg-blue-50 text-blue-700"
          }`}>
            {appointment.patient_age} yrs
          </span>
          <span className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-xs font-medium">
            {appointment.patient_gender}
          </span>
          <span className={`px-3 py-1 rounded-full text-xs font-medium ${
            isExpired 
              ? "bg-gray-200 text-gray-500" 
              : "bg-green-50 text-green-700"
          }`}>
            {appointment.status}
          </span>
        </div>
        
        <div className="flex items-center gap-6 text-sm text-gray-600">
          <div className="flex items-center gap-2">
            <span className="font-medium text-gray-900">📅</span>
            {formatDate(appointment.date)}
          </div>
          <div className="flex items-center gap-2">
            <span className="font-medium text-gray-900">🕒</span>
            {appointment.time}
          </div>
          <div className="flex items-center gap-2">
            <span className="font-medium text-gray-900">🏥</span>
            {appointment.department}
          </div>
        </div>
      </div>
      
      <div className="flex items-center gap-3">
        <div className="text-right mr-4">
          <div className="text-xs text-gray-500">Appointment ID</div>
          <div className="text-sm font-mono text-gray-700">{appointment.id}</div>
        </div>
        <div className={`w-2 h-2 rounded-full ${isExpired ? "bg-gray-400" : "bg-green-500"}`}></div>
      </div>
    </div>
  );
}
