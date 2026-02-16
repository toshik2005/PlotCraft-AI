# PlotCraft-AI

AI-powered story generation and analysis platform.

## Features

- 🎮 **Story Generation**: Continue stories using AI text generation
- 🎭 **Genre Detection**: Automatically detect story genre with confidence scores
- 🎪 **Plot Twists**: Generate unexpected plot twists to enhance narratives
- ⭐ **Story Scoring**: Score stories based on sentiment, length, complexity, and creativity
- 👥 **Character Extraction**: Extract character names from stories using NLP

## Project Structure

```
PlotCraft-AI/
├── backend/          # FastAPI backend
├── frontend/         # React frontend
├── docs/             # Documentation
└── README.md
```

## Quick Start

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install fastapi uvicorn spacy transformers scikit-learn textblob pydantic pydantic-settings joblib python-multipart python-dotenv torch
python -m spacy download en_core_web_sm
python -m app.main
```

Backend runs on `http://localhost:8000`

### Frontend Setup

```bash
cd frontend
npm install
npm start
```

Frontend runs on `http://localhost:3000`

## Technology Stack

**Backend:**
- FastAPI
- Transformers (GPT-2)
- spaCy
- scikit-learn
- Pydantic

**Frontend:**
- React
- Axios
- CSS

## Documentation

- [Product Requirements](docs/PRD.md)
- [Architecture](docs/Architecture.md)
- [API Documentation](docs/API_Documentation.md)

## License

MIT
