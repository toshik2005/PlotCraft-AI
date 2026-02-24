"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface StoryOutputProps {
  title: string;
  description?: string;
  children: React.ReactNode;
}

export function StoryOutput({ title, description, children }: StoryOutputProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        {description && <CardDescription>{description}</CardDescription>}
      </CardHeader>
      <CardContent>{children}</CardContent>
    </Card>
  );
}

interface GenreDisplayProps {
  genre: string;
  confidence: number;
  allProbabilities?: Record<string, number>;
}

export function GenreDisplay({ genre, confidence, allProbabilities }: GenreDisplayProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <span className="text-sm text-muted-foreground">Genre:</span>
        <Badge variant="default" className="text-sm">
          {genre}
        </Badge>
        <span className="text-sm text-muted-foreground">
          ({Math.round(confidence * 100)}% confidence)
        </span>
      </div>
      {allProbabilities && (
        <div className="space-y-2">
          <p className="text-sm font-medium">All Probabilities:</p>
          <div className="flex flex-wrap gap-2">
            {Object.entries(allProbabilities)
              .sort(([, a], [, b]) => b - a)
              .map(([genreName, prob]) => (
                <Badge key={genreName} variant="outline" className="text-xs">
                  {genreName}: {Math.round(prob * 100)}%
                </Badge>
              ))}
          </div>
        </div>
      )}
    </div>
  );
}

interface CharactersDisplayProps {
  characters: string[];
}

export function CharactersDisplay({ characters }: CharactersDisplayProps) {
  if (characters.length === 0) {
    return <p className="text-sm text-muted-foreground">No characters found.</p>;
  }

  return (
    <div className="space-y-2">
      <p className="text-sm font-medium">Found {characters.length} character(s):</p>
      <div className="flex flex-wrap gap-2">
        {characters.map((char, idx) => (
          <Badge key={idx} variant="secondary">
            {char}
          </Badge>
        ))}
      </div>
    </div>
  );
}

interface ScoreDisplayProps {
  totalScore: number;
  breakdown?: Record<string, number>;
  metrics?: Record<string, number>;
}

export function ScoreDisplay({ totalScore, breakdown, metrics }: ScoreDisplayProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <span className="text-sm font-medium">Total Score:</span>
        <Badge variant="default" className="text-lg">
          {totalScore}/100
        </Badge>
      </div>
      {breakdown && (
        <div className="space-y-2">
          <p className="text-sm font-medium">Breakdown:</p>
          <div className="space-y-1">
            {Object.entries(breakdown).map(([key, value]) => (
              <div key={key} className="flex items-center justify-between text-sm">
                <span className="capitalize">{key.replace(/_/g, " ")}:</span>
                <span className="font-medium">{Math.round(value)}</span>
              </div>
            ))}
          </div>
        </div>
      )}
      {metrics && (
        <div className="space-y-2">
          <p className="text-sm font-medium">Metrics:</p>
          <div className="space-y-1">
            {Object.entries(metrics).map(([key, value]) => (
              <div key={key} className="flex items-center justify-between text-sm">
                <span className="capitalize">{key.replace(/_/g, " ")}:</span>
                <span className="font-medium">{typeof value === "number" ? value.toFixed(2) : value}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
