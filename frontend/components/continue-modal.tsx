"use client";

import { motion } from "framer-motion";
import { Button } from "./ui/button";
import { BookOpenCheck, Sparkles, X } from "lucide-react";

interface ContinueModalProps {
  onReadExisting: () => void;
  onCreateNew: () => void;
  onClose: () => void;
}

export function ContinueModal({ onReadExisting, onCreateNew, onClose }: ContinueModalProps) {
  return (
    <div className="fixed inset-0 z-[130] flex items-center justify-center p-4">
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
        className="relative w-full max-w-md glass rounded-3xl shadow-2xl"
      >
        <div className="flex items-center justify-between px-6 py-4 border-b bg-muted/30 rounded-t-3xl">
          <div>
            <h3 className="text-sm font-bold uppercase tracking-widest text-muted-foreground">
              Continue story
            </h3>
            <p className="text-xs text-muted-foreground/70">
              You already have a continuation for this manuscript.
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
          <p className="text-sm text-muted-foreground">
            Would you like to reopen the existing continuation in reader mode, or generate a new
            alternative continuation?
          </p>

          <div className="flex flex-col sm:flex-row gap-3 mt-2">
            <Button
              variant="outline"
              className="flex-1 rounded-2xl justify-start gap-2"
              onClick={onReadExisting}
            >
              <BookOpenCheck className="w-4 h-4" />
              <span className="text-sm font-semibold">Read existing</span>
            </Button>
            <Button
              className="flex-1 rounded-2xl justify-start gap-2"
              onClick={onCreateNew}
            >
              <Sparkles className="w-4 h-4" />
              <span className="text-sm font-semibold">Create new</span>
            </Button>
          </div>
        </div>
      </motion.div>
    </div>
  );
}

