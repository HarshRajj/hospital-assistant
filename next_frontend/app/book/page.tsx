"use client";

import CalendarBooking from "../components/CalendarBooking";
import { SignedIn, SignedOut, SignUpButton } from "@clerk/nextjs";
import Link from "next/link";

export default function BookingPage() {
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
            <li className="text-gray-900 font-medium">Book Appointment</li>
          </ol>
        </nav>

        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Book an Appointment</h1>
          <p className="text-gray-500">Schedule your visit with our expert doctors</p>
        </div>

        <SignedIn>
          <CalendarBooking />
        </SignedIn>

        <SignedOut>
          <div className="bg-white rounded-2xl p-12 text-center border border-gray-100 shadow-sm">
            <div className="inline-flex items-center justify-center w-20 h-20 bg-blue-50 rounded-full mb-6">
              <div className="text-4xl">🔒</div>
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-3">Sign In Required</h2>
            <p className="text-gray-500 text-sm leading-relaxed max-w-md mx-auto mb-8">
              Please sign in or create a free account to book appointments with our specialist doctors.
            </p>
            <SignUpButton mode="modal">
              <button className="px-8 py-4 text-base font-semibold text-white bg-blue-600 rounded-xl hover:bg-blue-700 shadow-lg shadow-blue-600/20 transition-all hover:scale-105">
                Sign Up to Book
              </button>
            </SignUpButton>
          </div>
        </SignedOut>
      </main>
    </div>
  );
}
