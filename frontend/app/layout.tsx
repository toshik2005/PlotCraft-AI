import type { Metadata } from "next"
import "./globals.css"
import { Providers } from "@/components/providers"
import { Toaster } from "@/components/ui/sonner"

export const metadata: Metadata = {
  title: "PlotCraft-AI",
  description: "AI-Powered Story Generation and Analysis Platform",
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-background text-foreground">
        <Providers>
          <Toaster />
          {children}
        </Providers>
      </body>
    </html>
  );
}
