import { BACKEND_API_URL } from "./config";

export interface StoryContinueRequest {
  story: string;
  genre?: string;
}

export interface StoryContinueResponse {
  detected_genre: string;
  characters: string[];
  continuation: string;
  score: number;
}

export interface GenerateStoryRequest {
  user_id: string;
  story: string;
  genre?: string;
  twist?: string;
  refine?: boolean;
  measure?: boolean;
  temperature?: number;
  max_tokens?: number;
}

export interface GenerateStoryResponse {
  genre: string;
  detected_characters: string[];
  persisted_characters: string[];
  twist_applied?: string | null;
  generated_text: string;
  refined: boolean;
  score?: number | null;
  character_focus_required: boolean;
}

export interface GenreDetectRequest {
  text: string;
}

export interface GenreDetectResponse {
  genre: string;
  confidence: number;
  all_probabilities: Record<string, number>;
}

export interface ScoreStoryRequest {
  text: string;
}

export interface ScoreStoryResponse {
  total_score: number;
  breakdown: Record<string, number>;
  metrics: Record<string, number>;
}

export interface ExtractCharactersRequest {
  text: string;
  user_id?: string;
}

export interface ExtractCharactersResponse {
  characters: string[];
  count: number;
}

export interface APIResponse<T> {
  success: boolean;
  message: string;
  data: T;
  errors?: string[];
}

class APIError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = "APIError";
  }
}

function parseErrorMessage(errorData: unknown, fallback: string): string {
  if (!errorData || typeof errorData !== "object") return fallback;
  const d = errorData as Record<string, unknown>;
  if (typeof d.message === "string") return d.message;
  if (typeof d.detail === "string") return d.detail;
  // FastAPI 422 validation errors: detail is array of { msg, loc, ... }
  if (Array.isArray(d.detail) && d.detail.length > 0) {
    const first = d.detail[0] as { msg?: string; loc?: unknown[] };
    return typeof first.msg === "string" ? first.msg : JSON.stringify(first);
  }
  return fallback;
}

async function fetchAPI<T>(
  endpoint: string,
  options: RequestInit = {},
  timeoutMs?: number
): Promise<T> {
  // Build full URL using backend base; allows browser to talk directly
  // to the FastAPI backend without relying on Next.js dev proxy.
  const isAbsolute = endpoint.startsWith("http://") || endpoint.startsWith("https://");
  const url = isAbsolute ? endpoint : `${BACKEND_API_URL}${endpoint}`;

  const computedTimeoutMs =
    timeoutMs ?? (endpoint.includes("/story/") ? 300000 : 60000); // 5 min for story generation, 60s otherwise

  // Create abort controller for timeout (ML operations can take a while)
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), computedTimeoutMs);

  let response: Response;
  try {
    response = await fetch(url, {
      ...options,
      signal: controller.signal,
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
    });
  } catch (err) {
    clearTimeout(timeoutId);
    const msg = err instanceof Error ? err.message : "Network error";
    throw new APIError(
      0,
      msg.includes("fetch") || msg.includes("Failed to fetch")
        ? "Could not reach backend. Is it running on port 8000?"
        : msg.includes("abort")
          ? "Request timeout: Backend is taking too long to respond"
          : msg
    );
  }

  clearTimeout(timeoutId);

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    const message = parseErrorMessage(errorData, response.statusText || "API request failed");
    throw new APIError(response.status, message);
  }

  return response.json();
}

export const api = {
  // New story generation pipeline (character persistence, twist, refinement, scoring)
  async generateStory(request: GenerateStoryRequest): Promise<GenerateStoryResponse> {
    const response = await fetchAPI<GenerateStoryResponse>(
      "/api/v1/story/generate",
      {
        method: "POST",
        body: JSON.stringify(request),
      },
      300000
    );
    return response;
  },

  // Story continuation (full pipeline)
  async continueStory(request: StoryContinueRequest): Promise<StoryContinueResponse> {
    // This endpoint returns StoryResponse directly (not wrapped in APIResponse)
    const response = await fetchAPI<StoryContinueResponse>(
      "/api/v1/story/continue",
      {
        method: "POST",
        body: JSON.stringify(request),
      }
    );
    return response;
  },

  // Genre detection
  async detectGenre(request: GenreDetectRequest): Promise<GenreDetectResponse> {
    const response = await fetchAPI<APIResponse<GenreDetectResponse>>(
      "/api/v1/genre/detect",
      {
        method: "POST",
        body: JSON.stringify(request),
      }
    );
    return response.data;
  },

  // Story scoring
  async scoreStory(request: ScoreStoryRequest): Promise<ScoreStoryResponse> {
    const response = await fetchAPI<APIResponse<ScoreStoryResponse>>(
      "/api/v1/score/story",
      {
        method: "POST",
        body: JSON.stringify(request),
      }
    );
    return response.data;
  },

  // Character extraction
  async extractCharacters(request: ExtractCharactersRequest): Promise<ExtractCharactersResponse> {
    const response = await fetchAPI<APIResponse<ExtractCharactersResponse>>(
      "/api/v1/score/characters",
      {
        method: "POST",
        body: JSON.stringify(request),
      }
    );
    return response.data;
  },
};

export { APIError };
