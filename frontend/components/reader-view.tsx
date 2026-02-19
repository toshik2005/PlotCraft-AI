"use client";

import { motion } from "framer-motion";
import { ChevronLeft, ChevronRight, Book, X } from "lucide-react";
import { useState, useMemo, useEffect } from "react";
import { Button } from "./ui/button";
import { cn } from "@/lib/utils";

interface ReaderViewProps {
    fullStory: string;
    onClose: () => void;
}

export function ReaderView({ fullStory, onClose }: ReaderViewProps) {
    const [page, setPage] = useState(0);
    const [isMobile, setIsMobile] = useState(false);

    useEffect(() => {
        const checkMobile = () => setIsMobile(window.innerWidth < 1024); // Use lg breakpoint for dual page
        checkMobile();
        window.addEventListener('resize', checkMobile);
        return () => window.removeEventListener('resize', checkMobile);
    }, []);

    const pages = useMemo(() => {
        const PAGE_SIZE = 600;
        return fullStory.match(new RegExp(`.{1,${PAGE_SIZE}}(\\s|$)`, 'gs')) || [fullStory];
    }, [fullStory]);

    const totalPages = pages.length;
    const step = isMobile ? 1 : 2;

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="max-w-6xl mx-auto w-full pt-32 pb-24 px-4 relative"
        >
            <div className="absolute top-24 right-8 z-20">
                <Button
                    variant="ghost"
                    size="icon"
                    onClick={onClose}
                    className="rounded-full hover:bg-primary/10 transition-colors w-10 h-10"
                >
                    <X className="w-5 h-5 text-muted-foreground hover:text-primary transition-colors" />
                </Button>
            </div>
            <div className="w-full relative min-h-[70vh] flex flex-col items-center">
                <div className={cn(
                    "w-full relative perspective-2000 flex shadow-[0_50px_100px_-20px_rgba(0,0,0,0.5)]",
                    isMobile ? "max-w-md aspect-[0.7/1]" : "aspect-[1.4/1]"
                )}>
                    {/* Left Page (Always visible) */}
                    <div className="flex-1 book-gradient rounded-l-3xl lg:border-r border-black/10 relative overflow-hidden">
                        <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/paper-fibers.png')] opacity-20 pointer-events-none" />
                        <div className="h-full p-8 sm:p-14 flex flex-col">
                            <div className="mb-6 text-[10px] font-serif uppercase tracking-[0.3em] opacity-40 flex items-center gap-2">
                                <Book className="w-3 h-3 text-primary" />
                                Manuscript Archive
                            </div>
                            <div className="flex-1 overflow-y-auto scrollbar-hide">
                                <p className="text-lg sm:text-xl font-serif leading-relaxed text-ink first-letter:text-5xl first-letter:font-bold first-letter:mr-3 first-letter:float-left first-letter:text-primary">
                                    {pages[page] || ""}
                                </p>
                            </div>
                            <div className="mt-8 text-xs font-serif opacity-30 text-center tracking-widest">
                                &mdash; {page + 1} &mdash;
                            </div>
                        </div>
                    </div>

                    {/* Right Page (Only visible on desktop) */}
                    {!isMobile && (
                        <div className="flex-1 book-gradient rounded-r-3xl relative overflow-hidden">
                            <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/paper-fibers.png')] opacity-20 pointer-events-none" />
                            <div className="h-full p-8 sm:p-14 flex flex-col border-l border-white/5">
                                <div className="mb-6 text-[10px] font-serif uppercase tracking-[0.3em] opacity-40 text-right">
                                    PlotCraft Anthology
                                </div>
                                <div className="flex-1 overflow-y-auto scrollbar-hide">
                                    <p className="text-lg sm:text-xl font-serif leading-relaxed text-ink">
                                        {pages[page + 1] || ""}
                                    </p>
                                </div>
                                {pages[page + 1] && (
                                    <div className="mt-8 text-xs font-serif opacity-30 text-center tracking-widest">
                                        &mdash; {page + 2} &mdash;
                                    </div>
                                )}
                            </div>
                        </div>
                    )}

                    {/* Navigation Controls */}
                    <div className="absolute inset-y-0 -left-6 flex items-center pointer-events-none">
                        <Button
                            variant="secondary"
                            size="icon"
                            disabled={page === 0}
                            onClick={() => setPage(p => Math.max(0, p - step))}
                            className="rounded-full w-12 h-12 shadow-2xl pointer-events-auto hover:scale-110 transition-transform bg-background/80 backdrop-blur"
                        >
                            <ChevronLeft className="w-6 h-6" />
                        </Button>
                    </div>

                    <div className="absolute inset-y-0 -right-6 flex items-center pointer-events-none">
                        <Button
                            variant="secondary"
                            size="icon"
                            disabled={page + step >= totalPages}
                            onClick={() => setPage(p => Math.min(totalPages - 1, p + step))}
                            className="rounded-full w-12 h-12 shadow-2xl pointer-events-auto hover:scale-110 transition-transform bg-background/80 backdrop-blur"
                        >
                            <ChevronRight className="w-6 h-6" />
                        </Button>
                    </div>
                </div>

                <div className="mt-12 glass px-8 py-3 rounded-full text-[10px] font-serif tracking-[0.4em] opacity-60 uppercase">
                    Chapter Progress &bull; {Math.round(((page + (isMobile ? 1 : 2)) / totalPages) * 100)}% Complete
                </div>
            </div>
        </motion.div>
    );
}
