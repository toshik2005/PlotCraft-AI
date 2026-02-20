"""
LSTM Language Model for next-word prediction.

Architecture:
  - Embedding(vocab_size, 256)
  - LSTM(256, 512, num_layers=2, dropout=0.3)
  - Linear(512, vocab_size) for logits
"""

import torch
from torch import nn


class LSTMLanguageModel(nn.Module):
    """
    Word-level LSTM language model.

    - Embedding dim: 256
    - LSTM hidden: 512, 2 layers, dropout 0.3
    - Output: linear to vocab_size (next-word logits)
    """

    def __init__(
        self,
        vocab_size: int,
        embedding_dim: int = 256,
        hidden_size: int = 512,
        num_layers: int = 2,
        dropout: float = 0.3,
    ) -> None:
        super().__init__()
        self.vocab_size = vocab_size
        self.embedding_dim = embedding_dim
        self.hidden_size = hidden_size
        self.num_layers = num_layers

        self.embedding = nn.Embedding(vocab_size, embedding_dim, padding_idx=0)
        self.lstm = nn.LSTM(
            input_size=embedding_dim,
            hidden_size=hidden_size,
            num_layers=num_layers,
            dropout=dropout if num_layers > 1 else 0.0,
            batch_first=True,
        )
        self.dropout = nn.Dropout(dropout)
        self.fc = nn.Linear(hidden_size, vocab_size)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        x: (batch, seq_len) token indices
        Returns: (batch, seq_len, vocab_size) logits for next word at each position
        """
        # (batch, seq_len) -> (batch, seq_len, embedding_dim)
        emb = self.embedding(x)
        emb = self.dropout(emb)

        # LSTM: (batch, seq_len, hidden_size)
        lstm_out, _ = self.lstm(emb)

        # (batch, seq_len, vocab_size)
        logits = self.fc(self.dropout(lstm_out))
        return logits
