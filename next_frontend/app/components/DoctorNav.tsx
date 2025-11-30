"use client";

import { useUser } from "@clerk/nextjs";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { isUserDoctor } from "./DoctorRedirect";

export default function DoctorNav() {
  const { user } = useUser();
  const pathname = usePathname();
  
  // Check if user is a doctor
  const email = user?.primaryEmailAddress?.emailAddress;
  const isDoctor = isUserDoctor(email);
  
  if (!isDoctor) return null;
  
  const isDoctorPage = pathname === "/doctor";
  
  return (
    <div className="flex items-center gap-2">
      {isDoctorPage && (
        <Link
          href="/"
          className="px-4 py-2 text-sm font-medium rounded-lg text-gray-700 hover:bg-gray-100 transition-colors"
        >
          🏠 Home
        </Link>
      )}
      <Link
        href="/doctor"
        className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
          isDoctorPage
            ? "bg-blue-600 text-white"
            : "text-gray-700 hover:bg-gray-100"
        }`}
      >
        📊 Doctor Dashboard
      </Link>
    </div>
  );
}
