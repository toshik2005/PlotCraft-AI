import React, { useState } from 'react';
import { genreAPI } from '../services/api';
import './GenreSelector.css';

const GenreSelector = ({ storyText, onGenreDetected }) => {
  const [genre, setGenre] = useState(null);
  const [confidence, setConfidence] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleDetectGenre = async () => {
    if (!storyText || storyText.trim().length < 5) {
      setError('Please enter at least 5 characters to detect genre');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await genreAPI.detectGenre(storyText);
      if (response.success && response.data) {
        setGenre(response.data.genre);
        setConfidence(response.data.confidence);
        if (onGenreDetected) {
          onGenreDetected(response.data);
        }
      } else {
        setError('Failed to detect genre');
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'An error occurred while detecting genre');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="genre-selector-container">
      <div className="genre-header">
        <h3>🎭 Genre Detection</h3>
        <button
          onClick={handleDetectGenre}
          disabled={isLoading || !storyText}
          className="btn-detect"
        >
          {isLoading ? 'Detecting...' : 'Detect Genre'}
        </button>
      </div>

      {error && (
        <div className="error-message">
          <span>⚠️</span>
          <span>{error}</span>
        </div>
      )}

      {genre && (
        <div className="genre-result">
          <div className="genre-badge">
            <span className="genre-name">{genre}</span>
            <span className="confidence">{(confidence * 100).toFixed(1)}% confidence</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default GenreSelector;
