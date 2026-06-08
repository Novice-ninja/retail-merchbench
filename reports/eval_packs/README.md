# Eval Pack Reports

This directory stores generated segment eval-pack run artifacts.

Current generated artifacts:

- `baseline_responses.json`: deterministic local baseline responses for every pack item.
- `baseline_scores.json`: automated contract scores for those responses.
- `baseline_summary.md`: compact markdown summary by model and segment.
- `scorer_robustness.md`: before/after anti-echo scorer robustness table for adversarial baselines.
- `openai_paid_ladder_results.md`: compact readout for the paid OpenAI ladder across `gpt-5-nano`, `gpt-5-mini`, `gpt-5.4-mini`, `gpt-5.4`, and `gpt-5.5`.
- Provider-specific `*_responses.json`, `*_scores.json`, `*_summary.md`, and `*_manifest.json` files for completed local, hosted, and paid runs.

Regenerate with:

```bash
make eval-pack-baselines
```

Score a future model response file with:

```bash
python3 -m merchbench.cli eval-pack-score \
  --responses path/to/model_responses.json \
  --output-scores reports/eval_packs/model_scores.json \
  --output-summary reports/eval_packs/model_summary.md
```

These baseline scores are bootstrap comparators for runner/scorer validation. They are not a substitute for model-provider runs or final human calibration. The current model-provider readout is summarized in `reports/atlas/analysis.md` and visualized in `reports/atlas/index.html`.

The benchmark corpus now contains 100 segment eval-pack items. Deterministic baselines and the curated provider panel cover `100/100`; partial OpenRouter free-tier probes and unavailable xAI runs are retained as capacity evidence but excluded from the main Atlas leaderboard.

Dry-run OpenRouter execution:

```bash
make eval-pack-openrouter-dry-run
```

Run OpenRouter execution after configuring `.env.local`:

```bash
python3 -m merchbench.cli eval-pack-openrouter --items-per-pack 1 --resume
```

Use `--items-per-pack 1` or `--items-per-pack 2` for free-tier probes. Provider run files use `openrouter_*.json` and `openrouter_*.md` names and are ignored by default until curated.
