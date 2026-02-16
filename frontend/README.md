# PlotCraft-AI Frontend

React frontend for AI-powered story generation and analysis.

## Features

- **Story Input**: Write and continue stories with AI
- **Genre Detection**: Automatically detect story genre
- **Plot Twists**: Add unexpected twists to your story
- **Story Scoring**: Get detailed scores and character extraction

## Setup

### Prerequisites

- Node.js 16+ and npm

### Installation

1. Install dependencies:
```bash
npm install
```

2. Create `.env` file (optional):
```bash
REACT_APP_API_URL=http://localhost:8000/api/v1
```

3. Start the development server:
```bash
npm start
```

The app will open at `http://localhost:3000`

## Build for Production

```bash
npm run build
```

This creates an optimized production build in the `build/` folder.

## Project Structure

```
frontend/
├── public/              # Static files
├── src/
│   ├── components/     # React components
│   ├── pages/          # Page components
│   ├── services/       # API services
│   ├── styles/         # CSS files
│   ├── App.jsx         # Main app component
│   └── index.js        # Entry point
├── package.json
└── README.md
```

## Components

- **StoryInput**: Text area for story input with controls
- **StoryOutput**: Display generated story continuation
- **GenreSelector**: Genre detection component
- **TwistButton**: Plot twist generation
- **ScoreCard**: Story scoring and character extraction

## Development

Run tests:
```bash
npm test
```

Build for production:
```bash
npm run build
```
