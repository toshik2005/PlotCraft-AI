## PlotCraft Horror Training

This folder describes how to train a **horror-specific PlotCraft model** from `creepypastas.xlsx` without touching the existing sci‑fi model.

All commands below are run **from the repo root**:

```bash
cd backend
```

Adjust for PowerShell as needed (same commands).

---

### 0. Install training dependencies (one time)

```bash
pip install -r plotcraft/requirements-train.txt
```

---

### 1. Convert `creepypastas.xlsx` → cleaned horror text

This reads the Excel file at the repo root and writes cleaned horror stories into PlotCraft’s data folder.

```bash
python plotcraft/src/prepare_horror_corpus.py
```

Output:

- `plotcraft/data/processed/cleaned_fixed_horror.txt`

If it picked the wrong column, re-run with an explicit column name:

```bash
python plotcraft/src/prepare_horror_corpus.py --text_column "Story"
```

Replace `"Story"` with the actual column header that holds the creepypasta text.

---

### 2. Build capped horror corpus

Turn the cleaned text into a large corpus file (optionally capped by character count).

```bash
python plotcraft/src/corpus_builder.py ^
  --input plotcraft/data/processed/cleaned_fixed_horror.txt ^
  --output plotcraft/data/processed/large_corpus_horror.txt
```

Output:

- `plotcraft/data/processed/large_corpus_horror.txt`

---

### 3. Create train/val splits for horror

```bash
python plotcraft/src/split_builder.py ^
  --input plotcraft/data/processed/large_corpus_horror.txt ^
  --out_dir plotcraft/data/splits_horror
```

Outputs:

- `plotcraft/data/splits_horror/train.txt`
- `plotcraft/data/splits_horror/val.txt`

---

### 4. Train a SentencePiece tokenizer for horror

```bash
python plotcraft/src/tokenizer_builder.py ^
  --input plotcraft/data/splits_horror/train.txt ^
  --model_prefix plotcraft/tokenizer/horror/spm ^
  --vocab_size 16000
```

Outputs:

- `plotcraft/tokenizer/horror/spm.model`
- `plotcraft/tokenizer/horror/spm.vocab`

---

### 5. Build HF datasets (512‑token blocks) for horror

```bash
python plotcraft/src/build_dataset.py ^
  --tokenizer_model plotcraft/tokenizer/horror/spm.model ^
  --split_dir plotcraft/data/splits_horror ^
  --save_path plotcraft/datasets_horror
```

Outputs:

- `plotcraft/datasets_horror/train_blocks`
- `plotcraft/datasets_horror/val_blocks`

---

### 6. Train the horror model

This trains a GPT‑2 style model and stores checkpoints under a **separate** horror namespace.

```bash
python plotcraft/src/train.py ^
  --run_name horror ^
  --dataset_dir plotcraft/datasets_horror ^
  --tokenizer_model plotcraft/tokenizer/horror/spm.model
```

Main outputs:

- `plotcraft/checkpoints/horror/best_model/model.pt`
- TensorBoard logs in `plotcraft/logs/horror`

---

### 7. How the backend uses the horror model

The FastAPI backend already checks the `genre` field:

- If `genre` contains the word `"horror"`, it calls:

  - tokenizer: `plotcraft/tokenizer/horror/spm.model`
  - model: `plotcraft/checkpoints/horror/best_model/model.pt`

- Otherwise it falls back to the sci‑fi (default) model.

