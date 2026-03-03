"use client";

import { useMemo, useState, useEffect } from "react";
import { MainNavbar, Phase } from "@/components/main-navbar";
import { WriterView } from "@/components/writer-view";
import { PreviewView } from "@/components/preview-view";
import { ReaderView } from "@/components/reader-view";
import { CharactersModal, GenreModal, ScoreModal } from "@/components/analysis-modal";
import { ContinueModal } from "@/components/continue-modal";
import { api, APIError } from "@/lib/api";
import { toast } from "sonner";
import { AnimatePresence } from "framer-motion";

export default function Home() {
  const [phase, setPhase] = useState<Phase>("writer");
  const [loading, setLoading] = useState(false);
  const [userId, setUserId] = useState<string>("");
  const [currentStory, setCurrentStory] = useState<string>("");
  const [selectedGenre, setSelectedGenre] = useState<"Auto" | "Sci-Fi" | "Horror" | "Action">("Auto");
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
  const [showGenreModal, setShowGenreModal] = useState(false);
  const [showScoreModal, setShowScoreModal] = useState(false);
  const [showCharactersModal, setShowCharactersModal] = useState(false);
  const [showContinueModal, setShowContinueModal] = useState(false);

  // Initialize theme on mount
  useEffect(() => {
    const theme = localStorage.getItem("theme") || "dark";
    document.documentElement.classList.toggle("dark", theme === "dark");
  }, []);

  // Stable user id for session character persistence (used by backend memory)
  useEffect(() => {
    try {
      const key = "plotcraft_user_id";
      let id = localStorage.getItem(key) || "";
      if (!id) {
        id =
          typeof crypto !== "undefined" && "randomUUID" in crypto
            ? crypto.randomUUID()
            : `${Date.now()}-${Math.random().toString(16).slice(2)}`;
        localStorage.setItem(key, id);
      }
      setUserId(id);
    } catch {
      // If storage is blocked, fall back to a runtime-only id
      const id = `${Date.now()}-${Math.random().toString(16).slice(2)}`;
      setUserId(id);
    }
  }, []);

  const normalizeGenre = (g?: string) => {
    if (!g) return undefined;
    const trimmed = g.trim();
    if (!trimmed) return undefined;
    if (trimmed.toLowerCase() === "sci-fi" || trimmed.toLowerCase() === "sci fi") return "scifi";
    return trimmed.toLowerCase();
  };

  const handleContinue = async (story: string, genre?: string) => {
    const trimmed = story.trim();
    // If we already have a continuation for this exact story, ask whether to read or create new
    if (storyResult?.continuation && trimmed && trimmed === currentStory.trim()) {
      setShowContinueModal(true);
      return;
    }

    setCurrentStory(story);
    await generateContinuation(story, genre);
  };

  const generateContinuation = async (story: string, genre?: string) => {
    setLoading(true);
    try {
      let effectiveGenre = normalizeGenre(genre);
      if (!effectiveGenre) {
        const detected = await api.detectGenre({ text: story });
        effectiveGenre = detected.genre;
        setGenreResult({
          genre: detected.genre,
          confidence: detected.confidence,
          allProbabilities: detected.all_probabilities,
        });
      }

      const result = await api.generateStory({
        user_id: userId || "anonymous",
        story,
        genre: effectiveGenre || "scfi",
        refine: false,
        measure: true,
        temperature: 0.8,
        max_tokens: 200,
      });

      setStoryResult({
        continuation: result.generated_text,
        genre: result.genre,
        characters: result.persisted_characters,
        score: typeof result.score === "number" ? result.score : undefined,
      });

      setGenreResult((prev) => prev ?? {
        genre: result.genre,
        confidence: 0.8,
        allProbabilities: { [result.genre]: 0.8 },
      });

      if (typeof result.score === "number") {
        setScoreResult({
          totalScore: result.score,
          breakdown: {},
          metrics: {},
        });
      }

      setCharactersResult(result.persisted_characters);
      toast.success("AI Continuation Ready!");
      setShowPreview(true);
    } catch (error) {
      const message = error instanceof APIError ? error.message : "Failed to continue story";
      toast.error(message);
    } finally {
      setLoading(false);
    }
  };

  const handleScoreStory = async (story: string) => {
    setCurrentStory(story);
    setLoading(true);
    try {
      const score = await api.scoreStory({ text: story });
      setScoreResult({
        totalScore: score.total_score,
        breakdown: score.breakdown,
        metrics: score.metrics,
      });

      setShowScoreModal(true);
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
      const result = await api.extractCharacters({ text: story, user_id: userId || undefined });
      setCharactersResult(result.characters);
      toast.success(`Cast of ${result.count} characters identified.`);
      setShowCharactersModal(true);
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
      setShowGenreModal(true);
      toast.success("Genre profile updated.");
    } catch (error) {
      const message = error instanceof APIError ? error.message : "Failed to detect genre";
      toast.error(message);
    } finally {
      setLoading(false);
    }
  };

  const hasGenerated = !!storyResult?.continuation;

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
            if (!hasGenerated) {
              toast.error("Generate a story first!");
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
              onScoreStory={handleScoreStory}
              onExtractCharacters={handleExtractCharacters}
              loading={loading}
              selectedGenre={selectedGenre}
              onGenreChange={setSelectedGenre}
              analysisEnabled={hasGenerated}
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
        {showGenreModal && (
          <GenreModal
            genreResult={genreResult}
            onClose={() => setShowGenreModal(false)}
          />
        )}
        {showScoreModal && (
          <ScoreModal
            scoreResult={scoreResult}
            onClose={() => setShowScoreModal(false)}
          />
        )}
        {showCharactersModal && (
          <CharactersModal
            characters={charactersResult}
            onClose={() => setShowCharactersModal(false)}
          />
        )}
        {showContinueModal && (
          <ContinueModal
            onReadExisting={() => {
              setShowContinueModal(false);
              setPhase("reader");
            }}
            onCreateNew={() => {
              // Reset to a fresh manuscript (no continuation, no analysis)
              setShowContinueModal(false);
              setCurrentStory("");
              setStoryResult(null);
              setGenreResult(null);
              setScoreResult(null);
              setCharactersResult(null);
              setSelectedGenre("Auto");
              setPhase("writer");
            }}
            onClose={() => setShowContinueModal(false)}
          />
        )}
      </AnimatePresence>

      <footer className="py-8 text-center text-[10px] text-muted-foreground/30 font-mono tracking-widest uppercase">
        PlotCraft AI &bull; Interactive Narrative Studio &bull; 2026
      </footer>
    </div>
  );
}
