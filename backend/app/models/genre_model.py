"""Genre detection model."""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from typing import List
import joblib
import os

from app.core.constants import GENRE_TRAINING_DATA


class GenreModel:
    """Genre classification model."""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer()
        self.model = LogisticRegression(max_iter=1000)
        self._is_trained = False
    
    def _prepare_training_data(self) -> tuple[List[str], List[str]]:
        """Prepare training data from constants."""
        texts = []
        genres = []
        
        for genre, examples in GENRE_TRAINING_DATA.items():
            texts.extend(examples)
            genres.extend([genre] * len(examples))
        
        return texts, genres
    
    def train(self):
        """Train the genre classification model."""
        texts, genres = self._prepare_training_data()
        
        X = self.vectorizer.fit_transform(texts)
        self.model.fit(X, genres)
        self._is_trained = True
    
    def predict(self, text: str) -> str:
        """Predict genre for given text."""
        if not self._is_trained:
            self.train()
        
        X_test = self.vectorizer.transform([text])
        prediction = self.model.predict(X_test)[0]
        return prediction
    
    def predict_proba(self, text: str) -> dict[str, float]:
        """Get probability distribution over genres."""
        if not self._is_trained:
            self.train()
        
        X_test = self.vectorizer.transform([text])
        probabilities = self.model.predict_proba(X_test)[0]
        
        genre_probs = dict(zip(self.model.classes_, probabilities))
        return genre_probs
    
    def save(self, filepath: str):
        """Save model to file."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        joblib.dump({
            'vectorizer': self.vectorizer,
            'model': self.model,
            'is_trained': self._is_trained
        }, filepath)
    
    def load(self, filepath: str):
        """Load model from file."""
        data = joblib.load(filepath)
        self.vectorizer = data['vectorizer']
        self.model = data['model']
        self._is_trained = data['is_trained']


# Global model instance
genre_model = GenreModel()
