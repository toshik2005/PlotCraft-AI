"""
PlotCraft story generator for API use.

Lazy-loads trained genre-specific models (action, horror, scifi) and SentencePiece tokenizers.
Provides generate_text() for FastAPI story pipeline to generate multi-genre story continuations.
Implements intelligent caching, fallback mechanisms, and GPU support.

If checkpoint/tokenizer are missing, raises PlotCraftUnavailable so callers can fall back
to alternative generation methods.
"""

import os
import logging
from typing import Dict, Tuple, Optional

# Optional deps: torch and sentencepiece only needed when model is used
try:
    import torch
    import sentencepiece as spm
except ImportError:
    torch = None  # type: ignore
    spm = None  # type: ignore

from .model import build_model

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Paths: both scifi and horror use namespaced dirs (checkpoints/{genre}/best_model, tokenizer/{genre}/)
# ---------------------------------------------------------------------------
_BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_CHECKPOINT_DIR = os.path.join(_BASE, "checkpoints")
_TOKENIZER_DIR = os.path.join(_BASE, "tokenizer")

SUPPORTED_GENRES = ["action", "horror", "scifi"]


class PlotCraftUnavailable(Exception):
    """Raised when the PlotCraft model or tokenizer cannot be loaded."""
    pass


# Cache models per genre to avoid reloading on every request
_cache: Dict[str, Tuple["torch.nn.Module", "spm.SentencePieceProcessor", "torch.device"]] = {}


def _normalize_model_name(model_name: Optional[str]) -> str:
    """
    Normalize model name to supported genre.
    
    Maps common variations to canonical names:
    - "sci-fi", "sci_fi", "sci fi", "science fiction" -> "scifi"
    - Falls back to "scifi" if not recognized
    
    Args:
        model_name: Raw model name from user
    
    Returns:
        Normalized genre name
    """
    if not model_name:
        return "scifi"
    n = model_name.strip().lower()
    if n in {"sci-fi", "sci_fi", "sci fi", "science fiction"}:
        return "scifi"
    if n not in SUPPORTED_GENRES:
        logger.warning(f"Unknown genre '{n}'. Defaulting to 'scifi'.")
        return "scifi"
    return n


def _resolve_paths(model_name: str) -> Tuple[str, str]:
    """
    Resolve checkpoint and tokenizer paths for a genre.
    
    Args:
        model_name: Genre name (action, horror, scifi)
    
    Returns:
        (model_path, tokenizer_path) tuple
    """
    # Both scifi and horror: checkpoints/{genre}/best_model/model.pt, tokenizer/{genre}/spm.model
    model = os.path.join(_CHECKPOINT_DIR, model_name, "best_model", "model.pt")
    tok = os.path.join(_TOKENIZER_DIR, model_name, "spm.model")
    return model, tok


def _ensure_loaded(model_name: Optional[str] = None) -> Tuple["torch.nn.Module", "spm.SentencePieceProcessor", "torch.device"]:
    """
    Lazy-load tokenizer and model for a given genre with caching.
    
    Uses in-memory cache to avoid reloading models on each request.
    Falls back to scifi if genre not found.
    
    Args:
        model_name: Genre name or None (defaults to scifi)
    
    Returns:
        Tuple of (model, tokenizer, device)
    
    Raises:
        PlotCraftUnavailable: If files not found or loading fails
    """
    model_name_n = _normalize_model_name(model_name)
    
    # Return cached model if available
    if model_name_n in _cache:
        logger.debug(f"Using cached model for genre: {model_name_n}")
        return _cache[model_name_n]

    if torch is None or spm is None:
        raise PlotCraftUnavailable("torch or sentencepiece not installed")

    model_path, tok_path = _resolve_paths(model_name_n)

    if not os.path.exists(model_path):
        logger.error(f"Model not found at {model_path}. Expected: {model_path}")
        raise PlotCraftUnavailable(f"Model not found at {model_path}")
    if not os.path.exists(tok_path):
        logger.error(f"Tokenizer not found at {tok_path}. Expected: {tok_path}")
        raise PlotCraftUnavailable(f"Tokenizer not found at {tok_path}")

    try:
        logger.info(f"Loading PlotCraft model for genre: {model_name_n}")
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {device}")
        
        tokenizer = spm.SentencePieceProcessor(model_file=tok_path)
        vocab_size = tokenizer.vocab_size()
        logger.info(f"Tokenizer loaded. Vocab size: {vocab_size}")
        
        model = build_model(vocab_size, 512).to(device)
        state_dict = torch.load(model_path, map_location=device)
        model.load_state_dict(state_dict)
        model.eval()
        logger.info(f"Model loaded and moved to {device}")
    except Exception as e:  # noqa: BLE001
        logger.error(f"Failed to load PlotCraft ({model_name_n}): {e}")
        raise PlotCraftUnavailable(f"Failed to load PlotCraft ({model_name_n}): {e}") from e

    _cache[model_name_n] = (model, tokenizer, device)
    logger.info(f"Model cached for genre: {model_name_n}")
    return _cache[model_name_n]


def is_available() -> bool:
    """Return True if PlotCraft model and tokenizer can be loaded."""
    try:
        _ensure_loaded()
        return True
    except PlotCraftUnavailable:
        return False


def get_cached_genres() -> Dict[str, bool]:
    """
    Get information about which genres are currently cached.
    
    Returns:
        Dict mapping genre names to boolean indicating if cached
    """
    return {genre: genre in _cache for genre in SUPPORTED_GENRES}


def clear_cache(genre: Optional[str] = None) -> None:
    """
    Clear model cache to free memory.
    
    Args:
        genre: Specific genre to clear, or None to clear all
    """
    global _cache
    if genre:
        if genre in _cache:
            del _cache[genre]
            logger.info(f"Cleared cache for genre: {genre}")
    else:
        _cache.clear()
        logger.info("Cleared all model caches")




def generate_text(
    prompt: str,
    max_tokens: int = 800,
    model_name: Optional[str] = None,
    temperature: float = 0.8,
    top_k: int = 40,
    top_p: float = 0.95,
    repetition_penalty: float = 1.2,
    no_repeat_ngram_size: int = 3,
) -> str:
    """
    Generate story continuation from a prompt using the PlotCraft model.
    
    Supports multi-genre generation (action, horror, scifi) with fine-grained
    sampling control. Uses nucleus sampling (top_p) for diversity and repetition
    penalties to avoid repetitive text.

    Args:
        prompt: Input text (story prefix or full prompt).
        max_tokens: Maximum new tokens to generate (default: 800).
        model_name: Genre to use (action, horror, scifi). Defaults to scifi.
        temperature: Sampling temperature. Higher = more creative. (default: 0.8)
        top_k: Keep top-k tokens (default: 40).
        top_p: Nucleus sampling threshold (default: 0.95).
        repetition_penalty: Penalize repetitive tokens (default: 1.2).
        no_repeat_ngram_size: Forbid repeating n-grams of this size (default: 3).

    Returns:
        Generated continuation text (prompt stripped at token-level).

    Raises:
        PlotCraftUnavailable: If model/tokenizer are not present or load fails.
        ValueError: If prompt is empty.
    
    Example:
        >>> text = generate_text("Once upon a time", model_name="horror", max_tokens=200)
        >>> print(text)  # "... continued horror story ..."
    """
    if not prompt or not prompt.strip():
        raise ValueError("Prompt cannot be empty")
    
    model, tokenizer, device = _ensure_loaded(model_name)
    model_name_n = _normalize_model_name(model_name)

    context_size = 512  # model n_positions
    input_ids = tokenizer.encode(prompt, out_type=int)
    
    logger.debug(f"Prompt encoded to {len(input_ids)} tokens")
    
    # Keep within model context window
    if len(input_ids) > context_size:
        logger.warning(f"Prompt too long ({len(input_ids)} tokens). Truncating to {context_size}.")
        input_ids = input_ids[-context_size:]

    # Total length (input + generated) must not exceed context_size
    max_new_tokens = min(max_tokens, context_size - len(input_ids))
    if max_new_tokens <= 0:
        logger.warning("Prompt uses entire context window. No tokens left for generation.")
        return ""

    input_tensor = torch.tensor([input_ids]).to(device)

    pad_id = tokenizer.pad_id()
    if pad_id is None or pad_id < 0:
        pad_id = 0

    logger.info(
        f"Generating text ({model_name_n}): "
        f"prompt_tokens={len(input_ids)}, max_new_tokens={max_new_tokens}, "
        f"temp={temperature}, top_p={top_p}"
    )
    
    with torch.no_grad():
        output = model.generate(
            input_tensor,
            max_new_tokens=max_new_tokens,
            do_sample=True,
            top_k=top_k,
            top_p=top_p,
            temperature=temperature,
            repetition_penalty=repetition_penalty,
            no_repeat_ngram_size=no_repeat_ngram_size,
            pad_token_id=pad_id,
        )

    out_ids = output[0].tolist()
    continuation_ids = out_ids[len(input_ids) :]
    result = tokenizer.decode(continuation_ids).strip()
    
    logger.info(f"Generated {len(result)} characters")
    return result

