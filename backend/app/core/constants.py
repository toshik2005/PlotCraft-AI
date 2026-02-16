"""Application constants."""

# Genre labels
GENRES = ["horror", "scifi", "comedy", "fantasy", "mystery", "romance", "thriller"]

# Genre training examples
GENRE_TRAINING_DATA = {
    "horror": [
        "ghost in dark house",
        "vampire in cemetery",
        "zombie apocalypse",
        "haunted mansion",
        "demonic possession"
    ],
    "scifi": [
        "robot flying in space",
        "alien spaceship attack",
        "time travel machine",
        "cyberpunk future city",
        "mars colony mission"
    ],
    "comedy": [
        "funny school prank",
        "awkward first date",
        "misunderstanding at work",
        "pet causing chaos",
        "family vacation disaster"
    ],
    "fantasy": [
        "kingdom war and sword",
        "magic spell casting",
        "dragon and knight",
        "elf forest adventure",
        "wizard tower quest"
    ],
    "mystery": [
        "detective solving crime",
        "missing person case",
        "secret code breaking",
        "suspicious neighbor",
        "hidden treasure map"
    ],
    "romance": [
        "love story reunion",
        "wedding planning",
        "second chance romance",
        "enemies to lovers",
        "long distance relationship"
    ],
    "thriller": [
        "chase scene escape",
        "kidnapping rescue",
        "spy mission danger",
        "serial killer hunt",
        "conspiracy unraveling"
    ]
}

# Story scoring weights
SCORING_WEIGHTS = {
    "sentiment": 40,
    "length": 20,
    "complexity": 20,
    "creativity": 20
}

# Default story parameters
DEFAULT_STORY_PARAMS = {
    "max_length": 150,
    "num_return_sequences": 1,
    "temperature": 0.8,
    "top_p": 0.9
}
