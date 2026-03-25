# Opinion coding: four justice dimensions (AI + human review)

Implements the plan aligned with [Vignette Coding Survey.docx](../Vignette%20Coding%20Survey.docx) scales (1–9) and Stata `c_score`–`f_score` (see [VIGNETTE_CDEF_MAPPING.md](VIGNETTE_CDEF_MAPPING.md)).

## Files

| Path | Purpose |
|------|---------|
| [CODEBOOK.md](CODEBOOK.md) | Definitions for human and AI coders |
| [prompts/system_prompt.txt](prompts/system_prompt.txt) | LLM system prompt with few-shot slot |
| [prompts/few_shot_examples.json](prompts/few_shot_examples.json) | Few-shot illustrations |
| `data/pilot_sample.csv` | 8-opinion pilot (regenerate with `sample_pilot.py`) |
| `data/pilot_ai_output.jsonl` | Chunk + aggregate scores per opinion |
| `data/pilot_human.csv` | Example human ratings for agreement demo (replace with blind human codes) |
| `data/example_crosswalk.csv` | Template: `email`, `prim_key` |
| `data/example_experiment_extract.csv` | Template for merge |

## Setup

```bash
cd opinion_coding
pip install -r requirements.txt
export OPENAI_API_KEY=...   # required for real labeling (not dry-run)
```

## Pilot workflow

```bash
python scripts/sample_pilot.py --n 8 --seed 42
python scripts/label_opinions.py              # live API
# or
python scripts/label_opinions.py --dry-run    # heuristic placeholder (no key)
# After pilot revisions:
python scripts/label_opinions.py --prompt prompts/system_prompt_v2.txt

python scripts/compare_pilot_agreement.py \
  --ai data/pilot_ai_output.jsonl \
  --human data/pilot_human.csv \
  -o data/pilot_agreement_report.txt
```

Follow [human_pilot_protocol.md](human_pilot_protocol.md) for independent coding; replace `pilot_human.csv` with real blind ratings.

## Full corpus

```bash
python scripts/run_full_corpus.py \
  --input /path/to/all_cases_w_texts.csv \
  --output data/full_labels.jsonl \
  --batch-size 15 \
  --model gpt-4o-mini
```

Use `--limit N` for smoke tests. Requires `OPENAI_API_KEY` unless `--dry-run`.

## Aggregate to judge (email)

```bash
python scripts/aggregate_judge_scores.py data/full_labels.jsonl -o data/judge_level_opinion_scores.csv
```

Use rows with `"aggregate": true` in the JSONL (one per opinion).

## Merge with experiment

Export `prim_key`, `c_score`, `d_score`, `e_score`, `f_score`, `eq_focus` from Stata to CSV. Build a crosswalk from `email` to `prim_key`. Then:

```bash
python scripts/merge_with_experiment.py \
  --opinions data/judge_level_opinion_scores.csv \
  --crosswalk data/your_crosswalk.csv \
  --experiment data/your_experiment.csv \
  -o data/merged_opinions_experiment.csv
```

## Variable mapping hypothesis

`c_score` ≈ efficiency, `d_score` ≈ corrective justice, `e_score` ≈ distributive justice, `f_score` ≈ formalist–functionalist. **Verify** against `vignettes_raw` before publication (see mapping doc).
