# Frontend Integration Guide

## Overview

This guide explains how to integrate the new multi-genre story generation pipeline into the frontend.

---

## New Endpoint: POST /api/v1/story/generate

### TypeScript Types

```typescript
interface GenerateStoryRequest {
  user_id: string;
  story: string;
  genre: "action" | "horror" | "scifi";
  twist?: "unexpected" | "reversal" | "revelation" | "betrayal" | "discovery";
  refine?: boolean;
  measure?: boolean;
  temperature?: number;  // 0.1 - 2.0
  max_tokens?: number;   // 50 - 1000
}

interface GenerateStoryResponse {
  genre: string;
  detected_characters: string[];
  persisted_characters: string[];
  twist_applied: string | null;
  generated_text: string;
  refined: boolean;
  score: number | null;
  character_focus_required: boolean;
}
```

### React Hook Example

```typescript
import { useState, useCallback } from 'react';
import { GenerateStoryRequest, GenerateStoryResponse } from '@/types/story';

export function useStoryGeneration() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const generateStory = useCallback(
    async (request: GenerateStoryRequest): Promise<GenerateStoryResponse | null> => {
      setLoading(true);
      setError(null);

      try {
        const response = await fetch('/api/v1/story/generate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(request),
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || 'Generation failed');
        }

        const data: GenerateStoryResponse = await response.json();
        return data;
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Unknown error';
        setError(message);
        return null;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  return { generateStory, loading, error };
}
```

### Usage Example

```typescript
function StoryWriter() {
  const { generateStory, loading, error } = useStoryGeneration();
  const [userId] = useState(generateSessionId());
  const [characters, setCharacters] = useState<string[]>([]);

  const handleGenerate = async (prompt: string) => {
    const result = await generateStory({
      user_id: userId,
      story: prompt,
      genre: 'horror',
      twist: 'revelation',
      refine: true,
      measure: true,
      temperature: 0.85,
      max_tokens: 300,
    });

    if (result) {
      // Update character list
      setCharacters(result.persisted_characters);
      
      // Display generated text
      console.log('Generated:', result.generated_text);
      console.log('Score:', result.score);
      console.log('Twist applied:', result.twist_applied);
    }
  };

  return (
    <div>
      <StoryInput onSubmit={handleGenerate} disabled={loading} />
      {error && <Alert variant="destructive">{error}</Alert>}
      
      {characters.length > 0 && (
        <div className="mt-4">
          <h3>Story Characters</h3>
          <ul>
            {characters.map(char => (
              <li key={char}>{char}</li>
            ))}
          </ul>
        </div>
      )}

      {loading && <Spinner />}
    </div>
  );
}
```

---

## Feature Integration Examples

### 1. Genre Selection Component

```typescript
interface GenreSelectProps {
  value: 'action' | 'horror' | 'scifi';
  onChange: (genre: 'action' | 'horror' | 'scifi') => void;
}

export function GenreSelect({ value, onChange }: GenreSelectProps) {
  const genres = [
    { id: 'action', label: 'Action', emoji: '⚡' },
    { id: 'horror', label: 'Horror', emoji: '👻' },
    { id: 'scifi', label: 'Sci-Fi', emoji: '🚀' },
  ];

  return (
    <div className="flex gap-2">
      {genres.map(genre => (
        <button
          key={genre.id}
          onClick={() => onChange(genre.id as any)}
          className={`px-4 py-2 rounded ${
            value === genre.id
              ? 'bg-primary text-white'
              : 'bg-gray-200'
          }`}
        >
          {genre.emoji} {genre.label}
        </button>
      ))}
    </div>
  );
}
```

### 2. Twist Selector Component

```typescript
type TwistType = "unexpected" | "reversal" | "revelation" | "betrayal" | "discovery";

interface TwistSelectorProps {
  value: TwistType | null;
  onChange: (twist: TwistType | null) => void;
}

export function TwistSelector({ value, onChange }: TwistSelectorProps) {
  const twists = [
    { id: 'unexpected', label: 'Unexpected', desc: 'Surprising event' },
    { id: 'reversal', label: 'Reversal', desc: 'Everything changes' },
    { id: 'revelation', label: 'Revelation', desc: 'Hidden truth revealed' },
    { id: 'betrayal', label: 'Betrayal', desc: 'Trusted character betrays' },
    { id: 'discovery', label: 'Discovery', desc: 'Startling find' },
  ];

  return (
    <div className="grid grid-cols-2 gap-2">
      <button
        onClick={() => onChange(null)}
        className={`p-2 rounded text-center ${!value ? 'bg-primary text-white' : 'bg-gray-100'}`}
      >
        None
      </button>
      {twists.map(twist => (
        <button
          key={twist.id}
          onClick={() => onChange(twist.id as TwistType)}
          className={`p-2 rounded text-center ${
            value === twist.id ? 'bg-primary text-white' : 'bg-gray-100'
          }`}
          title={twist.desc}
        >
          {twist.label}
        </button>
      ))}
    </div>
  );
}
```

### 3. Advanced Settings Component

```typescript
interface StorySettingsProps {
  temperature: number;
  onTemperatureChange: (temp: number) => void;
  maxTokens: number;
  onMaxTokensChange: (tokens: number) => void;
  refine: boolean;
  onRefineChange: (refine: boolean) => void;
  measure: boolean;
  onMeasureChange: (measure: boolean) => void;
}

export function StorySettings(props: StorySettingsProps) {
  return (
    <div className="space-y-4">
      {/* Temperature Slider */}
      <div>
        <label className="block text-sm font-medium">
          Creativity: {props.temperature.toFixed(1)}
        </label>
        <input
          type="range"
          min="0.1"
          max="2"
          step="0.1"
          value={props.temperature}
          onChange={(e) => props.onTemperatureChange(parseFloat(e.target.value))}
          className="w-full"
        />
        <div className="flex justify-between text-xs text-gray-500">
          <span>Focused</span>
          <span>Creative</span>
        </div>
      </div>

      {/* Max Tokens */}
      <div>
        <label className="block text-sm font-medium mb-1">
          Length: {props.maxTokens} tokens
        </label>
        <input
          type="range"
          min="50"
          max="1000"
          step="50"
          value={props.maxTokens}
          onChange={(e) => props.onMaxTokensChange(parseInt(e.target.value))}
          className="w-full"
        />
      </div>

      {/* Checkboxes */}
      <div className="space-y-2">
        <label className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={props.refine}
            onChange={(e) => props.onRefineChange(e.target.checked)}
          />
          <span className="text-sm">Refine for coherence</span>
        </label>
        <label className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={props.measure}
            onChange={(e) => props.onMeasureChange(e.target.checked)}
          />
          <span className="text-sm">Score the story</span>
        </label>
      </div>
    </div>
  );
}
```

### 4. Story Score Display

```typescript
interface StoryScoreProps {
  score: number | null;
}

export function StoryScore({ score }: StoryScoreProps) {
  if (score === null) return null;

  // Maps 0-5 to stars and color
  const stars = Math.round(score);
  const isGood = score >= 3.5;
  const isExcellent = score >= 4.5;

  return (
    <div className={`p-4 rounded-lg border-2 ${
      isExcellent ? 'border-green-500 bg-green-50' :
      isGood ? 'border-blue-500 bg-blue-50' :
      'border-orange-500 bg-orange-50'
    }`}>
      <div className="flex items-center gap-2">
        <div className="text-3xl">
          {'⭐'.repeat(stars)}
        </div>
        <div>
          <p className="font-semibold">{score.toFixed(2)} / 5.0</p>
          <p className="text-sm text-gray-600">
            {isExcellent && 'Excellent quality!'}
            {isGood && !isExcellent && 'Good narrative'}
            {!isGood && 'Could be improved'}
          </p>
        </div>
      </div>
    </div>
  );
}
```

### 5. Character Persistence Display

```typescript
interface CharacterListProps {
  detected: string[];
  persisted: string[];
}

export function CharacterList({ detected, persisted }: CharacterListProps) {
  return (
    <div className="space-y-4">
      {/* Newly detected */}
      {detected.length > 0 && (
        <div>
          <h4 className="text-sm font-semibold text-gray-700 mb-2">
            New Characters Found
          </h4>
          <div className="flex flex-wrap gap-2">
            {detected.map(char => (
              <Badge key={char} variant="default">
                ✨ {char}
              </Badge>
            ))}
          </div>
        </div>
      )}

      {/* Persisted across session */}
      {persisted.length > 0 && (
        <div>
          <h4 className="text-sm font-semibold text-gray-700 mb-2">
            Story Cast ({persisted.length})
          </h4>
          <div className="flex flex-wrap gap-2">
            {persisted.map(char => (
              <Badge
                key={char}
                variant="secondary"
                className="cursor-pointer hover:bg-gray-300"
              >
                👤 {char}
              </Badge>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
```

---

## Complete Story Writer Component

```typescript
import { useState } from 'react';
import { useStoryGeneration } from '@/hooks/useStoryGeneration';
import { GenerateStoryRequest } from '@/types/story';
import { GenreSelect } from '@/components/GenreSelect';
import { TwistSelector } from '@/components/TwistSelector';
import { StorySettings } from '@/components/StorySettings';
import { StoryScore } from '@/components/StoryScore';
import { CharacterList } from '@/components/CharacterList';

export function StoryWriter() {
  const { generateStory, loading, error } = useStoryGeneration();
  const [userId] = useState(() => `user_${Date.now()}`);

  // Story state
  const [prompt, setPrompt] = useState('');
  const [generatedText, setGeneratedText] = useState('');

  // Settings state
  const [genre, setGenre] = useState<'action' | 'horror' | 'scifi'>('scifi');
  const [twist, setTwist] = useState<string | null>(null);
  const [temperature, setTemperature] = useState(0.8);
  const [maxTokens, setMaxTokens] = useState(300);
  const [refine, setRefine] = useState(false);
  const [measure, setMeasure] = useState(true);

  // Result state
  const [detectedChars, setDetectedChars] = useState<string[]>([]);
  const [persistedChars, setPersistedChars] = useState<string[]>([]);
  const [score, setScore] = useState<number | null>(null);

  const handleGenerate = async () => {
    if (!prompt.trim()) {
      alert('Please enter a story prompt');
      return;
    }

    const request: GenerateStoryRequest = {
      user_id: userId,
      story: prompt,
      genre,
      twist: twist as any,
      refine,
      measure,
      temperature,
      max_tokens: maxTokens,
    };

    const result = await generateStory(request);

    if (result) {
      setGeneratedText(result.generated_text);
      setDetectedChars(result.detected_characters);
      setPersistedChars(result.persisted_characters);
      setScore(result.score);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Left Panel: Settings */}
      <div className="lg:col-span-1 space-y-4">
        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="font-semibold mb-4">Story Settings</h3>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Genre</label>
              <GenreSelect
                value={genre}
                onChange={setGenre}
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Twist Type</label>
              <TwistSelector
                value={twist}
                onChange={setTwist}
              />
            </div>

            <StorySettings
              temperature={temperature}
              onTemperatureChange={setTemperature}
              maxTokens={maxTokens}
              onMaxTokensChange={setMaxTokens}
              refine={refine}
              onRefineChange={setRefine}
              measure={measure}
              onMeasureChange={setMeasure}
            />

            <button
              onClick={handleGenerate}
              disabled={loading}
              className="w-full bg-primary text-white py-2 rounded font-medium disabled:opacity-50"
            >
              {loading ? 'Generating...' : 'Generate Story'}
            </button>

            {error && (
              <div className="bg-red-100 border border-red-400 text-red-700 px-3 py-2 rounded text-sm">
                {error}
              </div>
            )}
          </div>
        </div>

        {score !== null && (
          <StoryScore score={score} />
        )}

        {persistedChars.length > 0 && (
          <div className="bg-white p-4 rounded-lg shadow">
            <CharacterList
              detected={detectedChars}
              persisted={persistedChars}
            />
          </div>
        )}
      </div>

      {/* Right Panel: Story */}
      <div className="lg:col-span-2 space-y-4">
        {/* Input */}
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Enter your story prompt..."
          className="w-full h-24 p-3 border rounded-lg resize-none"
        />

        {/* Output */}
        {generatedText && (
          <div className="bg-white p-4 rounded-lg shadow">
            <h3 className="font-semibold mb-2">Generated Story</h3>
            <p className="text-gray-700 whitespace-pre-wrap leading-relaxed">
              {generatedText}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
```

---

## Migration from Legacy Endpoint

### Before (Legacy)
```typescript
const response = await fetch('/api/v1/story/continue', {
  method: 'POST',
  body: JSON.stringify({
    story: prompt,
    genre: genre,
  }),
});
```

### After (New)
```typescript
const response = await fetch('/api/v1/story/generate', {
  method: 'POST',
  body: JSON.stringify({
    user_id: userId,      // NEW: required
    story: prompt,
    genre: genre,
    twist: undefined,     // NEW: optional
    refine: false,        // NEW: optional
    measure: true,        // NEW: optional
    temperature: 0.8,     // NEW: optional
    max_tokens: 300,      // NEW: optional
  }),
});
```

**Backward Compatibility**: The old endpoint still works. Migrate at your own pace.

---

## Best Practices

### 1. Session Management
```typescript
// Generate unique session ID per user
const userId = `user_${auth.userId}_${Date.now()}`;

// OR reuse across multiple requests in same session
const sessionId = useSessionId();  // Hook that persists
```

### 2. Error Handling
```typescript
try {
  const result = await generateStory(request);
  if (!result) {
    // Error already set by hook
    return;
  }
  // Use result
} catch (err) {
  // Shouldn't happen if hook is used correctly
  console.error('Unexpected error:', err);
}
```

### 3. Loading States
```typescript
<button disabled={loading}>
  {loading ? '🕐 Generating...' : 'Generate Story'}
</button>

{loading && <ProgressBar />}
```

### 4. Latency Optimization
```typescript
// Pre-generate while user refines prompt
const preGenerate = useCallback(() => {
  if (prompt.length > 20) {
    refetch();  // Background request
  }
}, [prompt]);

useEffect(() => {
  const timer = setTimeout(preGenerate, 1000);
  return () => clearTimeout(timer);
}, [prompt, preGenerate]);
```

---

## Troubleshooting

### "Cannot POST /api/v1/story/generate"
- Check backend is running: `http://localhost:8000/docs`
- Check CORS settings in backend `.env`
- Check frontend API URL in config

### "user_id is required"
- Make sure to include `user_id` in request
- `user_id` cannot be empty string

### Empty generated_text
- Check prompt length (minimum 10 chars)
- Check model is loaded successfully
- Check GPU/CPU has enough memory

### Timeout on generation
- Reduce `max_tokens` (try 200 instead of 300)
- Check backend logs for errors
- Try with `refine: false` for faster generation

---

## Performance Tips

1. **Debounce rapid requests**: Add 1-2s delay between requests
2. **Cache results**: Store user prompts + responses locally
3. **Lazy load settings panel**: Only show advanced options if user clicks
4. **Disable buttons during generation**: Prevent double submissions
5. **Show character hints**: Display persisted characters to aid user input

---

## Next Steps

1. ✅ Copy the hooks and components from this guide
2. ✅ Update your API client library
3. ✅ Add TypeScript types from this guide
4. ✅ Test with the new endpoint
5. ✅ Deploy when ready
6. ✅ Deprecate old endpoint after 1-2 versions

---

For more details, see:
- [API_REFERENCE.md](./API_REFERENCE.md)
- [IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md)
