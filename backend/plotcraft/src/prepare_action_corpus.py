import argparse
import os
import re


def _clean(text: str) -> str:
    """Normalize newlines and whitespace for action scripts."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+\n", "\n", text)          # strip trailing spaces before newline
    text = re.sub(r"\n{3,}", "\n\n", text)          # collapse 3+ blank lines into 2
    text = re.sub(r"[ \t]{2,}", " ", text)          # collapse multiple spaces/tabs
    return text.strip()


def main() -> None:
    # backend/plotcraft/
    plotcraft_base = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    # project root (where imsdb_action_scripts.csv lives)
    repo_root = os.path.abspath(os.path.join(plotcraft_base, "..", ".."))

    parser = argparse.ArgumentParser(description="Convert imsdb_action_scripts.csv into cleaned text corpus.")
    parser.add_argument(
        "--input",
        default=os.path.join(repo_root, "imsdb_action_scripts.csv"),
        help="Path to imsdb_action_scripts.csv (treated as raw text).",
    )
    parser.add_argument(
        "--output",
        default=os.path.join(plotcraft_base, "data", "processed", "cleaned_fixed_action.txt"),
        help="Output cleaned text path.",
    )
    args = parser.parse_args()

    if not os.path.exists(args.input):
        raise FileNotFoundError(f"Input CSV file not found: {args.input}")

    os.makedirs(os.path.dirname(args.output), exist_ok=True)

    with open(args.input, "r", encoding="utf-8") as f:
        raw = f.read()

    cleaned = _clean(raw)

    with open(args.output, "w", encoding="utf-8") as out:
        out.write(cleaned)
        out.write("\n")

    print("Done.")
    print("Input:", args.input)
    print("Output:", args.output)
    print("Characters:", len(cleaned))


if __name__ == "__main__":
    main()

