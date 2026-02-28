import argparse
import os


def main() -> None:
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    parser = argparse.ArgumentParser(description="Create train/val text splits for PlotCraft.")
    parser.add_argument(
        "--input",
        default=os.path.join(base_path, "data", "processed", "large_corpus.txt"),
        help="Input corpus file.",
    )
    parser.add_argument(
        "--out_dir",
        default=os.path.join(base_path, "data", "splits"),
        help="Output directory for train.txt and val.txt.",
    )
    parser.add_argument("--train_ratio", type=float, default=0.95)
    args = parser.parse_args()

    if not os.path.exists(args.input):
        raise FileNotFoundError(f"Corpus not found at: {args.input}")

    os.makedirs(args.out_dir, exist_ok=True)

    with open(args.input, "r", encoding="utf-8") as f:
        text = f.read()

    split_index = int(len(text) * args.train_ratio)

    with open(os.path.join(args.out_dir, "train.txt"), "w", encoding="utf-8") as f:
        f.write(text[:split_index])

    with open(os.path.join(args.out_dir, "val.txt"), "w", encoding="utf-8") as f:
        f.write(text[split_index:])

    print("Train/Val split created.")
    print("Train:", os.path.join(args.out_dir, "train.txt"))
    print("Val:", os.path.join(args.out_dir, "val.txt"))


if __name__ == "__main__":
    main()