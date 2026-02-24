"use client";

import { motion } from "framer-motion";
import { StoryInput } from "./story-input";

interface WriterViewProps {
    currentStory: string;
    onStoryChange: (story: string) => void;
    onContinue: (story: string, genre?: string) => void;
    onDetectGenre: (story: string) => void;
    onGenerateTwist: (story: string, twistType?: string) => void;
    onScoreStory: (story: string) => void;
    onExtractCharacters: (story: string) => void;
    loading: boolean;
}

export function WriterView({
    currentStory,
    onStoryChange,
    onContinue,
    onDetectGenre,
    onGenerateTwist,
    onScoreStory,
    onExtractCharacters,
    loading,
}: WriterViewProps) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="max-w-4xl mx-auto w-full pt-24 pb-12"
        >
            <div className="space-y-8">
                <div className="text-center space-y-2">
                    <h2 className="text-4xl font-serif font-bold tracking-tight">The Scriptum</h2>
                    <p className="text-muted-foreground">Draft your masterpiece and let the AI guide your narrative flow.</p>
                </div>

                <div className="glass rounded-2xl p-6 shadow-xl">
                    <StoryInput
                        initialStory={currentStory}
                        onStoryChange={onStoryChange}
                        onContinue={onContinue}
                        onDetectGenre={onDetectGenre}
                        onGenerateTwist={onGenerateTwist}
                        onScoreStory={onScoreStory}
                        onExtractCharacters={onExtractCharacters}
                        loading={loading}
                    />
                </div>
            </div>
        </motion.div>
    );
}
