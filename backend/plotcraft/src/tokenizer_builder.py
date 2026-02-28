import argparse
import os

import sentencepiece as spm


def main() -> None:
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    parser = argparse.ArgumentParser(description="Train SentencePiece tokenizer for PlotCraft.")
    parser.add_argument(
        "--input",
        default=os.path.join(base_path, "data", "splits", "train.txt"),
        help="Training text file path.",
    )
    parser.add_argument(
        "--model_prefix",
        default=os.path.join(base_path, "tokenizer", "spm"),
        help="Output prefix (creates .model and .vocab).",
    )
    parser.add_argument("--vocab_size", type=int, default=16000)
    parser.add_argument("--model_type", default="unigram", choices=["unigram", "bpe", "char", "word"])
    parser.add_argument("--character_coverage", type=float, default=0.9995)
    parser.add_argument("--input_sentence_size", type=int, default=2_000_000)
    parser.add_argument("--shuffle_input_sentence", action="store_true", default=True)
    args = parser.parse_args()

    if not os.path.exists(args.input):
        raise FileNotFoundError(f"Tokenizer training input not found: {args.input}")

    out_dir = os.path.dirname(args.model_prefix)
    os.makedirs(out_dir, exist_ok=True)

    spm.SentencePieceTrainer.train(
        input=args.input,
        model_prefix=args.model_prefix,
        vocab_size=args.vocab_size,
        model_type=args.model_type,
        character_coverage=args.character_coverage,
        input_sentence_size=args.input_sentence_size,
        shuffle_input_sentence=args.shuffle_input_sentence,
        pad_id=0,
        unk_id=1,
        bos_id=2,
        eos_id=3,
    )

    print("Tokenizer trained.")
    print("Model:", args.model_prefix + ".model")
    print("Vocab:", args.model_prefix + ".vocab")


if __name__ == "__main__":
    main()