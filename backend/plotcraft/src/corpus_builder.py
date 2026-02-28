import argparse
import os


def main() -> None:
    # backend/plotcraft
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    parser = argparse.ArgumentParser(description="Build a capped large corpus for PlotCraft.")
    parser.add_argument(
        "--input",
        default=os.path.join(base_path, "data", "processed", "cleaned_fixed.txt"),
        help="Input cleaned text file.",
    )
    parser.add_argument(
        "--output",
        default=os.path.join(base_path, "data", "processed", "large_corpus.txt"),
        help="Output large corpus file.",
    )
    parser.add_argument(
        "--max_chars",
        type=int,
        default=100_000_000,
        help="Maximum characters to keep (~100MB default).",
    )
    args = parser.parse_args()

    if not os.path.exists(args.input):
        raise FileNotFoundError(f"Input file not found at: {args.input}")

    os.makedirs(os.path.dirname(args.output), exist_ok=True)

    print("Reading from:", args.input)
    with open(args.input, "r", encoding="utf-8") as f:
        text = f.read()

    large_text = text[: args.max_chars]

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(large_text)

    print("Corpus created.")
    print("Characters:", len(large_text))
    print("Saved to:", args.output)


if __name__ == "__main__":
    main()