import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { signIn } from "next-auth/react"
import { InputOTP, InputOTPGroup, InputOTPSlot, InputOTPSeparator } from "@/components/ui/input-otp"
import { REGEXP_ONLY_DIGITS_AND_CHARS } from "input-otp"
import React from "react"
import { toast } from "sonner"
import { useRouter } from "next/navigation"
import { BACKEND_API_URL } from "@/lib/config"

export function SignUpForm({
  className,
  ...props
}: React.ComponentProps<"form">) {
  const [step, setStep] = useState<'email' | 'otp'>("email")
  const [email, setEmail] = useState("")
  const [otp, setOtp] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const [resendCooldown, setResendCooldown] = useState(0)
  const RESEND_SECONDS = 30
  const router = useRouter()

  // Cooldown timer for resend OTP
  React.useEffect(() => {
    if (resendCooldown > 0) {
      const timer = setTimeout(() => setResendCooldown(resendCooldown - 1), 1000)
      return () => clearTimeout(timer)
    }
  }, [resendCooldown])

  const handleEmailSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setError("")
    setLoading(true)
    try {
      // Check if user exists
      const checkRes = await fetch(`http://localhost:8000/users/check?email=${encodeURIComponent(email)}`)
      const checkData = await checkRes.json()
      if (checkData.exists) {
        toast.error("An account with this email already exists. Please log in to continue.")
        setTimeout(() => router.push("/login"), 1200)
        return
      }
      const res = await fetch("http://localhost:8000/send-otp", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email }),
      })
      if (!res.ok) {
        throw new Error("Failed to send OTP")
      }
      
      const data = await res.json()
      console.log("OTP sent:", data) // Debug log
      
      setStep("otp")
    } catch (err) {
      setError("Failed to send OTP. Please try again.")
    } finally {
      setLoading(false)
    }
  }

  const handleResendOtp = async () => {
    setError("")
    setLoading(true)
    try {
      const res = await fetch("http://localhost:8000/send-otp", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email }),
      })
      if (!res.ok) {
        throw new Error("Failed to resend OTP")
      }
      setResendCooldown(RESEND_SECONDS)
    } catch (err) {
      setError("Failed to resend OTP. Please try again.")
    } finally {
      setLoading(false)
    }
  }

  const handleOtpSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setError("")
    setLoading(true)
    
    try {
      const response = await fetch(`${BACKEND_API_URL}/verify-otp`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, otp }),
      })
      
      const data = await response.json()
      
      if (!response.ok) {
        throw new Error(data.detail || "Invalid OTP")
      }
      
      if (data.exists) {
        // User already exists, redirect to login
        toast.error("An account with this email already exists. Please log in to continue.")
        setTimeout(() => router.push("/login"), 1200)
      } else {
        // New user, redirect to onboarding
        toast.success("OTP verified!", { description: "Let's complete your profile 🎯" })
        localStorage.setItem("email", email)
        setTimeout(() => router.push("/onboarding"), 1200)
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Invalid OTP. Please try again."
      setError(errorMessage)
      console.error("OTP verification error:", err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <form
      className={"flex flex-col gap-6 " + (className || "") + " w-full"}
      {...props}
      onSubmit={step === "email" ? handleEmailSubmit : handleOtpSubmit}
    >
      <div className="flex flex-col items-center text-center mb-2 mt-1">
        <h1 className="text-3xl font-light font-sans mb-2">{step === "email" ? "Login In" : "Enter OTP"}</h1>
      </div>
      <div className="grid gap-4">
        {step === "email" ? (
          <>
            <div className="grid gap-2">
              <div className="flex items-center justify-between">
                <Label htmlFor="email" className="text-sm font-medium">Email</Label>
                <button
                  type="button"
                  onClick={() => router.push("/login")}
                  className="inline-block px-3 py-0.5 border border-primary/30 rounded-md text-primary font-medium bg-background hover:bg-primary hover:text-white transition-colors duration-200 shadow-sm hover:shadow-md focus:outline-none focus:ring-2 focus:ring-primary/40 focus:ring-offset-2 text-xs ml-2"
                  style={{ lineHeight: '1.5' }}
                >
                  Already have an account?
                </button>
              </div>
              <div className="relative">
                <Input id="email" type="email" placeholder="Email" required className="pr-10" value={email} onChange={e => setEmail(e.target.value)} />
                {/* Password manager icon (optional, right side) */}
                <span className="absolute right-2 top-1/2 -translate-y-1/2 text-muted-foreground">
                  <svg width="20" height="20" fill="currentColor" viewBox="0 0 20 20"><rect x="2" y="5" width="16" height="10" rx="2" fill="#e5e7eb"/><circle cx="10" cy="10" r="2" fill="#9ca3af"/></svg>
                </span>
              </div>
            </div>
            <p className="text-xs text-muted-foreground text-left mb-1">
              By continuing, you agree to the <a href="#" className="underline">Self Service PSS</a> and <a href="#" className="underline">Privacy Policy</a>.
            </p>
            <Button type="submit" className="w-full bg-primary hover:bg-primary/80 text-primary-foreground text-base font-semibold py-2 rounded-md shadow-md mt-1" disabled={loading}>
              {loading ? "Sending..." : "Continue"}
            </Button>
            <div className="flex items-center gap-2 my-1">
              <div className="flex-1 border-t border-[var(--border)]" />
              <span className="text-xs text-muted-foreground">OR</span>
              <div className="flex-1 border-t border-[var(--border)]" />
            </div>
            <Button variant="outline" className="w-full flex items-center gap-2 py-2 text-base font-medium">
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12"/></svg>
              Continue with GitHub
            </Button>
            <Button variant="outline" className="w-full flex items-center gap-2 py-2 text-base font-medium" onClick={(e) => { e.preventDefault(); signIn('google'); }}>
              <svg className="w-5 h-5" viewBox="0 0 48 48"><g><path fill="#4285F4" d="M24 9.5c3.54 0 6.71 1.22 9.2 3.6l6.86-6.86C36.68 2.7 30.8 0 24 0 14.82 0 6.73 5.8 2.69 14.09l7.98 6.19C12.36 13.13 17.68 9.5 24 9.5z"/><path fill="#34A853" d="M46.1 24.55c0-1.64-.15-3.22-.42-4.74H24v9.01h12.42c-.54 2.9-2.18 5.36-4.65 7.02l7.19 5.59C43.98 37.13 46.1 31.3 46.1 24.55z"/><path fill="#FBBC05" d="M10.67 28.18a14.5 14.5 0 0 1 0-8.36l-7.98-6.19A24.01 24.01 0 0 0 0 24c0 3.91.94 7.61 2.69 10.91l7.98-6.19z"/><path fill="#EA4335" d="M24 48c6.48 0 11.93-2.15 15.9-5.85l-7.19-5.59c-2.01 1.35-4.59 2.16-8.71 2.16-6.32 0-11.64-3.63-13.33-8.77l-7.98 6.19C6.73 42.2 14.82 48 24 48z"/></g></svg>
              Continue with Google
            </Button>
            <Button variant="outline" className="w-full flex items-center gap-2 py-2 text-base font-medium">
              <svg className="w-5 h-5" viewBox="0 0 24 24"><path fill="#F25022" d="M6.305 17.842l-2.447 2.447A11.953 11.953 0 0 0 12 24c2.62 0 5.037-.84 7.042-2.258l-2.447-2.447z"/><path fill="#7FBA00" d="M17.842 17.695l2.447 2.447A11.953 11.953 0 0 0 24 12c0-2.62-.84-5.037-2.258-7.042l-2.447 2.447z"/><path fill="#00A4EF" d="M6.305 6.158l-2.447-2.447A11.953 11.953 0 0 0 0 12c0 2.62.84 5.037 2.258 7.042l2.447-2.447z"/><path fill="#FFB900" d="M17.842 6.305l2.447-2.447A11.953 11.953 0 0 0 12 0C9.38 0 6.963.84 4.958 2.258l2.447 2.447z"/></svg>
              Continue with Microsoft
            </Button>
          </>
        ) : (
          <>
            <div className="grid gap-2">
              <h2 className="text-xl font-semibold text-center">Verify your email</h2>
              <p className="text-sm text-muted-foreground text-center mb-2">
                We've sent a 6-digit code to <span className="font-medium text-primary">{email}</span>.<br />
                Please enter it below to continue.
              </p>
              {/* Temporary OTP display for testing - remove in production */}
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 text-center">
                <p className="text-xs text-yellow-800 font-mono">
                  🧪 Test Mode: Check console for OTP
                </p>
              </div>
              <InputOTP
                maxLength={6}
                value={otp}
                onChange={setOtp}
                pattern={REGEXP_ONLY_DIGITS_AND_CHARS}
                containerClassName="justify-center"
              >
                <InputOTPGroup>
                  <InputOTPSlot index={0} />
                  <InputOTPSlot index={1} />
                  <InputOTPSlot index={2} />
                  <InputOTPSlot index={3} />
                  <InputOTPSlot index={4} />
                  <InputOTPSlot index={5} />
                </InputOTPGroup>
              </InputOTP>
              <div className="flex flex-col items-center mt-2">
                <Button
                  type="button"
                  variant="ghost"
                  className="text-xs px-2 py-1 h-auto mb-1"
                  onClick={handleResendOtp}
                  disabled={resendCooldown > 0 || loading}
                >
                  {resendCooldown > 0 ? `Resend OTP in ${resendCooldown}s` : "Resend OTP"}
                </Button>
                <span className="text-xs text-muted-foreground text-center">
                  Didn't receive the code? Check your spam folder or <br /> click resend above.
                </span>
              </div>
            </div>
            <Button type="submit" className="w-full bg-primary hover:bg-primary/80 text-primary-foreground text-base font-semibold py-2 rounded-md shadow-md mt-1" disabled={loading || otp.length !== 6}>
              {loading ? "Verifying..." : "Verify OTP"}
            </Button>
            <Button type="button" variant="outline" className="w-full mt-2" onClick={() => setStep('email')}>
              Back
            </Button>
          </>
        )}
        {error && <p className="text-red-500 text-xs mt-1">{error}</p>}
      </div>
    </form>
  )
}
