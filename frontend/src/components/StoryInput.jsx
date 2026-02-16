import React, { useState } from 'react';
import './StoryInput.css';

const StoryInput = ({ onStorySubmit, placeholder = "Write your story here..." }) => {
  const [story, setStory] = useState('');
  const [maxLength, setMaxLength] = useState(150);
  const [temperature, setTemperature] = useState(0.8);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (story.trim()) {
      onStorySubmit(story, maxLength, temperature);
    }
  };

  const handleClear = () => {
    setStory('');
  };

  return (
    <div className="story-input-container">
      <form onSubmit={handleSubmit} className="story-form">
        <div className="input-group">
          <label htmlFor="story-text">Your Story</label>
          <textarea
            id="story-text"
            value={story}
            onChange={(e) => setStory(e.target.value)}
            placeholder={placeholder}
            rows={8}
            className="story-textarea"
            required
          />
        </div>

        <div className="controls-group">
          <div className="control-item">
            <label htmlFor="max-length">Max Length: {maxLength}</label>
            <input
              id="max-length"
              type="range"
              min="50"
              max="500"
              value={maxLength}
              onChange={(e) => setMaxLength(Number(e.target.value))}
              className="slider"
            />
          </div>

          <div className="control-item">
            <label htmlFor="temperature">Temperature: {temperature.toFixed(1)}</label>
            <input
              id="temperature"
              type="range"
              min="0.1"
              max="2.0"
              step="0.1"
              value={temperature}
              onChange={(e) => setTemperature(Number(e.target.value))}
              className="slider"
            />
          </div>
        </div>

        <div className="button-group">
          <button type="submit" className="btn btn-primary">
            Continue Story
          </button>
          <button type="button" onClick={handleClear} className="btn btn-secondary">
            Clear
          </button>
        </div>
      </form>
    </div>
  );
};

export default StoryInput;
