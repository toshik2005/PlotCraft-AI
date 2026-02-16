"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Loader2 } from "lucide-react";

interface StoryInputProps {
  onContinue: (story: string, genre?: string) => Promise<void>;
  onDetectGenre: (story: string) => Promise<void>;
  onGenerateTwist: (story: string, twistType?: string) => Promise<void>;
  onScoreStory: (story: string) => Promise<void>;
  onExtractCharacters: (story: string) => Promise<void>;
  loading?: boolean;
}

export function StoryInput({
  onContinue,
  onDetectGenre,
  onGenerateTwist,
  onScoreStory,
  onExtractCharacters,
  loading = false,
}: StoryInputProps) {
  const [story, setStory] = useState("");
  const [genre, setGenre] = useState("");
  const [twistType, setTwistType] = useState("unexpected");

  const handleContinue = async () => {
    if (!story.trim()) return;
    await onContinue(story, genre || undefined);
  };

  const handleDetectGenre = async () => {
    if (!story.trim()) return;
    await onDetectGenre(story);
  };

  const handleGenerateTwist = async () => {
    if (!story.trim()) return;
    await onGenerateTwist(story, twistType);
  };

  const handleScoreStory = async () => {
    if (!story.trim()) return;
    await onScoreStory(story);
  };

  const handleExtractCharacters = async () => {
    if (!story.trim()) return;
    await onExtractCharacters(story);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Story Input</CardTitle>
        <CardDescription>
          Enter your story text to generate continuations, detect genre, add twists, score, or extract characters.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="story">Your Story</Label>
          <textarea
            id="story"
            value={story}
            onChange={(e) => setStory(e.target.value)}
            placeholder="Once upon a time..."
            className="w-full min-h-[200px] px-3 py-2 rounded-md border border-input bg-transparent text-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
            disabled={loading}
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="genre">Genre (Optional)</Label>
            <Input
              id="genre"
              value={genre}
              onChange={(e) => setGenre(e.target.value)}
              placeholder="horror, scifi, fantasy, etc."
              disabled={loading}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="twist-type">Twist Type</Label>
            <select
              id="twist-type"
              value={twistType}
              onChange={(e) => setTwistType(e.target.value)}
              className="w-full h-9 px-3 rounded-md border border-input bg-background text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
              disabled={loading}
            >
              <option value="unexpected">Unexpected</option>
              <option value="reversal">Reversal</option>
              <option value="revelation">Revelation</option>
              <option value="betrayal">Betrayal</option>
              <option value="discovery">Discovery</option>
            </select>
          </div>
        </div>

        <div className="flex flex-wrap gap-2">
          <Button
            onClick={handleContinue}
            disabled={loading || !story.trim()}
            className="flex-1 min-w-[140px]"
          >
            {loading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Generating...
              </>
            ) : (
              "Continue Story"
            )}
          </Button>
          <Button
            onClick={handleDetectGenre}
            disabled={loading || !story.trim()}
            variant="outline"
            className="flex-1 min-w-[140px]"
          >
            Detect Genre
          </Button>
          <Button
            onClick={handleGenerateTwist}
            disabled={loading || !story.trim()}
            variant="outline"
            className="flex-1 min-w-[140px]"
          >
            Add Twist
          </Button>
          <Button
            onClick={handleScoreStory}
            disabled={loading || !story.trim()}
            variant="outline"
            className="flex-1 min-w-[140px]"
          >
            Score Story
          </Button>
          <Button
            onClick={handleExtractCharacters}
            disabled={loading || !story.trim()}
            variant="outline"
            className="flex-1 min-w-[140px]"
          >
            Extract Characters
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
