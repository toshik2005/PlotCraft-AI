// Use relative path to hit Next.js rewrites (proxied to backend) - avoids CORS
export const BACKEND_API_URL = typeof window !== "undefined" ? "" : (process.env.BACKEND_API_URL || "http://localhost:8000");

export const API_CONFIG = {
  ENDPOINTS: {
    LOGOUT: "/api/logout",
    // Add other endpoints as needed
  },
  getUrl: (endpoint: string) => `${BACKEND_API_URL}${endpoint}`,
};
