import subprocess
import sys

scripts = [
    "corpus_builder.py",
    "split_builder.py",
    "tokenizer_builder.py",
    "build_dataset.py",
]

for script in scripts:
    print(f"\nRunning {script}...\n")
    result = subprocess.run([sys.executable, script])

    if result.returncode != 0:
        print(f"Error in {script}. Stopping pipeline.")
        sys.exit(1)

print("\nPipeline completed successfully.")