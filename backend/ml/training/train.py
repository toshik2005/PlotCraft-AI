"""
Train the LSTM language model on cleaned Sci‑Fi text.

Expects:
  - ml/data/processed/cleaned_scifi.txt (from clean_data.py)
  - ml/artifacts/vocab.pkl (from tokenizer_builder.py)

Saves:
  - ml/artifacts/scifi_model.pt

Run from backend directory:
    python -m ml.training.train
Or from backend/ml:
    python training/train.py
"""

from pathlib import Path
import sys

# Allow running as script from backend/ml (e.g. python training/train.py)
_BACKEND = Path(__file__).resolve().parents[2]
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

import torch
from torch.utils.data import DataLoader

from ml.training.dataset import SciFiDataset, load_vocab
from ml.training.model import LSTMLanguageModel

BACKEND_ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS_DIR = BACKEND_ROOT / "ml" / "artifacts"
MODEL_SAVE_PATH = ARTIFACTS_DIR / "scifi_model.pt"

# Training config
BATCH_SIZE = 64
EPOCHS = 15
LR = 1e-3
SEQ_LEN = 30


def main() -> None:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    # Load dataset and vocab
    dataset = SciFiDataset(seq_len=SEQ_LEN)
    vocab = load_vocab()
    vocab_size = len(vocab)

    dataloader = DataLoader(
        dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
        num_workers=0,
        pin_memory=(device.type == "cuda"),
    )

    model = LSTMLanguageModel(
        vocab_size=vocab_size,
        embedding_dim=256,
        hidden_size=512,
        num_layers=2,
        dropout=0.3,
    ).to(device)

    criterion = torch.nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=LR)

    model.train()
    for epoch in range(1, EPOCHS + 1):
        total_loss = 0.0
        num_batches = 0
        for input_seq, target_word in dataloader:
            input_seq = input_seq.to(device)
            target_word = target_word.to(device)

            optimizer.zero_grad()
            # logits: (batch, seq_len, vocab_size); we predict next word from last position
            logits = model(input_seq)
            last_logits = logits[:, -1, :]  # (batch, vocab_size)
            loss = criterion(last_logits, target_word)
            loss.backward()
            optimizer.step()

            total_loss += loss.item()
            num_batches += 1

        avg_loss = total_loss / num_batches if num_batches else 0.0
        print(f"Epoch {epoch}/{EPOCHS}  Loss: {avg_loss:.4f}")

    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), MODEL_SAVE_PATH)
    print(f"Model saved to {MODEL_SAVE_PATH}")


if __name__ == "__main__":
    main()
