# Pilot run notes

- **Sample:** `pilot_sample.csv` — 8 opinions (`sample_pilot.py`, seed 42, max length 15k chars).
- **AI run:** `pilot_ai_output.jsonl` produced with `label_opinions.py --dry-run` (no `OPENAI_API_KEY` in CI). Re-run without `--dry-run` after setting the key for real scores and quotes.
- **Human proxy:** `pilot_human.csv` contains researcher-style ratings for pipeline testing. Replace with **blind independent** human codes per `human_pilot_protocol.md`.
- **Agreement (dry-run vs proxy human):** see `pilot_agreement_report.txt`. Low `r` on formalist_functionalist is expected for the keyword heuristic; expect improvement with a real model and adjudicated gold standards.
