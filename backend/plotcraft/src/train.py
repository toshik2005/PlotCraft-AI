import argparse
import os
import shutil

import sentencepiece as spm
import torch
from datasets import load_from_disk
from torch.optim import AdamW
from torch.utils.data import DataLoader
from torch.utils.tensorboard import SummaryWriter
from tqdm import tqdm
from transformers import get_linear_schedule_with_warmup

from model import build_model


def parse_args() -> argparse.Namespace:
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    parser = argparse.ArgumentParser(description="Train PlotCraft GPT-2 style model.")
    parser.add_argument("--run_name", default="scifi", help="Used to namespace checkpoints/logs (e.g. horror).")
    parser.add_argument("--block_size", type=int, default=512)
    parser.add_argument("--batch_size", type=int, default=2)
    parser.add_argument("--grad_accum", type=int, default=16)
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--lr", type=float, default=5e-4)
    parser.add_argument("--warmup_steps", type=int, default=2000)
    parser.add_argument(
        "--dataset_dir",
        default=os.path.join(base_path, "datasets"),
        help="Directory containing train_blocks/ and val_blocks/.",
    )
    parser.add_argument(
        "--tokenizer_model",
        default=os.path.join(base_path, "tokenizer", "spm.model"),
        help="SentencePiece .model path.",
    )
    parser.add_argument(
        "--checkpoints_dir",
        default=os.path.join(base_path, "checkpoints"),
        help="Root checkpoints directory.",
    )
    parser.add_argument(
        "--logs_dir",
        default=os.path.join(base_path, "logs"),
        help="Root tensorboard logs directory.",
    )
    return parser.parse_args()


def train(args: argparse.Namespace) -> None:
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    dataset_path = os.path.join(args.dataset_dir, "train_blocks")
    val_path = os.path.join(args.dataset_dir, "val_blocks")

    # Namespace outputs per run_name (avoid overwriting sci-fi when training horror)
    checkpoints_dir = os.path.join(args.checkpoints_dir, args.run_name)
    best_path = os.path.join(checkpoints_dir, "best_model")
    log_path = os.path.join(args.logs_dir, args.run_name)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("Using device:", device)

    os.makedirs(checkpoints_dir, exist_ok=True)
    os.makedirs(best_path, exist_ok=True)
    os.makedirs(log_path, exist_ok=True)

    writer = SummaryWriter(log_path)

    # =========================================
    # DATA
    # =========================================
    train_dataset = load_from_disk(dataset_path)
    val_dataset = load_from_disk(val_path)

    train_dataset.set_format(type="torch")
    val_dataset.set_format(type="torch")

    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=args.batch_size)

    # =========================================
    # MODEL
    # =========================================
    if not os.path.exists(args.tokenizer_model):
        raise FileNotFoundError(f"Tokenizer model not found: {args.tokenizer_model}")

    sp = spm.SentencePieceProcessor(model_file=args.tokenizer_model)
    vocab_size = sp.vocab_size()

    model = build_model(vocab_size, args.block_size).to(device)

    optimizer = AdamW(model.parameters(), lr=args.lr)

    total_steps = (len(train_loader) * args.epochs) // max(1, args.grad_accum)

    scheduler = get_linear_schedule_with_warmup(
        optimizer,
        num_warmup_steps=args.warmup_steps,
        num_training_steps=total_steps,
    )

    use_amp = device.type == "cuda"
    scaler = torch.amp.GradScaler("cuda") if use_amp else None

    best_loss = float("inf")

    # =========================================
    # SAVE FUNCTION
    # =========================================
    def save_checkpoint(epoch: int, val_loss: float) -> None:
        nonlocal best_loss

        epoch_dir = os.path.join(checkpoints_dir, f"epoch_{epoch}")
        os.makedirs(epoch_dir, exist_ok=True)

        torch.save(model.state_dict(), os.path.join(epoch_dir, "model.pt"))
        torch.save(optimizer.state_dict(), os.path.join(epoch_dir, "optimizer.pt"))
        torch.save(scheduler.state_dict(), os.path.join(epoch_dir, "scheduler.pt"))

        print(f"Checkpoint saved: {os.path.basename(epoch_dir)}")

        # Save best model
        if val_loss < best_loss:
            best_loss = val_loss
            torch.save(model.state_dict(), os.path.join(best_path, "model.pt"))
            print("Best model updated.")

        # Keep only last 3 epoch checkpoints (excluding best_model)
        epoch_dirs = sorted(
            [d for d in os.listdir(checkpoints_dir) if d.startswith("epoch_")],
            key=lambda x: int(x.split("_")[1]),
        )

        while len(epoch_dirs) > 3:
            oldest = epoch_dirs.pop(0)
            shutil.rmtree(os.path.join(checkpoints_dir, oldest))
            print("Removed old checkpoint:", oldest)

    # =========================================
    # TRAIN LOOP
    # =========================================
    for epoch in range(1, args.epochs + 1):
        model.train()
        total_train_loss = 0.0

        progress = tqdm(train_loader, desc=f"Epoch {epoch}/{args.epochs}")
        optimizer.zero_grad()

        for step, batch in enumerate(progress):
            inputs = batch["input_ids"].to(device)

            if use_amp:
                with torch.autocast("cuda"):
                    outputs = model(input_ids=inputs, labels=inputs)
                    loss = outputs.loss / args.grad_accum
                assert scaler is not None
                scaler.scale(loss).backward()
            else:
                outputs = model(input_ids=inputs, labels=inputs)
                loss = outputs.loss / args.grad_accum
                loss.backward()

            if (step + 1) % args.grad_accum == 0:
                if use_amp:
                    assert scaler is not None
                    scaler.step(optimizer)
                    scaler.update()
                else:
                    optimizer.step()
                scheduler.step()
                optimizer.zero_grad()

            total_train_loss += loss.item() * args.grad_accum
            progress.set_postfix(loss=loss.item() * args.grad_accum)

        avg_train_loss = total_train_loss / max(1, len(train_loader))

        # ================= VALIDATION =================
        model.eval()
        total_val_loss = 0.0
        with torch.no_grad():
            for batch in val_loader:
                inputs = batch["input_ids"].to(device)
                outputs = model(input_ids=inputs, labels=inputs)
                total_val_loss += outputs.loss.item()

        avg_val_loss = total_val_loss / max(1, len(val_loader))
        print(f"\nEpoch {epoch} - Train Loss: {avg_train_loss:.4f}, Val Loss: {avg_val_loss:.4f}")

        writer.add_scalar("Loss/train", avg_train_loss, epoch)
        writer.add_scalar("Loss/val", avg_val_loss, epoch)

        save_checkpoint(epoch, avg_val_loss)

    print("\nTraining complete.")


def main() -> None:
    args = parse_args()
    train(args)


if __name__ == "__main__":
    main()