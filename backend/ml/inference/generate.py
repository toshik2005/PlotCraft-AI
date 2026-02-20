"""
Load trained LSTM model and vocab; generate text with temperature sampling.

Supports optional prefix <GENRE_SCIFI>. Generates 100 words after the prompt.

Run from backend (or use as module):
    from ml.inference.generate import generate_story
    text = generate_story("the ship entered", num_words=100, temperature=0.8)
"""

from pathlib import Path
from typing import Optional

import pickle
import torch

from ml.training.model import LSTMLanguageModel

BACKEND_ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS_DIR = BACKEND_ROOT / "ml" / "artifacts"
MODEL_PATH = ARTIFACTS_DIR / "scifi_model.pt"
VOCAB_PATH = ARTIFACTS_DIR / "vocab.pkl"

GENRE_SCIFI = "<GENRE_SCIFI>"
SEQ_LEN = 30

_device: Optional[torch.device] = None


def _get_device() -> torch.device:
    global _device
    if _device is None:
        _device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    return _device


def _load_vocab() -> dict:
    with open(VOCAB_PATH, "rb") as f:
        return pickle.load(f)


def _load_model(vocab_size: int) -> LSTMLanguageModel:
    model = LSTMLanguageModel(
        vocab_size=vocab_size,
        embedding_dim=256,
        hidden_size=512,
        num_layers=2,
        dropout=0.0,  # no dropout at inference
    )
    state = torch.load(MODEL_PATH, map_location=_get_device())
    model.load_state_dict(state)
    model.eval()
    return model.to(_get_device())


def generate_story(
    prompt: str,
    num_words: int = 100,
    temperature: float = 0.8,
    use_genre_prefix: bool = True,
) -> str:
    """
    Generate the next `num_words` words after `prompt` using temperature sampling.

    If use_genre_prefix is True and prompt does not already start with <GENRE_SCIFI>,
    we prepend <GENRE_SCIFI> to the token sequence so the model conditions on genre.
    """
    if not MODEL_PATH.exists() or not VOCAB_PATH.exists():
        raise FileNotFoundError(
            "Artifacts not found. Run preprocessing and training first:\n"
            "  python -m ml.preprocessing.clean_data\n"
            "  python -m ml.preprocessing.tokenizer_builder\n"
            "  python -m ml.training.train"
        )

    vocab = _load_vocab()
    inv_vocab = {v: k for k, v in vocab.items()}
    unk_id = vocab.get("<UNK>", 1)
    genre_id = vocab.get(GENRE_SCIFI)

    model = _load_model(len(vocab))
    device = _get_device()

    # Tokenize prompt (lowercase, split)
    words = prompt.strip().lower().split()
    if use_genre_prefix and genre_id is not None and (not words or words[0] != GENRE_SCIFI.strip("<>")):
        words = [GENRE_SCIFI] + words
    token_ids = [vocab.get(w, unk_id) for w in words]

    # Pad or trim to SEQ_LEN for initial LSTM input
    if len(token_ids) < SEQ_LEN:
        pad_id = vocab.get("<PAD>", 0)
        token_ids = [pad_id] * (SEQ_LEN - len(token_ids)) + token_ids
    else:
        token_ids = token_ids[-SEQ_LEN:]

    generated: list[str] = []
    with torch.no_grad():
        for _ in range(num_words):
            x = torch.tensor([token_ids], dtype=torch.long, device=device)
            logits = model(x)  # (1, seq_len, vocab_size)
            next_logits = logits[0, -1, :].float()

            if temperature <= 0:
                next_id = int(logits[0, -1, :].argmax().item())
            else:
                next_logits = next_logits / temperature
                probs = torch.softmax(next_logits, dim=-1)
                next_id = int(torch.multinomial(probs, 1).item())

            word = inv_vocab.get(next_id, "<UNK>")
            generated.append(word)

            # Shift window: drop first, append new
            token_ids = token_ids[1:] + [next_id]

    return " ".join(generated)


# Backwards-compatible alias for existing app integration
def generate(prompt: str, max_tokens: int = 100, temperature: float = 0.8) -> str:
    return generate_story(prompt, num_words=max_tokens, temperature=temperature)
