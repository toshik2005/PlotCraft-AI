"use client";

import { useMemo, useState, useEffect } from "react";
import { MainNavbar, Phase } from "@/components/main-navbar";
import { WriterView } from "@/components/writer-view";
import { PreviewView } from "@/components/preview-view";
import { ReaderView } from "@/components/reader-view";
import { api, APIError } from "@/lib/api";
import { toast } from "sonner";
import { AnimatePresence } from "framer-motion";

export default function Home() {
  const [phase, setPhase] = useState<Phase>("writer");
  const [loading, setLoading] = useState(false);
  const [currentStory, setCurrentStory] = useState<string>("");
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
  const [scoreResult, setScoreResult] = useState<{
    totalScore: number;
    breakdown?: Record<string, number>;
    metrics?: Record<string, number>;
  } | null>(null);
  const [charactersResult, setCharactersResult] = useState<string[] | null>(null);

  const [showPreview, setShowPreview] = useState(false);
  const [showReader, setShowReader] = useState(false);

  // Initialize theme on mount
  useEffect(() => {
    const theme = localStorage.getItem("theme") || "dark";
    document.documentElement.classList.toggle("dark", theme === "dark");
  }, []);

  const handleContinue = async (story: string, genre?: string) => {
    setCurrentStory(story);
    setLoading(true);
    try {
      const result = await api.continueStory({ story, genre });
      setStoryResult({
        continuation: result.continuation,
        genre: result.detected_genre,
        characters: result.characters,
        score: result.score,
      });
      // Populate analysis sidebar from continue pipeline
      setGenreResult({
        genre: result.detected_genre,
        confidence: 0.8,
        allProbabilities: { [result.detected_genre]: 0.8 },
      });
      setScoreResult({
        totalScore: result.score,
        breakdown: {},
        metrics: {},
      });
      setCharactersResult(result.characters);
      toast.success("AI Continuation Ready!");
      setShowPreview(true); // Open preview modal automatically
    } catch (error) {
      const message = error instanceof APIError ? error.message : "Failed to continue story";
      toast.error(message);
    } finally {
      setLoading(false);
    }
  };

  const handleDetectGenre = async (story: string) => {
    setCurrentStory(story);
    setLoading(true);
    try {
      const result = await api.detectGenre({ text: story });
      setGenreResult({
        genre: result.genre,
        confidence: result.confidence,
        allProbabilities: result.all_probabilities,
      });
      toast.success("Genre profile updated.");
    } catch (error) {
      const message = error instanceof APIError ? error.message : "Failed to detect genre";
      toast.error(message);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateTwist = async (story: string, twistType?: string) => {
    setCurrentStory(story);
    setLoading(true);
    try {
      const result = await api.generateTwist({
        text: story,
        twist_type: twistType as any,
      });
      // Integrate twist directly for now
      setCurrentStory(result.full_story_with_twist);
      toast.success("Twist integrated into manuscript.");
    } catch (error) {
      const message = error instanceof APIError ? error.message : "Failed to generate twist";
      toast.error(message);
    } finally {
      setLoading(false);
    }
  };

  const handleScoreStory = async (story: string) => {
    setCurrentStory(story);
    setLoading(true);
    try {
      const result = await api.scoreStory({ text: story });
      setScoreResult({
        totalScore: result.total_score,
        breakdown: result.breakdown,
        metrics: result.metrics,
      });
      toast.success("Story analysis complete.");
    } catch (error) {
      const message = error instanceof APIError ? error.message : "Failed to score story";
      toast.error(message);
    } finally {
      setLoading(false);
    }
  };

  const handleExtractCharacters = async (story: string) => {
    setCurrentStory(story);
    setLoading(true);
    try {
      const result = await api.extractCharacters({ text: story });
      setCharactersResult(result.characters);
      toast.success(`Cast of ${result.count} characters identified.`);
    } catch (error) {
      const message = error instanceof APIError ? error.message : "Failed to extract characters";
      toast.error(message);
    } finally {
      setLoading(false);
    }
  };

  const fullStory = useMemo(() => {
    return `${currentStory}\n\n${storyResult?.continuation || ""}`.trim();
  }, [currentStory, storyResult?.continuation]);

  return (
    <div className="min-h-screen bg-background text-foreground selection:bg-primary/30 selection:text-primary-foreground overflow-x-hidden transition-colors duration-500">
      {/* Background gradients - optimized with pulse for depth */}
      <div className="fixed inset-0 pointer-events-none -z-10 overflow-hidden">
        <div className="absolute top-[-20%] left-[-10%] w-[60%] h-[60%] bg-primary/5 blur-[120px] rounded-full animate-pulse will-change-transform" style={{ animationDuration: '8s' }} />
        <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] bg-blue-500/5 blur-[120px] rounded-full animate-pulse will-change-transform" style={{ animationDuration: '12s' }} />
      </div>

      <MainNavbar
        currentPhase={phase}
        onPhaseChange={(p) => {
          if (p === "reader") {
            if (!currentStory.trim()) {
              toast.error("Write something first!");
              return;
            }
            setPhase("reader");
          } else {
            setPhase("writer");
          }
        }}
        isGenerating={loading}
      />

      <main className="relative z-10">
        <AnimatePresence mode="wait">
          {phase === "writer" && (
            <WriterView
              key="writer"
              currentStory={currentStory}
              onStoryChange={setCurrentStory}
              onContinue={handleContinue}
              onDetectGenre={handleDetectGenre}
              onGenerateTwist={handleGenerateTwist}
              onScoreStory={handleScoreStory}
              onExtractCharacters={handleExtractCharacters}
              loading={loading}
            />
          )}

          {phase === "reader" && (
            <ReaderView
              key="reader"
              fullStory={fullStory}
              onClose={() => setPhase("writer")}
            />
          )}
        </AnimatePresence>
      </main>

      <AnimatePresence>
        {showPreview && (
          <PreviewView
            currentStory={currentStory}
            storyResult={storyResult}
            genreResult={genreResult}
            scoreResult={scoreResult}
            charactersResult={charactersResult}
            onClose={() => setShowPreview(false)}
            onPublish={() => {
              setShowPreview(false);
              setPhase("reader");
            }}
          />
        )}
      </AnimatePresence>

      <footer className="py-8 text-center text-[10px] text-muted-foreground/30 font-mono tracking-widest uppercase">
        PlotCraft AI &bull; Interactive Narrative Studio &bull; 2026
      </footer>
    </div>
  );
}
