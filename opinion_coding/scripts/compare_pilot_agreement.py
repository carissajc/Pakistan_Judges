#!/usr/bin/env python3
"""Compare pilot AI aggregate scores to human-coded pilot_human.csv."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

DIMS = [
    "efficiency_1_9",
    "corrective_1_9",
    "distributive_1_9",
    "formalist_functionalist_1_9",
]


def load_ai_aggregates(path: Path) -> dict[str, dict]:
    out: dict[str, dict] = {}
    with path.open(encoding="utf-8") as f:
        for line in f:
            rec = json.loads(line)
            if not rec.get("aggregate"):
                continue
            rid = str(rec.get("row_id", ""))
            out[rid] = rec
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ai", type=Path, required=True, help="pilot_ai_output.jsonl")
    ap.add_argument("--human", type=Path, required=True, help="pilot_human.csv")
    ap.add_argument("-o", "--output", type=Path, default=None)
    args = ap.parse_args()

    ai = load_ai_aggregates(args.ai)

    import csv

    pairs: dict[str, list[tuple[float, float]]] = {d: [] for d in DIMS}
    with args.human.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rid = str(row.get("row_id", "")).strip()
            if not rid or rid.startswith("#"):
                continue
            if rid not in ai:
                continue
            a = ai[rid]
            for d in DIMS:
                h = row.get(d)
                if h is None or str(h).strip() == "":
                    continue
                try:
                    hv = float(h)
                except ValueError:
                    continue
                av = a.get(d)
                if av is None or (isinstance(av, float) and np.isnan(av)):
                    continue
                pairs[d].append((float(av), hv))

    lines = ["# Pilot agreement: AI aggregate vs human", ""]
    for d in DIMS:
        ps = pairs[d]
        if not ps:
            lines.append(f"## {d}: no paired rows")
            lines.append("")
            continue
        av, hv = zip(*ps)
        err = [abs(a - b) for a, b in ps]
        lines.append(f"## {d}")
        lines.append(f"- n = {len(ps)}")
        lines.append(f"- mean absolute error = {sum(err)/len(err):.3f}")
        lines.append(f"- Pearson r = {np.corrcoef(av, hv)[0,1]:.3f}")
        lines.append("")

    report = "\n".join(lines)
    print(report)
    if args.output:
        args.output.write_text(report, encoding="utf-8")
        print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
