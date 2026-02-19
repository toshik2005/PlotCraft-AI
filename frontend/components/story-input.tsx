"use client";

import { useEffect, useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Loader2, Sparkles, PenTool, Zap, Target, BookOpen, Users, RotateCcw, Eye, ShieldAlert, Search } from "lucide-react";
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
  onGenerateTwist: (story: string, twistType?: string) => Promise<void>;
  onScoreStory: (story: string) => Promise<void>;
  onExtractCharacters: (story: string) => Promise<void>;
  loading?: boolean;
  initialStory?: string;
  onStoryChange?: (story: string) => void;
}

export function StoryInput({
  onContinue,
  onDetectGenre,
  onGenerateTwist,
  onScoreStory,
  onExtractCharacters,
  loading = false,
  initialStory,
  onStoryChange,
}: StoryInputProps) {
  const [story, setStory] = useState(initialStory ?? "");
  const [genre, setGenre] = useState("");
  const [twistType, setTwistType] = useState("unexpected");
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

            <div className="mt-8 pt-6 border-t border-primary/10 flex flex-wrap gap-6">
              <div className="space-y-1">
                <Label className="text-[10px] uppercase tracking-widest opacity-40">Genre Filter</Label>
                <Input
                  value={genre}
                  onChange={e => setGenre(e.target.value)}
                  className="h-8 bg-transparent border-primary/20 rounded-full text-xs"
                  placeholder="Fantasy, Noir, etc."
                />
              </div>
              <div className="space-y-1">
                <Label className="text-[10px] uppercase tracking-widest opacity-40">Narrative Twist</Label>
                <Select value={twistType} onValueChange={setTwistType}>
                  <SelectTrigger className="h-8 bg-transparent border-primary/20 rounded-full text-xs px-3 min-w-[130px] hover:border-primary/50 transition-colors">
                    <SelectValue placeholder="Select Twist" />
                  </SelectTrigger>
                  <SelectContent className="glass border-primary/20 rounded-2xl">
                    <SelectItem value="unexpected" className="text-xs hover:bg-primary/10 rounded-lg">
                      <div className="flex items-center gap-2">
                        <Sparkles className="w-3 h-3 text-amber-500" />
                        <span>Unexpected</span>
                      </div>
                    </SelectItem>
                    <SelectItem value="reversal" className="text-xs hover:bg-primary/10 rounded-lg">
                      <div className="flex items-center gap-2">
                        <RotateCcw className="w-3 h-3 text-blue-500" />
                        <span>Reversal</span>
                      </div>
                    </SelectItem>
                    <SelectItem value="revelation" className="text-xs hover:bg-primary/10 rounded-lg">
                      <div className="flex items-center gap-2">
                        <Eye className="w-3 h-3 text-purple-500" />
                        <span>Revelation</span>
                      </div>
                    </SelectItem>
                    <SelectItem value="betrayal" className="text-xs hover:bg-primary/10 rounded-lg">
                      <div className="flex items-center gap-2">
                        <ShieldAlert className="w-3 h-3 text-red-500" />
                        <span>Betrayal</span>
                      </div>
                    </SelectItem>
                    <SelectItem value="discovery" className="text-xs hover:bg-primary/10 rounded-lg">
                      <div className="flex items-center gap-2">
                        <Search className="w-3 h-3 text-emerald-500" />
                        <span>Discovery</span>
                      </div>
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Wax Seal Action Buttons */}
      <div className="flex flex-wrap justify-center gap-4">
        {[
          { label: "Continue", icon: Sparkles, action: () => onContinue(story, genre), primary: true },
          { label: "Refine", icon: Zap, action: () => onDetectGenre(story) },
          { label: "Infuse Twist", icon: PenTool, action: () => onGenerateTwist(story, twistType) },
          { label: "Measure", icon: Target, action: () => onScoreStory(story) },
          { label: "Identify", icon: Users, action: () => onExtractCharacters(story) },
        ].map((btn, i) => (
          <motion.button
            key={btn.label}
            whileHover={{ scale: 1.05, y: -2 }}
            whileTap={{ scale: 0.95 }}
            onClick={btn.action}
            disabled={loading || !story.trim()}
            className={cn(
              "group relative px-6 py-3 rounded-2xl flex items-center gap-2 transition-all duration-300 overflow-hidden shadow-lg",
              btn.primary
                ? "bg-primary text-primary-foreground"
                : "glass text-foreground border-primary/10 hover:border-primary/40",
              (loading || !story.trim()) && "opacity-50 grayscale cursor-not-allowed"
            )}
          >
            {/* Animated wax shine */}
            <div className="absolute inset-0 bg-gradient-to-tr from-white/0 via-white/10 to-white/0 -translate-x-full group-hover:translate-x-full transition-transform duration-1000" />

            {loading && btn.primary ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <btn.icon className="w-4 h-4" />
            )}
            <span className="text-sm font-bold tracking-tight">{btn.label}</span>
          </motion.button>
        ))}
      </div>
    </div>
  );
}
