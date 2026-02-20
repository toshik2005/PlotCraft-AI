"""
Step 2: Build word‑level vocabulary from cleaned text.

Special tokens: <PAD>=0, <UNK>=1, <GENRE_SCIFI>=2.
Saves backend/ml/artifacts/vocab.pkl and prints vocab size.

Run from backend directory:
    python -m ml.preprocessing.tokenizer_builder
"""

import pickle
from pathlib import Path
from collections import Counter

BACKEND_ROOT = Path(__file__).resolve().parents[2]
CLEANED_PATH = BACKEND_ROOT / "ml" / "data" / "processed" / "cleaned_scifi.txt"
VOCAB_PATH = BACKEND_ROOT / "ml" / "artifacts" / "vocab.pkl"

# Special tokens (order defines their indices)
PAD = "<PAD>"
UNK = "<UNK>"
GENRE_SCIFI = "<GENRE_SCIFI>"
SPECIAL_TOKENS = [PAD, UNK, GENRE_SCIFI]


def build_vocabulary(
    text_path: Path = CLEANED_PATH,
    vocab_path: Path = VOCAB_PATH,
    min_freq: int = 1,
) -> dict[str, int]:
    """
    Build word‑level vocabulary from cleaned text file.

    - Special tokens first: <PAD>=0, <UNK>=1, <GENRE_SCIFI>=2
    - Then all words appearing at least min_freq times, sorted by frequency (desc)
    """
    if not text_path.exists():
        raise FileNotFoundError(f"Cleaned text not found: {text_path}. Run clean_data.py first.")

    with open(text_path, "r", encoding="utf-8") as f:
        text = f.read()

    words = text.split()
    counter = Counter(words)

    # Special tokens get indices 0, 1, 2
    vocab: dict[str, int] = {}
    for idx, tok in enumerate(SPECIAL_TOKENS):
        vocab[tok] = idx

    # Then add words that meet min_freq, sorted by frequency (most common first)
    next_idx = len(SPECIAL_TOKENS)
    for word, freq in counter.most_common():
        if freq >= min_freq and word not in vocab:
            vocab[word] = next_idx
            next_idx += 1

    vocab_path.parent.mkdir(parents=True, exist_ok=True)
    with open(vocab_path, "wb") as f:
        pickle.dump(vocab, f)

    print(f"Vocabulary size: {len(vocab)} (saved to {vocab_path})")
    return vocab


def main() -> None:
    build_vocabulary()


if __name__ == "__main__":
    main()
