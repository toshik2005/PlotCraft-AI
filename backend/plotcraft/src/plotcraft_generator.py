"""
PlotCraft story generator for API use.

Lazy-loads the trained model and SentencePiece tokenizer; exposes generate_text()
so the FastAPI story pipeline can use it instead of (or in addition to) the
transformers-based generator. If the checkpoint/tokenizer are missing, the
module raises PlotCraftUnavailable so callers can fall back.
"""

import os
from typing import Dict, Tuple, Optional

# Optional deps: torch and sentencepiece only needed when model is used
try:
    import torch
    import sentencepiece as spm
except ImportError:
    torch = None  # type: ignore
    spm = None  # type: ignore

from .model import build_model

# ---------------------------------------------------------------------------
# Paths: both scifi and horror use namespaced dirs (checkpoints/{genre}/best_model, tokenizer/{genre}/)
# ---------------------------------------------------------------------------
_BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_CHECKPOINT_DIR = os.path.join(_BASE, "checkpoints")


class PlotCraftUnavailable(Exception):
    """Raised when the PlotCraft model or tokenizer cannot be loaded."""
    pass


_cache: Dict[str, Tuple["torch.nn.Module", "spm.SentencePieceProcessor", "torch.device"]] = {}


def _normalize_model_name(model_name: Optional[str]) -> str:
    if not model_name:
        return "scifi"
    n = model_name.strip().lower()
    if n in {"sci-fi", "sci_fi", "sci fi", "science fiction"}:
        return "scifi"
    return n


def _resolve_paths(model_name: str) -> Tuple[str, str]:
    # Both scifi and horror: checkpoints/{genre}/best_model/model.pt, tokenizer/{genre}/spm.model
    model = os.path.join(_CHECKPOINT_DIR, model_name, "best_model", "model.pt")
    tok = os.path.join(_BASE, "tokenizer", model_name, "spm.model")
    return model, tok


def _ensure_loaded(model_name: Optional[str] = None) -> Tuple["torch.nn.Module", "spm.SentencePieceProcessor", "torch.device"]:
    """Lazy-load tokenizer and model for a given model_name."""
    model_name_n = _normalize_model_name(model_name)
    if model_name_n in _cache:
        return _cache[model_name_n]

    if torch is None or spm is None:
        raise PlotCraftUnavailable("torch or sentencepiece not installed")

    model_path, tok_path = _resolve_paths(model_name_n)

    if not os.path.exists(model_path):
        raise PlotCraftUnavailable(f"Model not found at {model_path}")
    if not os.path.exists(tok_path):
        raise PlotCraftUnavailable(f"Tokenizer not found at {tok_path}")

    try:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        tokenizer = spm.SentencePieceProcessor(model_file=tok_path)
        vocab_size = tokenizer.vocab_size()
        model = build_model(vocab_size, 512).to(device)
        model.load_state_dict(torch.load(model_path, map_location=device))
        model.eval()
    except Exception as e:  # noqa: BLE001
        raise PlotCraftUnavailable(f"Failed to load PlotCraft ({model_name_n}): {e}") from e

    _cache[model_name_n] = (model, tokenizer, device)
    return _cache[model_name_n]


def is_available() -> bool:
    """Return True if PlotCraft model and tokenizer can be loaded."""
    try:
        _ensure_loaded()
        return True
    except PlotCraftUnavailable:
        return False


def generate_text(prompt: str, max_tokens: int = 800, model_name: Optional[str] = None) -> str:
    """
    Generate story continuation from a prompt using the PlotCraft model.

    Args:
        prompt: Input text (e.g. story prefix or full prompt).
        max_tokens: Maximum new tokens to generate.
        model_name: Which PlotCraft checkpoint/tokenizer to use (e.g. "scifi", "horror").

    Returns:
        Generated continuation text (prompt stripped at token-level).

    Raises:
        PlotCraftUnavailable: If model/tokenizer are not present or load fails.
    """
    model, tokenizer, device = _ensure_loaded(model_name)

    context_size = 512  # model n_positions
    input_ids = tokenizer.encode(prompt, out_type=int)
    # Keep within model context window
    if len(input_ids) > context_size:
        input_ids = input_ids[-context_size:]

    # Total length (input + generated) must not exceed context_size to avoid "index out of range"
    max_new_tokens = min(max_tokens, context_size - len(input_ids))
    if max_new_tokens <= 0:
        return ""

    input_tensor = torch.tensor([input_ids]).to(device)

    pad_id = tokenizer.pad_id()
    if pad_id is None or pad_id < 0:
        pad_id = 0

    with torch.no_grad():
        output = model.generate(
            input_tensor,
            max_new_tokens=max_new_tokens,
            do_sample=True,
            top_k=40,
            top_p=0.95,
            temperature=0.8,
            repetition_penalty=1.2,
            no_repeat_ngram_size=3,
            pad_token_id=pad_id,
        )

    out_ids = output[0].tolist()
    continuation_ids = out_ids[len(input_ids) :]
    return tokenizer.decode(continuation_ids).strip()
