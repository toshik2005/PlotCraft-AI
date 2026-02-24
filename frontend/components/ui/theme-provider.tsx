"use client";

import React, { createContext, useContext, useEffect, useState } from "react";

type ThemeProviderProps = {
  children: React.ReactNode;
  defaultTheme?: "dark" | "light";
  storageKey?: string;
  enableSystem?: boolean;
  enableTransition?: boolean;
};

type ThemeContextType = {
  theme: "dark" | "light";
  setTheme: (theme: "dark" | "light" | "system") => void;
  toggleTheme: () => void;
  isSystem: boolean;
  resolvedTheme: "dark" | "light";
};

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

// Optimized SSR-safe theme detection
function useThemeSSR(): "dark" | "light" {
  if (typeof window === "undefined") {
    return "light";
  }
  
  const storedTheme = localStorage.getItem("theme") as "dark" | "light" | null;
  if (storedTheme) return storedTheme;
  
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

// System preference detection with proper cleanup
function useSystemThemeHook() {
  const [systemTheme, setSystemTheme] = useState<"dark" | "light">("light");

  useEffect(() => {
    const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");
    
    const updateSystemTheme = (e: MediaQueryListEvent | MediaQueryList) => {
      setSystemTheme(e.matches ? "dark" : "light");
    };

    // Set initial value
    updateSystemTheme(mediaQuery);

    // Listen for changes
    mediaQuery.addEventListener("change", updateSystemTheme);

    return () => {
      mediaQuery.removeEventListener("change", updateSystemTheme);
    };
  }, []);

  return systemTheme;
}

export function ThemeProvider({
  children,
  defaultTheme = "light",
  storageKey = "theme",
  enableSystem = true,
  enableTransition = true,
}: ThemeProviderProps) {
  const systemTheme = useSystemThemeHook();
  
  const [theme, setTheme] = useState<"dark" | "light">(() => {
    // During SSR, use the defaultTheme
    if (typeof window === "undefined") {
      return defaultTheme;
    }
    
    // On client, check localStorage first
    const storedTheme = localStorage.getItem(storageKey) as "dark" | "light" | "system" | null;
    
    if (storedTheme === "system" && enableSystem) {
      return systemTheme;
    }
    
    if (storedTheme === "dark" || storedTheme === "light") {
      return storedTheme;
    }
    
    // Fallback to system preference or default
    return enableSystem ? systemTheme : defaultTheme;
  });

  const [isSystem, setIsSystem] = useState(() => {
    if (typeof window === "undefined") return false;
    return localStorage.getItem(storageKey) === "system";
  });

  // Resolved theme (actual theme being applied)
  const resolvedTheme = isSystem ? systemTheme : theme;

  // Apply theme to document with optimizations
  useEffect(() => {
    const root = document.documentElement;
    
    // Remove existing theme classes
    root.classList.remove("light", "dark");
    
    // Add new theme class
    root.classList.add(resolvedTheme);
    
    // Set data attribute for CSS custom properties
    root.setAttribute("data-theme", resolvedTheme);
    
    // Store in localStorage
    const valueToStore = isSystem ? "system" : resolvedTheme;
    localStorage.setItem(storageKey, valueToStore);
    
    // Prevent flash of unstyled content
    root.style.colorScheme = resolvedTheme;
    
    // Add transition class if enabled
    if (enableTransition) {
      root.classList.add("transition-colors", "duration-200");
    }
  }, [resolvedTheme, isSystem, storageKey, enableTransition]);

  // Update theme when system preference changes
  useEffect(() => {
    if (isSystem) {
      setTheme(systemTheme);
    }
  }, [systemTheme, isSystem]);

  // Optimized theme setter
  const setThemeOptimized = (newTheme: "dark" | "light" | "system") => {
    if (newTheme === "system") {
      setIsSystem(true);
      setTheme(systemTheme);
    } else {
      setIsSystem(false);
      setTheme(newTheme);
    }
  };

  // Optimized theme toggle
  const toggleTheme = () => {
    if (isSystem) {
      // If currently using system, switch to explicit theme
      setThemeOptimized(systemTheme === "dark" ? "light" : "dark");
    } else {
      // Toggle between light and dark
      setThemeOptimized(theme === "dark" ? "light" : "dark");
    }
  };

  // Expose system theme for components that need it
  const contextValue: ThemeContextType = {
    theme: resolvedTheme,
    setTheme: setThemeOptimized,
    toggleTheme,
    isSystem,
    resolvedTheme,
  };

  return (
    <ThemeContext.Provider value={contextValue}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error("useTheme must be used within a ThemeProvider");
  }
  return context;
}

// Hook for system theme changes
export function useSystemTheme() {
  const { isSystem, resolvedTheme } = useTheme();
  return { isSystem, resolvedTheme };
}

// Hook for theme-aware styling
export function useThemeClass(lightClass: string, darkClass: string) {
  const { resolvedTheme } = useTheme();
  return resolvedTheme === "dark" ? darkClass : lightClass;
}

// Utility for conditional theme classes
export function getThemeClass(lightClass: string, darkClass: string, theme?: "dark" | "light") {
  const currentTheme = theme || (typeof window !== "undefined" ? 
    document.documentElement.classList.contains("dark") ? "dark" : "light" : "light"
  );
  return currentTheme === "dark" ? darkClass : lightClass;
}

export { useThemeSSR }; 