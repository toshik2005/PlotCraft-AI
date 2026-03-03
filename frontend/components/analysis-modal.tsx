"use client";

import { motion } from "framer-motion";
import { CharactersDisplay, GenreDisplay, ScoreDisplay } from "./story-output";
import { Button } from "./ui/button";
import { X } from "lucide-react";

interface GenreModalProps {
  genreResult: { genre: string; confidence: number; allProbabilities?: Record<string, number> } | null;
  onClose: () => void;
}

interface ScoreModalProps {
  scoreResult: { totalScore: number; breakdown?: Record<string, number>; metrics?: Record<string, number> } | null;
  onClose: () => void;
}

interface CharactersModalProps {
  characters: string[] | null;
  onClose: () => void;
}

export function GenreModal({ genreResult, onClose }: GenreModalProps) {
  if (!genreResult) return null;

  return (
    <div className="fixed inset-0 z-[120] flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={onClose}
        className="absolute inset-0 bg-background/80 backdrop-blur-md"
      />

      <motion.div
        initial={{ opacity: 0, scale: 0.9, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.9, y: 20 }}
        className="relative w-full max-w-md glass rounded-3xl shadow-2xl max-h-[80vh] overflow-y-auto"
      >
        <div className="flex items-center justify-between px-6 py-4 border-b bg-muted/30 rounded-t-3xl">
          <div>
            <h3 className="text-sm font-bold uppercase tracking-widest text-muted-foreground">
              Genre Detection
            </h3>
            <p className="text-xs text-muted-foreground/70">
              Detected genre and confidence profile
            </p>
          </div>
          <Button
            variant="ghost"
            size="icon"
            onClick={onClose}
            className="rounded-full h-8 w-8"
          >
            <X className="w-4 h-4" />
          </Button>
        </div>

        <div className="p-6 space-y-4">
          <GenreDisplay
            genre={genreResult.genre}
            confidence={genreResult.confidence}
            allProbabilities={genreResult.allProbabilities}
          />
        </div>
      </motion.div>
    </div>
  );
}

export function ScoreModal({ scoreResult, onClose }: ScoreModalProps) {
  if (!scoreResult) return null;

  return (
    <div className="fixed inset-0 z-[120] flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={onClose}
        className="absolute inset-0 bg-background/80 backdrop-blur-md"
      />

      <motion.div
        initial={{ opacity: 0, scale: 0.9, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.9, y: 20 }}
        className="relative w-full max-w-md glass rounded-3xl shadow-2xl max-h-[80vh] overflow-y-auto"
      >
        <div className="flex items-center justify-between px-6 py-4 border-b bg-muted/30 rounded-t-3xl">
          <div>
            <h3 className="text-sm font-bold uppercase tracking-widest text-muted-foreground">
              Story Score
            </h3>
            <p className="text-xs text-muted-foreground/70">
              Overall quality score and breakdown
            </p>
          </div>
          <Button
            variant="ghost"
            size="icon"
            onClick={onClose}
            className="rounded-full h-8 w-8"
          >
            <X className="w-4 h-4" />
          </Button>
        </div>

        <div className="p-6 space-y-4">
          <ScoreDisplay
            totalScore={scoreResult.totalScore}
            breakdown={scoreResult.breakdown}
            metrics={scoreResult.metrics}
          />
        </div>
      </motion.div>
    </div>
  );
}

export function CharactersModal({ characters, onClose }: CharactersModalProps) {
  if (!characters) return null;

  return (
    <div className="fixed inset-0 z-[120] flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={onClose}
        className="absolute inset-0 bg-background/80 backdrop-blur-md"
      />

      <motion.div
        initial={{ opacity: 0, scale: 0.9, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.9, y: 20 }}
        className="relative w-full max-w-md glass rounded-3xl shadow-2xl max-h-[80vh] overflow-y-auto"
      >
        <div className="flex items-center justify-between px-6 py-4 border-b bg-muted/30 rounded-t-3xl">
          <div>
            <h3 className="text-sm font-bold uppercase tracking-widest text-muted-foreground">
              Cast
            </h3>
            <p className="text-xs text-muted-foreground/70">
              Characters identified in your prompt
            </p>
          </div>
          <Button
            variant="ghost"
            size="icon"
            onClick={onClose}
            className="rounded-full h-8 w-8"
          >
            <X className="w-4 h-4" />
          </Button>
        </div>

        <div className="p-6 space-y-4">
          <CharactersDisplay characters={characters} />
        </div>
      </motion.div>
    </div>
  );
}

