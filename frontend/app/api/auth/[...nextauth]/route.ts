import NextAuth from "next-auth"
import GoogleProvider from "next-auth/providers/google"
import CredentialsProvider from "next-auth/providers/credentials"
import { BACKEND_API_URL } from "@/lib/config"

const handler = NextAuth({
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    }),
    CredentialsProvider({
      id: "credentials",
      name: "credentials",
      credentials: {
        email: { label: "Email", type: "email" },
        otp: { label: "OTP", type: "text" }
      },
      async authorize(credentials) {
        console.log("[NextAuth] Credentials provider called with:", credentials)
        
        if (!credentials?.email || !credentials?.otp) {
          console.log("[NextAuth] Missing credentials")
          return null
        }

        try {
          console.log("[NextAuth] Verifying OTP with backend...")
          // Verify OTP with backend
          const response = await fetch(`${BACKEND_API_URL}/verify-otp`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              email: credentials.email,
              otp: credentials.otp,
            }),
          })

          const data = await response.json()
          console.log("[NextAuth] OTP verification response:", data)

          if (!response.ok || !data.exists) {
            console.log("[NextAuth] OTP verification failed")
            return null
          }

          console.log("[NextAuth] Getting user profile from backend...")
          // Get user profile from backend
          const userResponse = await fetch(`${BACKEND_API_URL}/users/profile?email=${encodeURIComponent(credentials.email)}`)
          const userData = await userResponse.json()
          console.log("[NextAuth] User profile response:", userData)

          if (userData.success && userData.user) {
            const user = {
              id: userData.user.id,
              email: userData.user.email,
              name: userData.user.name,
              image: userData.user.image,
            }
            console.log("[NextAuth] Returning user:", user)
            return user
          }

          console.log("[NextAuth] User profile fetch failed")
          return null
        } catch (error) {
          console.error("[NextAuth] Credentials authorization error:", error)
          return null
        }
      }
    }),
  ],
  callbacks: {
    async redirect({ url, baseUrl }) {
      // Default redirect to dashboard, but we'll handle onboarding in the session callback
      return "/dashboard";
    },
    async signIn({ user }) {
      console.log("[NextAuth] signIn callback for:", user.email);
      try {
        if (!user.email) {
          console.error("[NextAuth] No email provided by Google. Cannot proceed with sign-in.");
          return false;
        }
        
        // Check if user exists and has a complete profile
        const checkRes = await fetch(`${BACKEND_API_URL}/users/check?email=${encodeURIComponent(user.email)}`);
        const checkData = await checkRes.json();
        
        if (checkData.exists) {
          // User exists, check if they have a complete profile
          if (checkData.user && checkData.user.profile) {
            // User has complete profile
            console.log(`[NextAuth] User has complete profile: ${user.email}.`);
            return true;
          } else {
            // User exists but no profile, needs onboarding
            console.log(`[NextAuth] User exists but no profile: ${user.email}. Needs onboarding.`);
            return true; // Allow sign in, we'll redirect in session callback
          }
        } else {
          // New user, create basic user record
          console.log(`[NextAuth] New user: ${user.email}. Creating user.`);
          
          const res = await fetch(`${BACKEND_API_URL}/users`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              id: user.id,
              name: user.name,
              email: user.email,
              image: user.image,
              provider: "google",
              profile: null, // No profile yet
            }),
          });
          
          if (res.ok) {
            console.log("[NextAuth] User created successfully");
            return true;
          } else {
            console.error("[NextAuth] Failed to create user in backend");
            return false;
          }
        }
      } catch (error) {
        console.error("[NextAuth] Error during Google sign-in process:", error);
        return false;
      }
    },
    async session({ session, token }) {
      console.log("[NextAuth] Session callback called with:", { session, token })
      
      // Add user ID and onboarding status to session
      if (session.user) {
        session.user.id = token.sub;
        console.log("[NextAuth] Session user:", session.user)
        
        // Check if user needs onboarding
        try {
          const checkRes = await fetch(`${BACKEND_API_URL}/users/check?email=${encodeURIComponent(session.user.email!)}`);
          const checkData = await checkRes.json();
          console.log("[NextAuth] User check response:", checkData)
          
          if (checkData.exists && checkData.user) {
            session.user.needsOnboarding = !checkData.user.profile;
            session.user.profile = checkData.user.profile;
          } else {
            session.user.needsOnboarding = true;
          }
        } catch (error) {
          console.error("[NextAuth] Error checking user profile:", error);
          session.user.needsOnboarding = true;
        }
      }
      console.log("[NextAuth] Final session:", session)
      return session;
    },
    async jwt({ token, user }) {
      if (user) {
        token.sub = user.id;
      }
      return token;
    },
  },
  pages: {
    signIn: '/login',
    error: '/login',
  },
})

export { handler as GET, handler as POST } 