"""Application constants (scoring weights, genre training data, etc.)."""

# Weights for story scoring (total scaled to 0–100)
SCORING_WEIGHTS = {
    "sentiment": 25,
    "length": 25,
    "complexity": 25,
    "creativity": 25,
}

# Minimal genre examples for TF-IDF + LogisticRegression genre model
GENRE_TRAINING_DATA = {
    "fantasy": [
        "The dragon soared over the castle and the wizard cast a spell.",
        "In a land of magic and elves, the hero drew his sword.",
    ],
    "horror": [
        "Something moved in the shadows and the door creaked open.",
        "She heard a whisper in the dark and turned slowly.",
    ],
    "sci-fi": [
        "The spaceship jumped to hyperspace and the crew held on.",
        "On the colony planet, the AI began to ask questions.",
    ],
    "romance": [
        "Their eyes met across the room and her heart skipped.",
        "He had never believed in love at first sight until now.",
    ],
    "mystery": [
        "The detective examined the clue and frowned.",
        "Someone in this house was lying; she was sure of it.",
    ],
}
