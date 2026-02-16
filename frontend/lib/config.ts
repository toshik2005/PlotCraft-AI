export const BACKEND_API_URL = process.env.BACKEND_API_URL || "http://localhost:8000";

export const API_CONFIG = {
  ENDPOINTS: {
    LOGOUT: "/api/logout",
    // Add other endpoints as needed
  },
  getUrl: (endpoint: string) => `${BACKEND_API_URL}${endpoint}`,
};
