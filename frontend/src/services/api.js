import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Story API
export const storyAPI = {
  continueStory: async (text, maxLength = 150, temperature = 0.8) => {
    const response = await api.post('/story/continue', {
      text,
      max_length: maxLength,
      temperature,
    });
    return response.data;
  },
};

// Genre API
export const genreAPI = {
  detectGenre: async (text) => {
    const response = await api.post('/genre/detect', { text });
    return response.data;
  },
};

// Twist API
export const twistAPI = {
  generateTwist: async (text, twistType = 'unexpected') => {
    const response = await api.post('/twist/generate', {
      text,
      twist_type: twistType,
    });
    return response.data;
  },
};

// Score API
export const scoreAPI = {
  scoreStory: async (text) => {
    const response = await api.post('/score/story', { text });
    return response.data;
  },
  extractCharacters: async (text) => {
    const response = await api.post('/score/characters', { text });
    return response.data;
  },
};

export default api;
