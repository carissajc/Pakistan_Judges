#!/usr/bin/env python3
"""AI labeling: four justice dimensions -> JSONL (OpenAI or dry-run)."""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
from pathlib import Path

csv.field_size_limit(min(sys.maxsize, 50_000_000))


REPO_ROOT = Path(__file__).resolve().parents[1]
PROMPTS = REPO_ROOT / "prompts"


def load_few_shot_block() -> str:
    data = json.loads((PROMPTS / "few_shot_examples.json").read_text(encoding="utf-8"))
    lines = []
    for ex in data:
        lines.append(f"--- Example: {ex['label']} ---")
        lines.append(f"TEXT: {ex['excerpt']}")
        lines.append(f"SCORES: {json.dumps(ex['scores'])}")
        lines.append(f"RATIONALE: {ex['rationale']}")
    return "\n".join(lines)


def load_system_prompt(path: Path | None = None) -> str:
    p = path or (PROMPTS / "system_prompt.txt")
    raw = p.read_text(encoding="utf-8")
    # Strip optional markdown-style header comments at top of v2 file
    lines = raw.splitlines()
    while lines and (lines[0].startswith("#") or lines[0].strip() == ""):
        lines.pop(0)
    template = "\n".join(lines).lstrip()
    return template.replace("{{FEW_SHOT_BLOCK}}", load_few_shot_block())


def chunk_text(text: str, max_chars: int, overlap: int) -> list[str]:
    if len(text) <= max_chars:
        return [text]
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + max_chars, len(text))
        if end < len(text):
            break_at = text.rfind("\n\n", start, end)
            if break_at == -1 or break_at <= start:
                break_at = end
            end = break_at
        chunks.append(text[start:end].strip())
        start = max(start + 1, end - overlap)
        if end >= len(text):
            break
    return [c for c in chunks if c]


def extract_json_object(raw: str) -> dict:
    raw = raw.strip()
    m = re.search(r"\{[\s\S]*\}\s*$", raw)
    if not m:
        raise ValueError(f"No JSON object in model output: {raw[:500]}")
    return json.loads(m.group(0))


def call_openai(system: str, user: str, model: str) -> dict:
    from openai import OpenAI

    client = OpenAI()
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.2,
    )
    content = resp.choices[0].message.content or ""
    return extract_json_object(content)


def dry_run_scores(text: str) -> dict:
    """Heuristic placeholder when API unavailable (for pipeline testing only)."""
    t = text.lower()
    eff = 5
    cor = 5
    dist = 5
    ff = 5
    if any(
        w in t
        for w in ("proportion", "cost", "waste", "economic", "aggregate", "disproportionate")
    ):
        eff = 7
    if any(
        w in t
        for w in (
            "breach",
            "compensation",
            "restor",
            "wrong",
            "plaintiff",
            "damages",
            "contract",
        )
    ):
        cor = 7
    if any(w in t for w in ("poor", "vulnerable", "equal", "society", "public")):
        dist = 6
    if any(w in t for w in ("section", "ppc", "ingredient", "framed", "statute")):
        ff = 3
    if any(w in t for w in ("policy", "purpose", "equity", "justice of")):
        ff = 7
    if "beyond reasonable doubt" in t and len(t) < 8000:
        return {
            "efficiency_1_9": None,
            "corrective_1_9": None,
            "distributive_1_9": None,
            "formalist_functionalist_1_9": 4,
            "confidence_efficiency": 2,
            "confidence_corrective": 2,
            "confidence_distributive": 2,
            "confidence_formalist_functionalist": 3,
            "quotes_efficiency": [],
            "quotes_corrective": [],
            "quotes_distributive": [],
            "quotes_formalist_functionalist": ["(dry-run: procedural emphasis)"],
            "insufficient_evidence": True,
            "notes": "dry_run heuristic — replace with API output",
        }
    return {
        "efficiency_1_9": eff,
        "corrective_1_9": cor,
        "distributive_1_9": dist,
        "formalist_functionalist_1_9": ff,
        "confidence_efficiency": 2,
        "confidence_corrective": 2,
        "confidence_distributive": 2,
        "confidence_formalist_functionalist": 2,
        "quotes_efficiency": [],
        "quotes_corrective": [],
        "quotes_distributive": [],
        "quotes_formalist_functionalist": [],
        "insufficient_evidence": False,
        "notes": "dry_run heuristic — replace with API output",
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--input",
        type=Path,
        default=REPO_ROOT / "data" / "pilot_sample.csv",
    )
    ap.add_argument(
        "--output",
        type=Path,
        default=REPO_ROOT / "data" / "pilot_ai_output.jsonl",
    )
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--model", default="gpt-4o-mini")
    ap.add_argument("--max-chars", type=int, default=12_000)
    ap.add_argument("--chunk-overlap", type=int, default=400)
    ap.add_argument(
        "--append",
        action="store_true",
        help="Append to output JSONL instead of overwriting",
    )
    ap.add_argument(
        "--prompt",
        type=Path,
        default=None,
        help="System prompt file (default: prompts/system_prompt.txt)",
    )
    args = ap.parse_args()

    system = load_system_prompt(args.prompt)
    args.output.parent.mkdir(parents=True, exist_ok=True)

    use_api = not args.dry_run and os.environ.get("OPENAI_API_KEY")
    if not args.dry_run and not use_api:
        print("No OPENAI_API_KEY; use --dry-run or set the key.")
        raise SystemExit(1)

    dims = [
        "efficiency_1_9",
        "corrective_1_9",
        "distributive_1_9",
        "formalist_functionalist_1_9",
    ]

    out_mode = "a" if args.append else "w"
    with args.input.open(encoding="utf-8", newline="") as f_in, args.output.open(
        out_mode, encoding="utf-8"
    ) as f_out:
        reader = csv.DictReader(f_in)
        for row in reader:
            text = row.get("text_of_judgement") or ""
            chunks = chunk_text(text, args.max_chars, args.chunk_overlap)
            chunk_recs: list[dict] = []
            for ci, chunk in enumerate(chunks):
                user = (
                    "Score the following JUDGMENT TEXT.\n\n"
                    f"row_id: {row.get('row_id','')}\n"
                    f"email: {row.get('email','')}\n"
                    f"filename: {row.get('filename','')}\n"
                    f"chunk_id: {ci}\n\n"
                    "--- BEGIN TEXT ---\n"
                    f"{chunk}\n"
                    "--- END TEXT ---"
                )
                if use_api:
                    try:
                        out = call_openai(system, user, args.model)
                    except Exception as e:
                        out = {
                            "error": str(e),
                            "insufficient_evidence": True,
                            "notes": "API failure",
                        }
                else:
                    out = dry_run_scores(chunk)

                rec = {
                    "row_id": row.get("row_id", ""),
                    "email": row.get("email", ""),
                    "filename": row.get("filename", ""),
                    "chunk_id": ci,
                    "chunk_count": len(chunks),
                    "model": args.model if use_api else "dry-run",
                    **out,
                }
                chunk_recs.append(rec)
                f_out.write(json.dumps(rec, ensure_ascii=False) + "\n")

            agg: dict = {d: None for d in dims}
            for d in dims:
                vals = [
                    x[d]
                    for x in chunk_recs
                    if isinstance(x.get(d), int) and 1 <= x[d] <= 9
                ]
                if vals:
                    vals.sort()
                    mid = len(vals) // 2
                    agg[d] = (
                        vals[mid] if len(vals) % 2 else (vals[mid - 1] + vals[mid]) / 2
                    )
            summary = {
                "row_id": row.get("row_id", ""),
                "email": row.get("email", ""),
                "filename": row.get("filename", ""),
                "chunk_id": -1,
                "chunk_count": len(chunks),
                "aggregate": True,
                "model": args.model if use_api else "dry-run",
                **{k: agg[k] for k in dims},
                "insufficient_evidence": all(
                    x.get("insufficient_evidence") for x in chunk_recs
                ),
                "notes": "aggregate row: median of chunk scores",
            }
            f_out.write(json.dumps(summary, ensure_ascii=False) + "\n")

    print(f"Wrote {args.output.resolve()}")


if __name__ == "__main__":
    main()
