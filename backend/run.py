"""
Main entry point for the PlotCraft-AI backend.

Blueprints:
  - API server (default): FastAPI app from app.main
  - ML pipeline: preprocessing and training (optional subcommands)

Usage:
  python run.py                    # Start API server (default)
  python run.py serve               # Same as above
  python run.py ml clean            # Clean raw scifi text
  python run.py ml vocab            # Build vocabulary
  python run.py ml train            # Train LSTM model
  python run.py ml all              # clean + vocab + train
"""

import argparse
import sys
from pathlib import Path

# Ensure backend root is on path when run as script
_BACKEND_ROOT = Path(__file__).resolve().parent
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))


def _run_server() -> None:
    """Start the FastAPI server (app.main:app)."""
    import uvicorn
    from app.core.config import settings

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )


def _run_ml_clean() -> None:
    """Run ML preprocessing: clean raw scifi.txt -> cleaned_scifi.txt."""
    from ml.preprocessing.clean_data import main as clean_main
    clean_main()


def _run_ml_vocab() -> None:
    """Run ML preprocessing: build vocab from cleaned text -> vocab.pkl."""
    from ml.preprocessing.tokenizer_builder import main as vocab_main
    vocab_main()


def _run_ml_train() -> None:
    """Run ML training: train LSTM -> scifi_model.pt."""
    from ml.training.train import main as train_main
    train_main()


def _run_ml_all() -> None:
    """Run full ML pipeline: clean -> vocab -> train."""
    _run_ml_clean()
    _run_ml_vocab()
    _run_ml_train()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="PlotCraft-AI backend: API server and ML pipeline.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # serve (default)
    parser_serve = subparsers.add_parser("serve", help="Start FastAPI server (default)")
    parser_serve.set_defaults(func=_run_server)

    # ml *
    parser_ml = subparsers.add_parser("ml", help="ML pipeline (preprocessing + training)")
    ml_sub = parser_ml.add_subparsers(dest="ml_command", required=True)
    ml_sub.add_parser("clean", help="Clean raw scifi.txt -> cleaned_scifi.txt").set_defaults(
        func=_run_ml_clean
    )
    ml_sub.add_parser("vocab", help="Build vocab -> vocab.pkl").set_defaults(func=_run_ml_vocab)
    ml_sub.add_parser("train", help="Train LSTM -> scifi_model.pt").set_defaults(func=_run_ml_train)
    ml_sub.add_parser("all", help="Run clean + vocab + train").set_defaults(func=_run_ml_all)

    args = parser.parse_args()

    # Default: serve
    if args.command is None:
        _run_server()
        return 0

    if args.command == "ml":
        args.func()
    else:
        args.func()

    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
