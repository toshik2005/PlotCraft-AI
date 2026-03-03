// Base URL for backend API, available on both server and client.
// Configure in `.env.local` as:
// NEXT_PUBLIC_BACKEND_API_URL=http://localhost:8000
export const BACKEND_API_URL =
  process.env.NEXT_PUBLIC_BACKEND_API_URL || "http://localhost:8000";

export const API_CONFIG = {
  ENDPOINTS: {
    LOGOUT: "/api/logout",
    // Add other endpoints as needed
  },
  getUrl: (endpoint: string) => `${BACKEND_API_URL}${endpoint}`,
};
