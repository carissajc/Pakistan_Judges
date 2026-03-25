#!/usr/bin/env python3
"""
Merge judge-level opinion scores with experiment data (c_score–f_score, eq_focus).

Requires:
- crosswalk CSV: email, prim_key (or id)
- experiment CSV exported from Stata: prim_key, c_score, d_score, e_score, f_score, eq_focus, ...
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--opinions",
        type=Path,
        required=True,
        help="aggregate_judge_scores output CSV",
    )
    ap.add_argument("--crosswalk", type=Path, required=True, help="email, prim_key")
    ap.add_argument("--experiment", type=Path, required=True)
    ap.add_argument("-o", "--output", type=Path, required=True)
    args = ap.parse_args()

    cross: dict[str, str] = {}
    with args.crosswalk.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            em = (row.get("email") or "").strip().lower()
            pk = (row.get("prim_key") or row.get("prim_key ") or "").strip()
            if em and pk:
                cross[em] = pk

    exp_by_pk: dict[str, dict] = {}
    with args.experiment.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            pk = (row.get("prim_key") or "").strip()
            if pk:
                exp_by_pk[pk] = row

    with args.opinions.open(encoding="utf-8", newline="") as f_in, args.output.open(
        "w", newline="", encoding="utf-8"
    ) as f_out:
        r_in = csv.DictReader(f_in)
        fieldnames = list(r_in.fieldnames or [])
        extra = [
            c
            for c in (
                "prim_key",
                "c_score",
                "d_score",
                "e_score",
                "f_score",
                "eq_focus",
            )
            if c not in fieldnames
        ]
        w = csv.DictWriter(f_out, fieldnames=fieldnames + extra)
        w.writeheader()
        for row in r_in:
            em = (row.get("email") or "").strip().lower()
            pk = cross.get(em, "")
            row = dict(row)
            row["prim_key"] = pk
            exp = exp_by_pk.get(pk, {})
            for k in ("c_score", "d_score", "e_score", "f_score", "eq_focus"):
                row[k] = exp.get(k, "")
            w.writerow(row)

    print(f"Wrote {args.output.resolve()}")


if __name__ == "__main__":
    main()
