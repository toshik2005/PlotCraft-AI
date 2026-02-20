# Sci‑Fi LSTM Language Model

Production-ready word-level LSTM trained on `ml/data/raw/scifi.txt`.

## Run order

From **backend/ml/** (recommended):

```bash
cd backend/ml

# 1. Clean raw text → ml/data/processed/cleaned_scifi.txt
python preprocessing/clean_data.py

# 2. Build vocabulary → ml/artifacts/vocab.pkl (prints vocab size)
python preprocessing/tokenizer_builder.py

# 3. Train model → ml/artifacts/scifi_model.pt (15 epochs, loss printed each epoch)
python training/train.py
```

From **backend/** (alternative):

```bash
cd backend
python -m ml.preprocessing.clean_data
python -m ml.preprocessing.tokenizer_builder
python -m ml.training.train
```

## Generate text

```python
from ml.inference.generate import generate_story

# Next 100 words after prompt; optional <GENRE_SCIFI> prefix
text = generate_story("the ship entered hyperspace", num_words=100, temperature=0.8)
print(text)
```

## Requirements

- PyTorch (GPU used if available)
- Raw data: `backend/ml/data/raw/scifi.txt`

No pretrained models; vocabulary and model are built and trained from scratch.
