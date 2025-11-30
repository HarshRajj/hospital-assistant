"use client";

import { useUser } from "@clerk/nextjs";
import { useRouter, usePathname } from "next/navigation";
import { useEffect } from "react";

// List of doctor emails - should match backend config
const DOCTOR_EMAILS = [
  "harsh.raj.cseiot.2022@miet.ac.in",
];

export function isUserDoctor(email: string | undefined): boolean {
  if (!email) return false;
  return DOCTOR_EMAILS.includes(email.toLowerCase());
}

export default function DoctorRedirect() {
  const { user, isLoaded } = useUser();
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    if (!isLoaded) return;

    const email = user?.primaryEmailAddress?.emailAddress;
    
    // If user is a doctor and on home page, redirect to doctor dashboard
    if (isUserDoctor(email) && pathname === "/") {
      router.push("/doctor");
    }
  }, [user, isLoaded, pathname, router]);

  return null; // This component doesn't render anything
}
