"use client";

import { motion } from "framer-motion";
import {
    GenreDisplay,
    CharactersDisplay,
    ScoreDisplay
} from "./story-output";
import { Button } from "./ui/button";
import { ArrowRight, Share2, Printer, X } from "lucide-react";

interface PreviewViewProps {
    currentStory: string;
    storyResult: {
        continuation?: string;
        genre?: string;
        characters?: string[];
        score?: number;
    } | null;
    genreResult: { genre: string; confidence: number; allProbabilities?: Record<string, number> } | null;
    scoreResult: { totalScore: number; breakdown?: Record<string, number>; metrics?: Record<string, number> } | null;
    charactersResult: string[] | null;
    onClose: () => void;
    onPublish: () => void;
}

function getAnalysisData(
    storyResult: PreviewViewProps["storyResult"],
    genreResult: PreviewViewProps["genreResult"],
    scoreResult: PreviewViewProps["scoreResult"],
    charactersResult: PreviewViewProps["charactersResult"]
) {
    return {
        genre: genreResult ?? (storyResult?.genre ? { genre: storyResult.genre, confidence: 0.8 } : null),
        score: scoreResult ?? (storyResult?.score != null ? { totalScore: storyResult.score, metrics: {} } : null),
        characters: charactersResult ?? storyResult?.characters ?? [],
    };
}

export function PreviewView({
    currentStory,
    storyResult,
    genreResult,
    scoreResult,
    charactersResult,
    onClose,
    onPublish,
}: PreviewViewProps) {
    const analysis = getAnalysisData(storyResult, genreResult, scoreResult, charactersResult);
    return (
        <div className="fixed inset-0 z-[110] flex items-center justify-center p-4">
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
                className="relative w-full max-w-5xl glass rounded-3xl shadow-2xl overflow-hidden grid lg:grid-cols-[1fr,320px] max-h-[90vh]"
            >
                {/* Main Content */}
                <div className="flex flex-col h-full min-h-0">
                    <div className="bg-muted/30 p-4 border-b flex items-center justify-between">
                        <span className="text-sm font-medium">Manuscript Preview</span>
                        <div className="flex items-center gap-2">
                            <Button variant="ghost" size="icon" onClick={onClose} className="rounded-full h-8 w-8">
                                <X className="w-4 h-4" />
                            </Button>
                        </div>
                    </div>

                    <div className="flex-1 overflow-y-auto p-8 space-y-8 scrollbar-hide bg-book-paper/30">
                        <div className="space-y-4">
                            <h3 className="text-[10px] font-bold uppercase tracking-[0.2em] text-primary">Original Text</h3>
                            <p className="text-base leading-relaxed font-serif text-ink italic opacity-80 whitespace-pre-wrap">
                                {currentStory}
                            </p>
                        </div>

                        <motion.div
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            className="space-y-4 pt-8 border-t border-primary/10"
                        >
                            <h3 className="text-[10px] font-bold uppercase tracking-[0.2em] text-primary flex items-center gap-2">
                                <ArrowRight className="w-3 h-3" />
                                AI Powered Continuation
                            </h3>
                            {storyResult?.continuation ? (
                                <p className="text-base leading-relaxed font-serif text-ink whitespace-pre-wrap">
                                    {storyResult.continuation}
                                </p>
                            ) : (
                                <p className="text-sm text-muted-foreground italic">No continuation generated yet. Click Continue in the writer view to generate.</p>
                            )}
                        </motion.div>
                    </div>

                    <div className="p-6 border-t bg-muted/20 flex items-center justify-between gap-4">
                        <div className="flex gap-2">
                            <Button variant="outline" size="sm" className="rounded-full"><Share2 className="w-3 h-3 mr-2" /> Share</Button>
                            <Button variant="outline" size="sm" className="rounded-full"><Printer className="w-3 h-3 mr-2" /> Print</Button>
                        </div>
                        <Button size="lg" onClick={onPublish} className="rounded-full px-8 font-bold shadow-lg hover:scale-105 transition-transform">
                            Finalize and Read
                        </Button>
                    </div>
                </div>

                {/* Sidebar Analysis */}
                <div className="flex flex-col h-full min-h-0 bg-muted/10 border-l">
                    <div className="p-6 border-b bg-muted/20 shrink-0">
                        <h3 className="text-sm font-bold uppercase tracking-widest text-muted-foreground">Analysis</h3>
                    </div>
                    <div className="flex-1 overflow-y-auto p-6 space-y-6 scrollbar-hide">
                        {analysis.genre && (
                            <div className="space-y-3">
                                <h4 className="text-[10px] font-bold uppercase tracking-tighter opacity-50">Genre</h4>
                                <GenreDisplay
                                    genre={analysis.genre.genre}
                                    confidence={analysis.genre.confidence}
                                    allProbabilities={analysis.genre.allProbabilities}
                                />
                            </div>
                        )}

                        {analysis.score != null && (
                            <div className="space-y-3">
                                <h4 className="text-[10px] font-bold uppercase tracking-tighter opacity-50">Score</h4>
                                <ScoreDisplay
                                    totalScore={analysis.score.totalScore}
                                    breakdown={analysis.score.breakdown}
                                    metrics={analysis.score.metrics}
                                />
                            </div>
                        )}

                        {analysis.characters.length > 0 && (
                            <div className="space-y-3">
                                <h4 className="text-[10px] font-bold uppercase tracking-tighter opacity-50">Cast</h4>
                                <CharactersDisplay characters={analysis.characters} />
                            </div>
                        )}
                    </div>
                </div>
            </motion.div>
        </div>
    );
}
