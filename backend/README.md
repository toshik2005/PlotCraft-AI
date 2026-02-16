# PlotCraft-AI Backend

FastAPI backend for AI-powered story generation and analysis.

## Features

- **Story Generation**: Continue stories using AI text generation
- **Genre Detection**: Automatically detect story genre
- **Plot Twists**: Generate unexpected plot twists
- **Story Scoring**: Score stories based on multiple criteria
- **Character Extraction**: Extract character names from stories

## Setup

### Prerequisites

- Python 3.9+
- pip

### Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install fastapi uvicorn spacy transformers scikit-learn textblob pydantic pydantic-settings joblib python-multipart python-dotenv torch
```

3. Download spaCy model:
```bash
python -m spacy download en_core_web_sm
```

4. Create `.env` file (copy from `.env.example` or use the provided `.env`)

5. Run the server:
```bash
python -m app.main
# Or
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Story
- `POST /api/v1/story/continue` - Generate story continuation

### Genre
- `POST /api/v1/genre/detect` - Detect story genre

### Twist
- `POST /api/v1/twist/generate` - Generate plot twist

### Score
- `POST /api/v1/score/story` - Score a story
- `POST /api/v1/score/characters` - Extract characters

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI entry point
│   ├── core/                # Configuration
│   ├── api/                 # API routes
│   ├── services/            # Business logic
│   ├── models/              # ML models
│   ├── utils/               # Utilities
│   └── schemas/             # Pydantic schemas
├── tests/                   # Test files
├── requirements.txt
└── README.md
```

## Development

Run tests:
```bash
pytest tests/
```

Format code:
```bash
black app/
```

Lint code:
```bash
flake8 app/
```
