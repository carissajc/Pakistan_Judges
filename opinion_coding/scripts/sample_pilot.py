#!/usr/bin/env python3
"""Draw a reproducible pilot sample from all_cases_w_texts.csv."""

from __future__ import annotations

import argparse
import csv
import random
import sys
from pathlib import Path

csv.field_size_limit(min(sys.maxsize, 10_000_000))


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--input",
        type=Path,
        default=Path(
            "/Users/carissa.chen/Downloads/all_judgements/all_cases_w_texts.csv"
        ),
    )
    p.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "data" / "pilot_sample.csv",
    )
    p.add_argument("--n", type=int, default=8)
    p.add_argument("--max-chars", type=int, default=15_000)
    p.add_argument("--seed", type=int, default=42)
    args = p.parse_args()

    random.seed(args.seed)

    eligible: list[dict] = []
    with args.input.open(newline="", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        # First column may be unnamed in source
        fieldnames = reader.fieldnames or []
        id_key = fieldnames[0] if fieldnames else None
        for row in reader:
            rid = row.get(id_key, "") if id_key else ""
            text = (row.get("text_of_judgement") or "").strip()
            if not text or len(text) > args.max_chars:
                continue
            eligible.append(
                {
                    "row_id": str(rid).strip(),
                    "email": (row.get("email") or "").strip(),
                    "filename": (row.get("filename") or "").strip(),
                    "text_of_judgement": text,
                }
            )

    if len(eligible) < args.n:
        raise SystemExit(
            f"Only {len(eligible)} rows under max_chars={args.max_chars}; "
            "raise --max-chars or check input path."
        )

    sample = random.sample(eligible, args.n) if len(eligible) > args.n else eligible
    for i, row in enumerate(sample, start=1):
        if not str(row.get("row_id", "")).strip():
            row["row_id"] = f"pilot_{i}"

    args.output.parent.mkdir(parents=True, exist_ok=True)

    with args.output.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=["row_id", "email", "filename", "text_of_judgement"],
        )
        w.writeheader()
        w.writerows(sample)

    print(f"Wrote {len(sample)} rows to {args.output.resolve()}")


if __name__ == "__main__":
    main()
