# Human pilot coding protocol

## Sample

Use the same judgments as in `data/pilot_sample.csv` (row_id identifies each row).

## Procedure

1. Open `data/pilot_human.csv` in Excel or a text editor.
2. For each row (skip the instruction row if present), read the **full** judgment text in `pilot_sample.csv` for matching `row_id`.
3. Assign integers **1–9** for each dimension using [CODEBOOK.md](CODEBOOK.md). Do **not** look at `pilot_ai_output.jsonl` until finished.
4. Enter optional `coder_initials` and `notes` for difficult cases.

## Adjudication

If two coders disagree by **2+ points** on any dimension, review quotes together and revise to consensus; keep a short log of changes.

## After coding

```bash
cd opinion_coding
python scripts/compare_pilot_agreement.py \
  --ai data/pilot_ai_output.jsonl \
  --human data/pilot_human.csv \
  -o data/pilot_agreement_report.txt
```

Use the report to revise the prompt (save as `prompts/system_prompt_v2.txt`) and re-run labeling if needed.
