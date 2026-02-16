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

async function fetchAPI<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${BACKEND_API_URL}${endpoint}`;
  
  const response = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: response.statusText }));
    throw new APIError(response.status, errorData.detail || errorData.message || "API request failed");
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
