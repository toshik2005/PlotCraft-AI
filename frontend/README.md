# PlotCraft-AI Frontend

Next.js frontend application for AI-powered story generation and analysis.

## Features

- 🎮 **Story Generation**: Continue stories using AI text generation
- 🎭 **Genre Detection**: Automatically detect story genre with confidence scores
- 🎪 **Plot Twists**: Generate unexpected plot twists to enhance narratives
- ⭐ **Story Scoring**: Score stories based on sentiment, length, complexity, and creativity
- 👥 **Character Extraction**: Extract character names from stories using NLP
- 🌓 **Dark Mode**: Built-in dark mode support
- 📱 **Responsive Design**: Mobile-friendly interface

## Tech Stack

- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: Radix UI
- **Animations**: Framer Motion
- **Icons**: Lucide React
- **Authentication**: NextAuth.js
- **State Management**: React Hooks

## Prerequisites

- Node.js 18+ 
- npm or yarn or pnpm

## Setup

1. Install dependencies:
```bash
npm install
# or
yarn install
# or
pnpm install
```

2. Create a `.env.local` file in the frontend directory:
```env
BACKEND_API_URL=http://localhost:8000
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-secret-key-here
```

3. Run the development server:
```bash
npm run dev
# or
yarn dev
# or
pnpm dev
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm start` - Start production server
- `npm run lint` - Run ESLint

## Project Structure

```
frontend/
├── app/                    # Next.js App Router pages
│   ├── layout.tsx         # Root layout
│   ├── page.tsx           # Home page
│   └── api/               # API routes
├── components/             # React components
│   ├── ui/                # Reusable UI components
│   └── ...                # Feature components
├── lib/                    # Utility functions
├── types/                  # TypeScript type definitions
├── public/                 # Static assets
├── tailwind.config.ts      # Tailwind CSS configuration
├── tsconfig.json           # TypeScript configuration
└── next.config.ts          # Next.js configuration
```

## Environment Variables

- `BACKEND_API_URL` - Backend API base URL (default: http://localhost:8000)
- `NEXTAUTH_URL` - NextAuth.js callback URL
- `NEXTAUTH_SECRET` - Secret key for NextAuth.js encryption

## Development

The app uses Next.js App Router with TypeScript. Key features:

- **Server Components**: Default React Server Components for better performance
- **Client Components**: Marked with `"use client"` directive when needed
- **API Routes**: Next.js API routes for backend communication
- **Middleware**: Authentication and routing middleware

## Building for Production

```bash
npm run build
npm start
```

## Deployment

The frontend can be deployed to:
- **Vercel** (recommended for Next.js)
- **Netlify**
- **AWS Amplify**
- Any Node.js hosting platform

Make sure to set environment variables in your deployment platform.

## API Integration

The frontend communicates with the FastAPI backend at `BACKEND_API_URL`. See the backend README for API documentation.

## License

MIT
