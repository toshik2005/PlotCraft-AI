# API Documentation
## PlotCraft-AI Backend API

Base URL: `http://localhost:8000/api/v1`

### Story Generation

#### Continue Story
**Endpoint:** `POST /story/continue`

**Request Body:**
```json
{
  "text": "Your story text here...",
  "max_length": 150,
  "temperature": 0.8
}
```

**Response:**
```json
{
  "success": true,
  "message": "Story continuation generated successfully",
  "data": {
    "original_text": "...",
    "generated_text": "...",
    "full_story": "...",
    "input_length": 50,
    "generated_length": 100
  }
}
```

### Genre Detection

#### Detect Genre
**Endpoint:** `POST /genre/detect`

**Request Body:**
```json
{
  "text": "Story text to analyze..."
}
```

**Response:**
```json
{
  "success": true,
  "message": "Genre detected successfully",
  "data": {
    "genre": "horror",
    "confidence": 0.85,
    "all_probabilities": {
      "horror": 0.85,
      "scifi": 0.10,
      ...
    }
  }
}
```

### Plot Twist

#### Generate Twist
**Endpoint:** `POST /twist/generate`

**Request Body:**
```json
{
  "text": "Story text...",
  "twist_type": "unexpected"
}
```

**Twist Types:** `unexpected`, `reversal`, `revelation`, `betrayal`, `discovery`

**Response:**
```json
{
  "success": true,
  "message": "Twist generated successfully",
  "data": {
    "twist": "Generated twist text...",
    "twist_type": "unexpected",
    "full_story_with_twist": "...",
    "prompt_used": "Suddenly, something unexpected happened:"
  }
}
```

### Story Scoring

#### Score Story
**Endpoint:** `POST /score/story`

**Request Body:**
```json
{
  "text": "Story text to score..."
}
```

**Response:**
```json
{
  "success": true,
  "message": "Story scored successfully",
  "data": {
    "total_score": 75,
    "breakdown": {
      "sentiment": 30.0,
      "length": 20.0,
      "complexity": 15.0,
      "creativity": 10.0
    },
    "metrics": {
      "word_count": 150,
      "sentence_count": 8,
      "sentiment_polarity": 0.5,
      "unique_words_ratio": 0.7
    }
  }
}
```

#### Extract Characters
**Endpoint:** `POST /score/characters`

**Request Body:**
```json
{
  "text": "Story with character names..."
}
```

**Response:**
```json
{
  "success": true,
  "message": "Characters extracted successfully",
  "data": {
    "characters": ["John", "Mary", "Sarah"],
    "count": 3
  }
}
```

### Error Responses

**400 Bad Request:**
```json
{
  "detail": "Error message"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Internal server error: Error message"
}
```

### Interactive Documentation

Visit `http://localhost:8000/docs` for Swagger UI documentation.

Visit `http://localhost:8000/redoc` for ReDoc documentation.
