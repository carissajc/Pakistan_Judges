#!/usr/bin/env python3
"""
Stream opinions from all_cases_w_texts.csv in batches through label_opinions.py.

  export OPENAI_API_KEY=...
  python scripts/run_full_corpus.py --input /path/to/all_cases_w_texts.csv \\
    --output data/full_labels.jsonl --batch-size 10 --limit 30

Use --dry-run for no API. First batch overwrites output; later batches use --append.
"""

from __future__ import annotations

import argparse
import csv
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, required=True)
    ap.add_argument("--output", type=Path, default=REPO / "data" / "full_labels.jsonl")
    ap.add_argument("--batch-size", type=int, default=15)
    ap.add_argument("--limit", type=int, default=0, help="0 = entire file")
    ap.add_argument("--model", default="gpt-4o-mini")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--max-chars", type=int, default=12_000)
    args = ap.parse_args()

    csv.field_size_limit(min(sys.maxsize, 50_000_000))

    tmp_csv = REPO / "data" / "_batch_input.csv"
    tmp_csv.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["row_id", "email", "filename", "text_of_judgement"]

    batch: list[dict] = []
    total = 0
    batch_idx = 0

    def run_batch(append: bool) -> None:
        nonlocal batch_idx
        if not batch:
            return
        with tmp_csv.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            w.writerows(batch)
        cmd = [
            sys.executable,
            str(REPO / "scripts" / "label_opinions.py"),
            "--input",
            str(tmp_csv),
            "--output",
            str(args.output),
            "--max-chars",
            str(args.max_chars),
        ]
        if append:
            cmd.append("--append")
        if args.dry_run:
            cmd.append("--dry-run")
        else:
            cmd.extend(["--model", args.model])
        subprocess.run(cmd, check=True, cwd=str(REPO))
        batch_idx += 1
        batch.clear()

    if args.output.exists():
        args.output.unlink()

    with args.input.open(newline="", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        cols = reader.fieldnames or []
        id_key = cols[0] if cols else None
        for row in reader:
            if args.limit and total >= args.limit:
                break
            text = (row.get("text_of_judgement") or "").strip()
            if not text:
                continue
            rid = str(row.get(id_key, "") if id_key else "").strip()
            if not rid:
                rid = f"auto_{total+1}"
            batch.append(
                {
                    "row_id": rid,
                    "email": (row.get("email") or "").strip(),
                    "filename": (row.get("filename") or "").strip(),
                    "text_of_judgement": text,
                }
            )
            total += 1
            if len(batch) >= args.batch_size:
                run_batch(append=batch_idx > 0)

    run_batch(append=batch_idx > 0)
    print(f"Labeled {total} opinions -> {args.output.resolve()}")


if __name__ == "__main__":
    main()
