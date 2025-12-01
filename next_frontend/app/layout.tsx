import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import {
  ClerkProvider,
  SignInButton,
  SignUpButton,
  SignedIn,
  SignedOut,
  UserButton,
} from "@clerk/nextjs";
import Link from "next/link";
import DoctorNav from "./components/DoctorNav";
import DoctorRedirect from "./components/DoctorRedirect";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Arogya Med-City | Premium Healthcare",
  description: "Your Health, Our Priority. AI-powered healthcare assistant.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <ClerkProvider>
      <html lang="en">
        <body
          className={`${geistSans.variable} ${geistMono.variable} antialiased`}
        >
          <header className="sticky top-0 z-50 bg-white/95 backdrop-blur-sm border-b border-gray-200 shadow-sm">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
              <div className="flex justify-between items-center">
                {/* Logo */}
                <Link href="/" className="flex items-center gap-3 hover:opacity-80 transition-opacity">
                  <div className="w-10 h-10 bg-blue-600 rounded-xl flex items-center justify-center text-white font-bold text-lg shadow-lg shadow-blue-600/20">
                    A
                  </div>
                  <div>
                    <span className="text-xl font-bold text-gray-900">Arogya Med-City</span>
                    <p className="text-xs text-gray-500 font-medium">Premium Healthcare</p>
                  </div>
                </Link>

                {/* Center - Emergency & Status */}
                <div className="hidden lg:flex items-center gap-6 text-sm">
                  <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-red-50 text-red-600 border border-red-100">
                    <span className="relative flex h-2 w-2">
                      <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
                      <span className="relative inline-flex rounded-full h-2 w-2 bg-red-500"></span>
                    </span>
                    Emergency: 911
                  </div>
                  <div className="flex items-center gap-2 text-green-600 font-medium">
                    <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                    24/7 Available
                  </div>
                </div>

                {/* Right - Navigation & Auth */}
                <div className="flex items-center gap-4">
                  <SignedIn>
                    <Link
                      href="/book"
                      className="hidden sm:flex items-center gap-2 px-4 py-2 text-sm font-medium text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                    >
                      <span>📅</span>
                      Book Appointment
                    </Link>
                    <Link
                      href="/appointments"
                      className="hidden sm:flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-600 hover:bg-gray-50 rounded-lg transition-colors"
                    >
                      <span>📋</span>
                      My Appointments
                    </Link>
                    <DoctorRedirect />
                    <DoctorNav />
                    <UserButton afterSignOutUrl="/" />
                  </SignedIn>
                  <SignedOut>
                    <SignInButton mode="modal">
                      <button className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900">
                        Sign In
                      </button>
                    </SignInButton>
                    <SignUpButton mode="modal">
                      <button className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 shadow-lg shadow-blue-600/20">
                        Sign Up
                      </button>
                    </SignUpButton>
                  </SignedOut>
                </div>
              </div>
            </div>
          </header>
          {children}
        </body>
      </html>
    </ClerkProvider>
  );
}
