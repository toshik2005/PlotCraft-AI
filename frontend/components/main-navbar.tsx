"use client";

import { motion } from "framer-motion";
import { PenTool, Eye, BookOpen, Sparkles, Sun, Moon } from "lucide-react";
import { cn } from "@/lib/utils";
import { useEffect, useState } from "react";

export type Phase = "writer" | "reader";

interface MainNavbarProps {
    currentPhase: Phase;
    onPhaseChange: (phase: Phase) => void;
    isGenerating?: boolean;
}

export function MainNavbar({ currentPhase, onPhaseChange, isGenerating }: MainNavbarProps) {
    const [theme, setTheme] = useState<"light" | "dark">("dark");

    useEffect(() => {
        const savedTheme = localStorage.getItem("theme") as "light" | "dark" | null;
        if (savedTheme) {
            setTheme(savedTheme);
            document.documentElement.classList.toggle("dark", savedTheme === "dark");
        } else {
            document.documentElement.classList.add("dark");
        }
    }, []);

    const toggleTheme = () => {
        const newTheme = theme === "light" ? "dark" : "light";
        setTheme(newTheme);
        localStorage.setItem("theme", newTheme);
        document.documentElement.classList.toggle("dark", newTheme === "dark");
    };

    const steps = [
        { id: "writer", label: "Craft", icon: PenTool },
        { id: "reader", label: "Read", icon: BookOpen },
    ] as const;

    return (
        <div className="fixed top-6 left-1/2 -translate-x-1/2 z-[100] w-full max-w-2xl px-4">
            <motion.nav
                initial={{ y: -100, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                className="glass rounded-full px-2 py-2 flex items-center justify-between shadow-2xl shadow-purple-500/10"
            >
                <div className="flex items-center gap-1 pl-4 mr-6">
                    <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center">
                        <Sparkles className="w-4 h-4 text-primary-foreground" />
                    </div>
                    <span className="font-bold text-sm tracking-tight hidden sm:block">PlotCraft</span>
                </div>

                <div className="flex items-center gap-1 flex-1 justify-center">
                    {steps.map((step) => {
                        const Icon = step.icon;
                        const isActive = currentPhase === step.id;

                        return (
                            <button
                                key={step.id}
                                onClick={() => onPhaseChange(step.id as Phase)}
                                className={cn(
                                    "relative flex items-center gap-2 px-4 py-2 rounded-full transition-all duration-300",
                                    isActive
                                        ? "text-primary-foreground"
                                        : "text-muted-foreground hover:text-foreground hover:bg-muted/50"
                                )}
                            >
                                {isActive && (
                                    <motion.div
                                        layoutId="active-pill"
                                        className="absolute inset-0 bg-primary rounded-full"
                                        transition={{ type: "spring", bounce: 0.2, duration: 0.6 }}
                                    />
                                )}
                                <Icon className={cn("w-4 h-4 relative z-10", isActive && "animate-pulse")} />
                                <span className="text-xs font-medium relative z-10">{step.label}</span>
                            </button>
                        );
                    })}
                </div>

                <div className="flex items-center gap-2 pr-2">
                    <button
                        onClick={toggleTheme}
                        className="w-10 h-10 rounded-full flex items-center justify-center text-muted-foreground hover:bg-muted/50 hover:text-foreground transition-colors"
                    >
                        {theme === "light" ? <Moon className="w-4 h-4" /> : <Sun className="w-4 h-4" />}
                    </button>
                    {isGenerating && (
                        <motion.div
                            animate={{ rotate: 360 }}
                            transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                            className="w-4 h-4 rounded-full border-2 border-primary border-t-transparent"
                        />
                    )}
                </div>
            </motion.nav>
        </div>
    );
}
