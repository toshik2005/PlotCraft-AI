import React from 'react';
import './StoryOutput.css';

const StoryOutput = ({ story, generatedText, isLoading, error }) => {
  if (isLoading) {
    return (
      <div className="story-output-container">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Generating your story...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="story-output-container">
        <div className="error-message">
          <span className="error-icon">⚠️</span>
          <p>{error}</p>
        </div>
      </div>
    );
  }

  if (!generatedText) {
    return null;
  }

  return (
    <div className="story-output-container">
      <div className="output-section">
        <h3 className="section-title">📚 AI Continuation</h3>
        <div className="story-content">
          <div className="original-text">
            <strong>Original:</strong>
            <p>{story}</p>
          </div>
          <div className="generated-text">
            <strong>Generated:</strong>
            <p>{generatedText}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StoryOutput;
