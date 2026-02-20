"""
PyTorch Dataset for next‑word prediction.

Reads cleaned text and vocab, converts text into sequences of length 30;
each sample is (input_seq, target_word) for training the LSTM language model.
"""

from pathlib import Path
from typing import Tuple

import pickle
import torch
from torch.utils.data import Dataset

BACKEND_ROOT = Path(__file__).resolve().parents[2]
CLEANED_PATH = BACKEND_ROOT / "ml" / "data" / "processed" / "cleaned_scifi.txt"
VOCAB_PATH = BACKEND_ROOT / "ml" / "artifacts" / "vocab.pkl"

# Index of <UNK> in vocab (used for out-of-vocab words)
UNK_ID = 1

# Sequence length (number of input words; target is the next single word)
SEQ_LEN = 30


class SciFiDataset(Dataset):
    """
    Dataset of (input sequence, target word) for next-word prediction.

    - input_seq: tensor of shape (SEQ_LEN,) with token ids
    - target_word: scalar tensor with the next word's id
    """

    def __init__(
        self,
        text_path: Path = CLEANED_PATH,
        vocab_path: Path = VOCAB_PATH,
        seq_len: int = SEQ_LEN,
    ) -> None:
        with open(vocab_path, "rb") as f:
            self.vocab = pickle.load(f)
        self.seq_len = seq_len
        self.unk_id = self.vocab.get("<UNK>", UNK_ID)

        with open(text_path, "r", encoding="utf-8") as f:
            text = f.read()
        words = text.split()
        # Convert to token ids; words not in vocab -> UNK
        self.token_ids = [
            self.vocab.get(w, self.unk_id)
            for w in words
        ]

        # Number of samples: every sliding window of length seq_len has one target (the next word)
        self.num_samples = max(0, len(self.token_ids) - self.seq_len)

    def __len__(self) -> int:
        return self.num_samples

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        # Input: tokens [idx, idx+1, ..., idx+seq_len-1]
        # Target: token at idx+seq_len
        start = idx
        end_input = start + self.seq_len
        input_ids = self.token_ids[start:end_input]
        target_id = self.token_ids[end_input]

        input_seq = torch.tensor(input_ids, dtype=torch.long)
        target_word = torch.tensor(target_id, dtype=torch.long)
        return input_seq, target_word


def load_vocab(vocab_path: Path = VOCAB_PATH) -> dict:
    """Load vocabulary from artifacts (for training script)."""
    with open(vocab_path, "rb") as f:
        return pickle.load(f)
