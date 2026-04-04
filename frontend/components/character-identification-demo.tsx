/**
 * Character Identification Demo Component
 * 
 * Example React component demonstrating how to use the new
 * character identification API endpoints.
 * 
 * Features:
 * - Single text analysis
 * - Batch processing
 * - Error handling
 * - Loading states
 */

"use client";

import { useState } from "react";
import { api, IdentifyCharacterResponse } from "@/lib/api";

/** User-facing label for extraction backend (no vendor names). */
function formatExtractionMethod(method: string | undefined): string {
  switch (method) {
    case "llm":
      return "Advanced model";
    case "spacy":
      return "Classic NLP";
    case "regex":
      return "Pattern-based";
    default:
      return method ?? "—";
  }
}

interface CharacterResult {
  text: string;
  characters: string[];
  method: string;
  loading: boolean;
  error: string | null;
}

export function CharacterIdentificationDemo() {
  const [inputText, setInputText] = useState("");
  const [maxCharacters, setMaxCharacters] = useState(5);
  const [result, setResult] = useState<IdentifyCharacterResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleIdentifyCharacters = async () => {
    if (!inputText.trim()) {
      setError("Please enter some text");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await api.identifyCharacters({
        text: inputText,
        max_characters: maxCharacters,
      });

      if (response.success) {
        setResult(response);
      } else {
        setError("Failed to identify characters");
      }
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to identify characters"
      );
    } finally {
      setLoading(false);
    }
  };

  const handleBatchIdentify = async () => {
    // Example: Split input by double newline and process in batch
    const texts = inputText.split("\n\n").filter((t) => t.trim());

    if (texts.length === 0) {
      setError("Please enter some text");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await api.batchIdentifyCharacters(
        texts.map((text) => ({
          text,
          max_characters: maxCharacters,
        }))
      );

      console.log("Batch identification results:", response);
      setError(null);
      // Handle batch results as needed
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Batch identification failed"
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <h2 className="text-2xl font-bold mb-4">Character Identification API</h2>

      {/* Input Section */}
      <div className="mb-4">
        <label className="block text-sm font-medium mb-2">Story Text</label>
        <textarea
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder="Enter story text to identify characters..."
          className="w-full h-32 p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {/* Max Characters Control */}
      <div className="mb-4">
        <label className="block text-sm font-medium mb-2">
          Max Characters: {maxCharacters}
        </label>
        <input
          type="range"
          min="1"
          max="20"
          value={maxCharacters}
          onChange={(e) => setMaxCharacters(Number(e.target.value))}
          className="w-full"
        />
      </div>

      {/* Action Buttons */}
      <div className="flex gap-2 mb-4">
        <button
          onClick={handleIdentifyCharacters}
          disabled={loading || !inputText.trim()}
          className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-300"
        >
          {loading ? "Processing..." : "Identify Characters"}
        </button>

        <button
          onClick={handleBatchIdentify}
          disabled={loading || !inputText.trim()}
          className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 disabled:bg-gray-300"
        >
          {loading ? "Processing..." : "Batch Identify"}
        </button>
      </div>

      {/* Error Display */}
      {error && (
        <div className="p-4 bg-red-100 text-red-700 rounded-lg mb-4">
          {error}
        </div>
      )}

      {/* Results Display */}
      {result && (
        <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
          <h3 className="font-bold text-lg mb-2">Identified Characters</h3>
          <div className="bg-white p-3 rounded border border-gray-200 mb-3">
            <div className="grid grid-cols-2 gap-2">
              <div>
                <strong>Count:</strong> {result.count}
              </div>
              <div>
                <strong>Method:</strong> {formatExtractionMethod(result.method)}
              </div>
            </div>
          </div>

          <div className="mb-3">
            <strong>Characters Found:</strong>
            <div className="flex flex-wrap gap-2 mt-2">
              {result.characters.map((char, idx) => (
                <span
                  key={idx}
                  className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm"
                >
                  {char}
                </span>
              ))}
            </div>
          </div>

          {result.message && (
            <div className="text-sm text-gray-600">
              <strong>Message:</strong> {result.message}
            </div>
          )}
        </div>
      )}

      {/* Usage Examples */}
      <div className="mt-8 p-4 bg-gray-50 rounded-lg">
        <h4 className="font-bold mb-2">API Usage Examples</h4>

        <details className="mb-3">
          <summary className="cursor-pointer font-medium">
            Single Character Identification
          </summary>
          <pre className="mt-2 p-3 bg-gray-800 text-gray-100 text-xs rounded overflow-x-auto">
{`const response = await api.identifyCharacters({
  text: "Alice met Bob in the forest",
  max_characters: 5
});

// Response:
{
  "success": true,
  "characters": ["Alice", "Bob"],
  "count": 2,
  "method": "spacy"
}`}
          </pre>
        </details>

        <details className="mb-3">
          <summary className="cursor-pointer font-medium">
            Batch Character Identification
          </summary>
          <pre className="mt-2 p-3 bg-gray-800 text-gray-100 text-xs rounded overflow-x-auto">
{`const response = await api.batchIdentifyCharacters([
  {
    text: "Alice met Bob",
    max_characters: 5
  },
  {
    text: "Charlie and Diana",
    max_characters: 5
  }
]);

// Response:
{
  "total_requests": 2,
  "successful": 2,
  "failed": 0,
  "results": [...]
}`}
          </pre>
        </details>

        <details>
          <summary className="cursor-pointer font-medium">
            Error Handling
          </summary>
          <pre className="mt-2 p-3 bg-gray-800 text-gray-100 text-xs rounded overflow-x-auto">
{`try {
  const response = await api.identifyCharacters({
    text: ""  // Empty text
  });
} catch (error) {
  // Handles 400 Bad Request
  console.error(error.message);
}`}
          </pre>
        </details>
      </div>
    </div>
  );
}

export default CharacterIdentificationDemo;
