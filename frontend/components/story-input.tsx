"use client";

import { useEffect, useRef, useState } from "react";
import { Label } from "@/components/ui/label";
import { Loader2, Sparkles, Target, BookOpen, Users, Rocket, Ghost, Search, PenTool } from "lucide-react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { motion, AnimatePresence } from "framer-motion";
import { cn } from "@/lib/utils";

interface StoryInputProps {
  onContinue: (story: string, genre?: string) => Promise<void>;
  onDetectGenre: (story: string) => Promise<void>;
  onScoreStory: (story: string) => Promise<void>;
  onExtractCharacters: (story: string) => Promise<void>;
  loading?: boolean;
  initialStory?: string;
  onStoryChange?: (story: string) => void;
}

export function StoryInput({
  onContinue,
  onDetectGenre,
  onScoreStory,
  onExtractCharacters,
  loading = false,
  initialStory,
  onStoryChange,
}: StoryInputProps) {
  const [story, setStory] = useState(initialStory ?? "");
  /** Genre for continuation: "Auto" = detect; explicit values map to PlotCraft models */
  const [genre, setGenre] = useState<"Auto" | "Sci-Fi" | "Horror" | "Action">("Auto");
  const [isTyping, setIsTyping] = useState(false);
  const [caretPos, setCaretPos] = useState({ x: 0, y: 0 });

  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const mirrorRef = useRef<HTMLDivElement>(null);
  const markerRef = useRef<HTMLSpanElement>(null);
  const typingTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (initialStory !== undefined && initialStory !== story) {
      setStory(initialStory);
    }
  }, [initialStory]);

  const updateCaretPos = () => {
    if (!textareaRef.current || !mirrorRef.current || !markerRef.current) return;

    const textarea = textareaRef.current;
    const mirror = mirrorRef.current;
    const marker = markerRef.current;
    const selectionEnd = textarea.selectionEnd;
    const textBeforeCaret = textarea.value.substring(0, selectionEnd);

    // Update mirror text and move marker
    mirror.textContent = textBeforeCaret;
    mirror.appendChild(marker);

    const { offsetLeft, offsetTop } = marker;

    setCaretPos({
      x: offsetLeft - textarea.scrollLeft,
      y: offsetTop - textarea.scrollTop,
    });
  };

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value;
    setStory(value);
    onStoryChange?.(value);
    setIsTyping(true);
    updateCaretPos();

    // Reset typing state after pause using ref to avoid closures/multiple timeouts
    if (typingTimeoutRef.current) clearTimeout(typingTimeoutRef.current);
    typingTimeoutRef.current = setTimeout(() => setIsTyping(false), 1000);
  };

  const wordCount = story.trim() ? story.trim().split(/\s+/).length : 0;
  const charCount = story.length;

  return (
    <div className="space-y-8">
      {/* The Manuscript Sheet */}
      <div className="relative group">
        <div className="absolute -inset-4 bg-gradient-to-r from-primary/10 via-purple-500/5 to-primary/10 blur-xl opacity-50 group-hover:opacity-100 transition-opacity duration-1000 pointer-events-none" />

        <div className="relative glass rounded-3xl overflow-hidden shadow-2xl border-primary/20">
          <div className="bg-muted/30 px-6 py-3 border-b flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-2 h-2 rounded-full bg-red-500" />
              <div className="w-2 h-2 rounded-full bg-amber-500" />
              <div className="w-2 h-2 rounded-full bg-emerald-500" />
              <span className="ml-2 text-[10px] font-bold uppercase tracking-[0.2em] opacity-40">Live Scriptum</span>
            </div>
            <div className="flex gap-4 text-[10px] font-bold uppercase tracking-widest opacity-40">
              <span>{wordCount} Words</span>
              <span>{charCount} Chars</span>
            </div>
          </div>

          <div className="relative p-8 min-h-[400px] flex flex-col bg-book-paper/40">
            {/* Mirror div for caret tracking (hidden) */}
            <div
              ref={mirrorRef}
              className="absolute pointer-events-none whitespace-pre-wrap break-words italic text-lg opacity-0"
              style={{
                fontFamily: "var(--font-serif), Georgia, serif",
                padding: "32px", // Matches textarea padding
                width: "calc(100% - 64px)",
                lineHeight: "1.6rem",
              }}
            />
            {/* Permanent marker for position measurement */}
            <span ref={markerRef} className="absolute invisible pointer-events-none">|</span>

            {/* 3D Floating Pen */}
            <AnimatePresence>
              {story.length > 0 && (
                <motion.div
                  animate={{
                    x: caretPos.x + 40,
                    y: caretPos.y + 10,
                    rotate: isTyping ? [0, -20, 0] : 0,
                    scale: isTyping ? 1.1 : 1,
                  }}
                  transition={{ type: "spring", stiffness: 150, damping: 15 }}
                  className="absolute pointer-events-none z-20"
                >
                  <PenTool className="w-8 h-8 text-primary drop-shadow-[0_10px_10px_rgba(168,85,247,0.4)]" />
                  {isTyping && (
                    <motion.div
                      initial={{ scale: 0, opacity: 0 }}
                      animate={{ scale: [0, 1.5], opacity: [0.5, 0] }}
                      className="absolute top-8 left-1 w-2 h-2 rounded-full bg-primary/40 blur-sm"
                    />
                  )}
                </motion.div>
              )}
            </AnimatePresence>

            <textarea
              ref={textareaRef}
              value={story}
              onChange={handleChange}
              onKeyUp={updateCaretPos}
              onMouseDown={updateCaretPos}
              onScroll={updateCaretPos}
              placeholder="Start your legend here..."
              className="w-full flex-1 bg-transparent border-none outline-none resize-none text-xl leading-relaxed font-serif text-ink placeholder:text-muted-foreground/30 scrollbar-hide"
              disabled={loading}
            />

            <div className="mt-8 pt-6 border-t border-primary/10 flex flex-wrap items-center justify-between gap-4">
              <div className="space-y-1">
                <Label className="text-[10px] uppercase tracking-widest opacity-40">
                  Story genre
                </Label>
                <Select
                  value={genre}
                  onValueChange={(v: "Auto" | "Sci-Fi" | "Horror" | "Action") => setGenre(v)}
                >
                  <SelectTrigger className="h-8 bg-transparent border-primary/20 rounded-full text-xs px-3 min-w-[140px] hover:border-primary/50 transition-colors">
                    <SelectValue placeholder="Genre" />
                  </SelectTrigger>
                  <SelectContent className="glass border-primary/20 rounded-2xl">
                    <SelectItem value="Auto" className="text-xs hover:bg-primary/10 rounded-lg">
                      <div className="flex items-center gap-2">
                        <BookOpen className="w-3 h-3 text-muted-foreground" />
                        <span>Auto (detect)</span>
                      </div>
                    </SelectItem>
                    <SelectItem value="Sci-Fi" className="text-xs hover:bg-primary/10 rounded-lg">
                      <div className="flex items-center gap-2">
                        <Rocket className="w-3 h-3 text-cyan-500" />
                        <span>Sci-Fi</span>
                      </div>
                    </SelectItem>
                    <SelectItem value="Horror" className="text-xs hover:bg-primary/10 rounded-lg">
                      <div className="flex items-center gap-2">
                        <Ghost className="w-3 h-3 text-rose-500" />
                        <span>Horror</span>
                      </div>
                    </SelectItem>
                    <SelectItem value="Action" className="text-xs hover:bg-primary/10 rounded-lg">
                      <div className="flex items-center gap-2">
                        <Target className="w-3 h-3 text-orange-500" />
                        <span>Action</span>
                      </div>
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <motion.button
                whileHover={{ scale: 1.05, y: -2 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => onContinue(story, genre === "Auto" ? undefined : genre)}
                disabled={loading || !story.trim()}
                className={cn(
                  "group relative px-6 py-3 rounded-2xl flex items-center gap-2 transition-all duration-300 overflow-hidden shadow-lg bg-primary text-primary-foreground",
                  (loading || !story.trim()) && "opacity-50 grayscale cursor-not-allowed"
                )}
              >
                <div className="absolute inset-0 bg-gradient-to-tr from-white/0 via-white/10 to-white/0 -translate-x-full group-hover:translate-x-full transition-transform duration-1000" />
                {loading ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Sparkles className="w-4 h-4" />
                )}
                <span className="text-sm font-bold tracking-tight">Continue</span>
              </motion.button>
            </div>
          </div>
        </div>
      </div>

      {/* Analysis Action Buttons */}
      <div className="flex flex-wrap justify-center gap-4">
        {[
          { label: "Detect Genre", icon: Search, action: () => onDetectGenre(story) },
          { label: "Measure", icon: Target, action: () => onScoreStory(story) },
          { label: "Identify", icon: Users, action: () => onExtractCharacters(story) },
        ].map((btn) => (
          <motion.button
            key={btn.label}
            whileHover={{ scale: 1.05, y: -2 }}
            whileTap={{ scale: 0.95 }}
            onClick={btn.action}
            disabled={loading || !story.trim()}
            className={cn(
              "group relative px-6 py-3 rounded-2xl flex items-center gap-2 transition-all duration-300 overflow-hidden shadow-lg glass text-foreground border-primary/10 hover:border-primary/40",
              (loading || !story.trim()) && "opacity-50 grayscale cursor-not-allowed"
            )}
          >
            <div className="absolute inset-0 bg-gradient-to-tr from-white/0 via-white/10 to-white/0 -translate-x-full group-hover:translate-x-full transition-transform duration-1000" />
            <btn.icon className="w-4 h-4" />
            <span className="text-sm font-bold tracking-tight">{btn.label}</span>
          </motion.button>
        ))}
      </div>
    </div>
  );
}
