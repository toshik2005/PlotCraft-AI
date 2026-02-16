import React, { useState } from 'react';
import { twistAPI } from '../services/api';
import './TwistButton.css';

const TWIST_TYPES = [
  { value: 'unexpected', label: 'Unexpected', emoji: '⚡' },
  { value: 'reversal', label: 'Reversal', emoji: '🔄' },
  { value: 'revelation', label: 'Revelation', emoji: '💡' },
  { value: 'betrayal', label: 'Betrayal', emoji: '🗡️' },
  { value: 'discovery', label: 'Discovery', emoji: '🔍' },
];

const TwistButton = ({ storyText, onTwistGenerated }) => {
  const [twist, setTwist] = useState(null);
  const [selectedType, setSelectedType] = useState('unexpected');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleGenerateTwist = async () => {
    if (!storyText || storyText.trim().length < 10) {
      setError('Please enter at least 10 characters to generate a twist');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await twistAPI.generateTwist(storyText, selectedType);
      if (response.success && response.data) {
        setTwist(response.data);
        if (onTwistGenerated) {
          onTwistGenerated(response.data);
        }
      } else {
        setError('Failed to generate twist');
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'An error occurred while generating twist');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="twist-button-container">
      <div className="twist-header">
        <h3>🎪 Add a Plot Twist</h3>
        <div className="twist-controls">
          <select
            value={selectedType}
            onChange={(e) => setSelectedType(e.target.value)}
            className="twist-select"
            disabled={isLoading}
          >
            {TWIST_TYPES.map((type) => (
              <option key={type.value} value={type.value}>
                {type.emoji} {type.label}
              </option>
            ))}
          </select>
          <button
            onClick={handleGenerateTwist}
            disabled={isLoading || !storyText}
            className="btn-twist"
          >
            {isLoading ? 'Generating...' : 'Generate Twist'}
          </button>
        </div>
      </div>

      {error && (
        <div className="error-message">
          <span>⚠️</span>
          <span>{error}</span>
        </div>
      )}

      {twist && (
        <div className="twist-result">
          <div className="twist-type-badge">
            {TWIST_TYPES.find(t => t.value === twist.twist_type)?.emoji} {twist.twist_type}
          </div>
          <div className="twist-content">
            <p>{twist.twist}</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default TwistButton;
