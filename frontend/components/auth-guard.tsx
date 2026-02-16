"use client"

import { useSession } from "next-auth/react"
import { useRouter, usePathname } from "next/navigation"
import { useEffect } from "react"

export function AuthGuard({ children }: { children: React.ReactNode }) {
  const { data: session, status } = useSession()
  const router = useRouter()
  const pathname = usePathname()

  useEffect(() => {
    if (status === "loading") return // Still loading

    // If onboarding just completed, redirect immediately without waiting for session refresh
    try {
      const onboardingComplete = typeof window !== "undefined" && localStorage.getItem("onboardingComplete") === "1"
      if (onboardingComplete) {
        if (pathname !== "/dashboard") {
          console.log("onboardingComplete flag detected. Redirecting to /dashboard")
          router.replace("/dashboard")
          return
        }
        // When on dashboard, keep the flag until session confirms onboarding is complete
        if (status === "authenticated" && session?.user && session.user.needsOnboarding === false) {
          localStorage.removeItem("onboardingComplete")
        }
        // While the flag exists, do not run further redirects based on session
        return
      }
    } catch (_err) {
      // ignore localStorage access errors
    }

    if (status === "authenticated" && session?.user) {
      // User is logged in
      if (session.user.needsOnboarding && pathname !== "/onboarding") {
        // User needs onboarding, redirect to onboarding page
        console.log("User needs onboarding, redirecting to /onboarding")
        localStorage.setItem("email", session.user.email || "")
        router.push("/onboarding")
        return
      }
      
      if (!session.user.needsOnboarding && pathname === "/onboarding") {
        // User has completed onboarding, redirect to dashboard
        console.log("User has completed onboarding, redirecting to /dashboard")
        router.replace("/dashboard")
        return
      }
    }
  }, [session, status, router, pathname])

  // Show loading while checking session
  if (status === "loading") {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
      </div>
    )
  }

  return <>{children}</>
}
