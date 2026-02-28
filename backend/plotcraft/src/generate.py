import os
import torch
import sentencepiece as spm
from model import build_model

# =========================================
# PATHS
# =========================================
BASE_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

CHECKPOINT_PATH = os.path.join(BASE_PATH, "checkpoints")
BEST_MODEL_PATH = os.path.join(CHECKPOINT_PATH, "scifi", "best_model", "model.pt")
TOKENIZER_PATH = os.path.join(BASE_PATH, "tokenizer", "scifi", "spm.model")

# =========================================
# SAFETY CHECKS
# =========================================
if not os.path.exists(BEST_MODEL_PATH):
    raise FileNotFoundError(
        "Model not found.\n"
        "Place sci-fi model at:\n"
        "backend/plotcraft/checkpoints/scifi/best_model/model.pt"
    )

if not os.path.exists(TOKENIZER_PATH):
    raise FileNotFoundError(
        "Tokenizer not found.\n"
        "Place spm.model at:\n"
        "backend/plotcraft/tokenizer/scifi/spm.model"
    )

# =========================================
# DEVICE
# =========================================
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Using device:", device)

# =========================================
# LOAD TOKENIZER
# =========================================
sp = spm.SentencePieceProcessor(model_file=TOKENIZER_PATH)
vocab_size = sp.vocab_size()

# =========================================
# LOAD MODEL
# =========================================
model = build_model(vocab_size, 512).to(device)

model.load_state_dict(
    torch.load(BEST_MODEL_PATH, map_location=device)
)

model.eval()
print("Model loaded successfully.\n")

# =========================================
# GENERATION FUNCTION
# =========================================
def generate_text(prompt, max_tokens=800):

    input_ids = sp.encode(prompt, out_type=int)
    input_tensor = torch.tensor([input_ids]).to(device)

    with torch.no_grad():
        output = model.generate(
            input_tensor,
            max_new_tokens=max_tokens,
            do_sample=True,
            top_k=40,
            top_p=0.95,
            temperature=0.8,
            repetition_penalty=1.2,
            no_repeat_ngram_size=3,
            pad_token_id=sp.pad_id()
        )

    return sp.decode(output[0].tolist())

# =========================================
# INTERACTIVE LOOP
# =========================================
if __name__ == "__main__":
    while True:
        prompt = input("Enter prompt: ").strip()
        if not prompt:
            continue

        print("\nGenerated:\n")
        print(generate_text(prompt))
        print("\n" + "=" * 70 + "\n")