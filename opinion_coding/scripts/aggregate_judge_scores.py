#!/usr/bin/env python3
"""Aggregate opinion-level AI labels to judge (email) level."""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path


DIMS = [
    "efficiency_1_9",
    "corrective_1_9",
    "distributive_1_9",
    "formalist_functionalist_1_9",
]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("jsonl", type=Path, help="Output from label_opinions.py")
    ap.add_argument("-o", "--output", type=Path, required=True)
    args = ap.parse_args()

    by_email: dict[str, dict[str, list]] = defaultdict(lambda: {d: [] for d in DIMS})
    insuff: dict[str, list[bool]] = defaultdict(list)
    n_opinions: dict[str, int] = defaultdict(int)

    with args.jsonl.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            if not rec.get("aggregate"):
                continue
            em = (rec.get("email") or "").strip().lower()
            if not em:
                continue
            n_opinions[em] += 1
            insuff[em].append(bool(rec.get("insufficient_evidence")))
            for d in DIMS:
                v = rec.get(d)
                if isinstance(v, (int, float)) and not isinstance(v, bool):
                    by_email[em][d].append(float(v))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(
            ["email", "n_opinions"]
            + [f"mean_{d}" for d in DIMS]
            + ["frac_insufficient_evidence"],
        )
        for em in sorted(by_email):
            vals = by_email[em]
            n = n_opinions[em]
            means = []
            for d in DIMS:
                xs = vals[d]
                means.append(sum(xs) / len(xs) if xs else "")
            frac_ins = (
                sum(1 for x in insuff[em] if x) / len(insuff[em]) if insuff[em] else ""
            )
            w.writerow([em, n, *means, frac_ins])

    print(f"Wrote {args.output.resolve()} ({len(by_email)} judges)")


if __name__ == "__main__":
    main()
