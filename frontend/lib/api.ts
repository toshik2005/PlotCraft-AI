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

export interface GenreDetectRequest {
  text: string;
}

export interface GenreDetectResponse {
  genre: string;
  confidence: number;
  all_probabilities: Record<string, number>;
}

export interface TwistGenerateRequest {
  text: string;
  twist_type?: "unexpected" | "reversal" | "revelation" | "betrayal" | "discovery";
}

export interface TwistGenerateResponse {
  twist: string;
  twist_type: string;
  full_story_with_twist: string;
  prompt_used: string;
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
  options: RequestInit = {}
): Promise<T> {
  const base = BACKEND_API_URL || "";
  const url = base ? `${base}${endpoint}` : endpoint;

  let response: Response;
  try {
    response = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
    });
  } catch (err) {
    const msg = err instanceof Error ? err.message : "Network error";
    throw new APIError(
      0,
      msg.includes("fetch") || msg.includes("Failed to fetch")
        ? "Could not reach backend. Is it running on port 8000?"
        : msg
    );
  }

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    const message = parseErrorMessage(errorData, response.statusText || "API request failed");
    throw new APIError(response.status, message);
  }

  return response.json();
}

export const api = {
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

  // Plot twist generation
  async generateTwist(request: TwistGenerateRequest): Promise<TwistGenerateResponse> {
    const response = await fetchAPI<APIResponse<TwistGenerateResponse>>(
      "/api/v1/twist/generate",
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
