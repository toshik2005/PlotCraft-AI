# Frontend Setup Guide

## Quick Start

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Set up environment variables:**
   Create a `.env.local` file in the `frontend` directory:
   ```env
   BACKEND_API_URL=http://localhost:8000
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```

4. **Open your browser:**
   Navigate to [http://localhost:3000](http://localhost:3000)

## Backend Connection

Make sure the backend is running on `http://localhost:8000` before using the frontend.

The frontend connects to the following backend endpoints:
- `POST /api/v1/story/continue` - Story continuation pipeline
- `POST /api/v1/genre/detect` - Genre detection
- `POST /api/v1/twist/generate` - Plot twist generation
- `POST /api/v1/score/story` - Story scoring
- `POST /api/v1/score/characters` - Character extraction

## Features

- ✅ Story continuation with AI
- ✅ Genre detection
- ✅ Plot twist generation
- ✅ Story scoring
- ✅ Character extraction
- ✅ Dark mode support
- ✅ Responsive design

## Troubleshooting

### CORS Errors
If you encounter CORS errors, make sure:
1. Backend CORS is configured to allow `http://localhost:3000`
2. Backend is running on `http://localhost:8000`
3. Environment variable `BACKEND_API_URL` is set correctly

### API Connection Issues
- Check that the backend server is running
- Verify the `BACKEND_API_URL` in `.env.local`
- Check browser console for detailed error messages
