import os
import subprocess
import sys


def main() -> None:
    """
    Convenience script to run the full horror training pipeline.

    Equivalent to manually executing the commands listed in README.md.
    """
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    backend_dir = os.path.join(repo_root, "backend")

    # All paths below are relative to backend/
    cmds = [
        # 1) Excel -> cleaned horror text
        [
            sys.executable,
            "plotcraft/src/prepare_horror_corpus.py",
        ],
        # 2) Cleaned -> large corpus
        [
            sys.executable,
            "plotcraft/src/corpus_builder.py",
            "--input",
            "plotcraft/data/processed/cleaned_fixed_horror.txt",
            "--output",
            "plotcraft/data/processed/large_corpus_horror.txt",
        ],
        # 3) Large corpus -> train/val splits
        [
            sys.executable,
            "plotcraft/src/split_builder.py",
            "--input",
            "plotcraft/data/processed/large_corpus_horror.txt",
            "--out_dir",
            "plotcraft/data/splits_horror",
        ],
        # 4) Train SentencePiece tokenizer
        [
            sys.executable,
            "plotcraft/src/tokenizer_builder.py",
            "--input",
            "plotcraft/data/splits_horror/train.txt",
            "--model_prefix",
            "plotcraft/tokenizer/horror/spm",
            "--vocab_size",
            "16000",
        ],
        # 5) Build HF datasets
        [
            sys.executable,
            "plotcraft/src/build_dataset.py",
            "--tokenizer_model",
            "plotcraft/tokenizer/horror/spm.model",
            "--split_dir",
            "plotcraft/data/splits_horror",
            "--save_path",
            "plotcraft/datasets_horror",
        ],
        # 6) Train model (run_name=horror)
        [
            sys.executable,
            "plotcraft/src/train.py",
            "--run_name",
            "horror",
            "--dataset_dir",
            "plotcraft/datasets_horror",
            "--tokenizer_model",
            "plotcraft/tokenizer/horror/spm.model",
        ],
    ]

    os.chdir(backend_dir)
    for cmd in cmds:
        print(f"\nRunning: {' '.join(cmd)}\n")
        result = subprocess.run(cmd)
        if result.returncode != 0:
            print(f"Command failed with exit code {result.returncode}: {' '.join(cmd)}")
            sys.exit(result.returncode)

    print("\nHorror training pipeline completed successfully.")


if __name__ == "__main__":
    main()

