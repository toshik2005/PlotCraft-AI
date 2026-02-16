import React, { useState, useEffect } from 'react';
import { scoreAPI } from '../services/api';
import './ScoreCard.css';

const ScoreCard = ({ storyText, autoScore = false }) => {
  const [score, setScore] = useState(null);
  const [characters, setCharacters] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (autoScore && storyText && storyText.trim().length >= 10) {
      handleScoreStory();
      handleExtractCharacters();
    }
  }, [autoScore, storyText]);

  const handleScoreStory = async () => {
    if (!storyText || storyText.trim().length < 10) {
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await scoreAPI.scoreStory(storyText);
      if (response.success && response.data) {
        setScore(response.data);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'An error occurred while scoring');
    } finally {
      setIsLoading(false);
    }
  };

  const handleExtractCharacters = async () => {
    if (!storyText || storyText.trim().length < 5) {
      return;
    }

    try {
      const response = await scoreAPI.extractCharacters(storyText);
      if (response.success && response.data) {
        setCharacters(response.data);
      }
    } catch (err) {
      // Silently fail for character extraction
      console.error('Character extraction failed:', err);
    }
  };

  const getScoreColor = (scoreValue) => {
    if (scoreValue >= 80) return '#27ae60';
    if (scoreValue >= 60) return '#f39c12';
    return '#e74c3c';
  };

  if (!score && !isLoading && !autoScore) {
    return (
      <div className="score-card-container">
        <button onClick={handleScoreStory} className="btn-score">
          Score Story
        </button>
      </div>
    );
  }

  return (
    <div className="score-card-container">
      {isLoading && (
        <div className="loading">Calculating score...</div>
      )}

      {error && (
        <div className="error-message">
          <span>⚠️</span>
          <span>{error}</span>
        </div>
      )}

      {score && (
        <>
          <div className="score-header">
            <h3>⭐ Story Score</h3>
            <div
              className="score-circle"
              style={{ borderColor: getScoreColor(score.total_score) }}
            >
              <span className="score-value">{score.total_score}</span>
              <span className="score-max">/100</span>
            </div>
          </div>

          <div className="score-breakdown">
            <h4>Breakdown</h4>
            <div className="breakdown-items">
              <div className="breakdown-item">
                <span className="label">Sentiment</span>
                <span className="value">{score.breakdown.sentiment.toFixed(1)}</span>
              </div>
              <div className="breakdown-item">
                <span className="label">Length</span>
                <span className="value">{score.breakdown.length.toFixed(1)}</span>
              </div>
              <div className="breakdown-item">
                <span className="label">Complexity</span>
                <span className="value">{score.breakdown.complexity.toFixed(1)}</span>
              </div>
              <div className="breakdown-item">
                <span className="label">Creativity</span>
                <span className="value">{score.breakdown.creativity.toFixed(1)}</span>
              </div>
            </div>
          </div>

          {characters && characters.characters.length > 0 && (
            <div className="characters-section">
              <h4>👥 Characters Found</h4>
              <div className="characters-list">
                {characters.characters.map((char, idx) => (
                  <span key={idx} className="character-tag">
                    {char}
                  </span>
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default ScoreCard;
