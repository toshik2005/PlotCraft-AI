import argparse
import os

import numpy as np
import sentencepiece as spm
from datasets import Dataset


def main() -> None:
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    parser = argparse.ArgumentParser(description="Build HF datasets of 512-token blocks for PlotCraft.")
    parser.add_argument(
        "--tokenizer_model",
        default=os.path.join(base_path, "tokenizer", "spm.model"),
        help="SentencePiece .model path.",
    )
    parser.add_argument(
        "--split_dir",
        default=os.path.join(base_path, "data", "splits"),
        help="Directory containing train.txt and val.txt.",
    )
    parser.add_argument(
        "--save_path",
        default=os.path.join(base_path, "datasets"),
        help="Output datasets directory (creates train_blocks/val_blocks).",
    )
    parser.add_argument("--block_size", type=int, default=512)
    args = parser.parse_args()

    if not os.path.exists(args.tokenizer_model):
        raise FileNotFoundError(f"Tokenizer model not found: {args.tokenizer_model}")

    os.makedirs(args.save_path, exist_ok=True)

    sp = spm.SentencePieceProcessor(model_file=args.tokenizer_model)

    def build_split(split_name: str) -> None:
        print(f"Building {split_name} dataset...")

        split_file = os.path.join(args.split_dir, f"{split_name}.txt")
        if not os.path.exists(split_file):
            raise FileNotFoundError(f"Missing split file: {split_file}")

        with open(split_file, "r", encoding="utf-8") as f:
            text = f.read()

        ids = sp.encode(text, out_type=int)
        num_blocks = len(ids) // args.block_size
        ids = ids[: num_blocks * args.block_size]

        blocks = np.array(ids).reshape(num_blocks, args.block_size).tolist()
        dataset = Dataset.from_dict({"input_ids": blocks})
        dataset.save_to_disk(os.path.join(args.save_path, f"{split_name}_blocks"))

        print(f"{split_name}: {num_blocks} blocks saved.")

    build_split("train")
    build_split("val")


if __name__ == "__main__":
    main()