# Product Requirements Document (PRD)
## PlotCraft-AI

### Overview
PlotCraft-AI is an AI-powered web application that helps users create, enhance, and analyze stories using machine learning models.

### Goals
- Enable users to generate story continuations using AI
- Automatically detect story genres
- Generate plot twists to enhance narratives
- Score stories based on multiple criteria
- Extract characters from stories

### Features

#### 1. Story Generation
- **Input**: User-provided story text
- **Output**: AI-generated story continuation
- **Controls**: Max length, temperature for creativity

#### 2. Genre Detection
- **Input**: Story text
- **Output**: Detected genre with confidence score
- **Genres**: Horror, Sci-Fi, Comedy, Fantasy, Mystery, Romance, Thriller

#### 3. Plot Twist Generation
- **Input**: Story text and twist type
- **Output**: Generated plot twist
- **Types**: Unexpected, Reversal, Revelation, Betrayal, Discovery

#### 4. Story Scoring
- **Input**: Story text
- **Output**: Score (0-100) with breakdown
- **Criteria**: Sentiment, Length, Complexity, Creativity

#### 5. Character Extraction
- **Input**: Story text
- **Output**: List of character names found

### Technical Requirements
- **Backend**: FastAPI (Python)
- **Frontend**: React (JavaScript)
- **ML Models**: Transformers (GPT-2), spaCy (NER), scikit-learn (Genre)
- **API**: RESTful API with JSON responses

### User Experience
- Clean, modern UI
- Real-time feedback
- Responsive design
- Error handling

### Success Metrics
- Story generation quality
- Genre detection accuracy
- User engagement
- API response time
