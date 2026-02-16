import React, { useState } from 'react';
import StoryInput from '../components/StoryInput';
import StoryOutput from '../components/StoryOutput';
import GenreSelector from '../components/GenreSelector';
import TwistButton from '../components/TwistButton';
import ScoreCard from '../components/ScoreCard';
import { storyAPI } from '../services/api';
import './Home.css';

const Home = () => {
  const [story, setStory] = useState('');
  const [generatedStory, setGeneratedStory] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [currentStory, setCurrentStory] = useState('');

  const handleStorySubmit = async (text, maxLength, temperature) => {
    setIsLoading(true);
    setError(null);
    setStory(text);
    setCurrentStory(text);

    try {
      const response = await storyAPI.continueStory(text, maxLength, temperature);
      if (response.success && response.data) {
        setGeneratedStory(response.data);
        setCurrentStory(response.data.full_story);
      } else {
        setError('Failed to generate story continuation');
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'An error occurred while generating the story');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="home-container">
      <div className="home-header">
        <h1>🎮 PlotCraft AI</h1>
        <p className="subtitle">AI-powered story generation and analysis</p>
      </div>

      <div className="content-wrapper">
        <div className="main-content">
          <StoryInput onStorySubmit={handleStorySubmit} />
          
          <StoryOutput
            story={story}
            generatedText={generatedStory?.generated_text}
            isLoading={isLoading}
            error={error}
          />
        </div>

        <div className="sidebar">
          <GenreSelector storyText={currentStory || story} />
          <TwistButton storyText={currentStory || story} />
          <ScoreCard storyText={currentStory || story} autoScore={true} />
        </div>
      </div>
    </div>
  );
};

export default Home;
