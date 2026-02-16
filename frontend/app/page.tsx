"use client";

import { useState } from "react";
import { StoryInput } from "@/components/story-input";
import {
  StoryOutput,
  GenreDisplay,
  CharactersDisplay,
  ScoreDisplay,
} from "@/components/story-output";
import { api, APIError } from "@/lib/api";
import { toast } from "sonner";

export default function Home() {
  const [loading, setLoading] = useState(false);
  const [storyResult, setStoryResult] = useState<{
    continuation?: string;
    genre?: string;
    characters?: string[];
    score?: number;
  } | null>(null);
  const [genreResult, setGenreResult] = useState<{
    genre: string;
    confidence: number;
    allProbabilities?: Record<string, number>;
  } | null>(null);
  const [twistResult, setTwistResult] = useState<{
    twist: string;
    twistType: string;
    fullStory: string;
  } | null>(null);
  const [scoreResult, setScoreResult] = useState<{
    totalScore: number;
    breakdown?: Record<string, number>;
    metrics?: Record<string, number>;
  } | null>(null);
  const [charactersResult, setCharactersResult] = useState<string[] | null>(null);

  const handleContinue = async (story: string, genre?: string) => {
    setLoading(true);
    setStoryResult(null);
    setGenreResult(null);
    setTwistResult(null);
    setScoreResult(null);
    setCharactersResult(null);

    try {
      const result = await api.continueStory({ story, genre });
      setStoryResult({
        continuation: result.continuation,
        genre: result.detected_genre,
        characters: result.characters,
        score: result.score,
      });
      toast.success("Story continuation generated successfully!");
    } catch (error) {
      const message = error instanceof APIError ? error.message : "Failed to continue story";
      toast.error(message);
      console.error("Error continuing story:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleDetectGenre = async (story: string) => {
    setLoading(true);
    setGenreResult(null);

    try {
      const result = await api.detectGenre({ text: story });
      setGenreResult({
        genre: result.genre,
        confidence: result.confidence,
        allProbabilities: result.all_probabilities,
      });
      toast.success("Genre detected successfully!");
    } catch (error) {
      const message = error instanceof APIError ? error.message : "Failed to detect genre";
      toast.error(message);
      console.error("Error detecting genre:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateTwist = async (story: string, twistType?: string) => {
    setLoading(true);
    setTwistResult(null);

    try {
      const result = await api.generateTwist({
        text: story,
        twist_type: twistType as any,
      });
      setTwistResult({
        twist: result.twist,
        twistType: result.twist_type,
        fullStory: result.full_story_with_twist,
      });
      toast.success("Plot twist generated successfully!");
    } catch (error) {
      const message = error instanceof APIError ? error.message : "Failed to generate twist";
      toast.error(message);
      console.error("Error generating twist:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleScoreStory = async (story: string) => {
    setLoading(true);
    setScoreResult(null);

    try {
      const result = await api.scoreStory({ text: story });
      setScoreResult({
        totalScore: result.total_score,
        breakdown: result.breakdown,
        metrics: result.metrics,
      });
      toast.success("Story scored successfully!");
    } catch (error) {
      const message = error instanceof APIError ? error.message : "Failed to score story";
      toast.error(message);
      console.error("Error scoring story:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleExtractCharacters = async (story: string) => {
    setLoading(true);
    setCharactersResult(null);

    try {
      const result = await api.extractCharacters({ text: story });
      setCharactersResult(result.characters);
      toast.success(`Extracted ${result.count} character(s) successfully!`);
    } catch (error) {
      const message = error instanceof APIError ? error.message : "Failed to extract characters";
      toast.error(message);
      console.error("Error extracting characters:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        <div className="mb-8 text-center">
          <h1 className="text-4xl font-bold tracking-tight mb-2">PlotCraft-AI</h1>
          <p className="text-muted-foreground text-lg">
            AI-powered story generation and analysis platform
          </p>
        </div>

        <div className="space-y-6">
          <StoryInput
            onContinue={handleContinue}
            onDetectGenre={handleDetectGenre}
            onGenerateTwist={handleGenerateTwist}
            onScoreStory={handleScoreStory}
            onExtractCharacters={handleExtractCharacters}
            loading={loading}
          />

          {storyResult && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <StoryOutput title="Story Continuation" description="AI-generated continuation">
                <div className="space-y-4">
                  <div className="prose prose-sm max-w-none dark:prose-invert">
                    <p className="whitespace-pre-wrap text-sm">{storyResult.continuation}</p>
                  </div>
                  {storyResult.genre && (
                    <div>
                      <p className="text-sm font-medium mb-2">Detected Genre:</p>
                      <GenreDisplay
                        genre={storyResult.genre}
                        confidence={1}
                      />
                    </div>
                  )}
                  {storyResult.characters && storyResult.characters.length > 0 && (
                    <div>
                      <p className="text-sm font-medium mb-2">Characters Found:</p>
                      <CharactersDisplay characters={storyResult.characters} />
                    </div>
                  )}
                  {storyResult.score !== undefined && (
                    <div>
                      <p className="text-sm font-medium mb-2">Story Score:</p>
                      <ScoreDisplay totalScore={storyResult.score} />
                    </div>
                  )}
                </div>
              </StoryOutput>
            </div>
          )}

          {genreResult && (
            <StoryOutput title="Genre Detection" description="Detected genre with confidence scores">
              <GenreDisplay
                genre={genreResult.genre}
                confidence={genreResult.confidence}
                allProbabilities={genreResult.allProbabilities}
              />
            </StoryOutput>
          )}

          {twistResult && (
            <StoryOutput title="Plot Twist" description={`${twistResult.twistType} twist generated`}>
              <div className="space-y-4">
                <div>
                  <p className="text-sm font-medium mb-2">Twist:</p>
                  <p className="text-sm whitespace-pre-wrap">{twistResult.twist}</p>
                </div>
                <div>
                  <p className="text-sm font-medium mb-2">Full Story with Twist:</p>
                  <p className="text-sm whitespace-pre-wrap">{twistResult.fullStory}</p>
                </div>
              </div>
            </StoryOutput>
          )}

          {scoreResult && (
            <StoryOutput title="Story Score" description="Detailed scoring breakdown">
              <ScoreDisplay
                totalScore={scoreResult.totalScore}
                breakdown={scoreResult.breakdown}
                metrics={scoreResult.metrics}
              />
            </StoryOutput>
          )}

          {charactersResult && (
            <StoryOutput title="Characters" description="Extracted character names">
              <CharactersDisplay characters={charactersResult} />
            </StoryOutput>
          )}
        </div>
      </div>
    </div>
  );
}
