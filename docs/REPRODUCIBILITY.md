# Reproducibility Guide

This guide describes how to reproduce Retail MerchBench artifacts from the public repository.

## Environment

Use Python 3.11 or newer.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Validate the Repository

```bash
make validate
```

The validator checks required release files, JSON syntax, markdown links, eval-pack schema compliance, routing artifacts, stored score artifacts, Python compilation, and unit tests.

## Offline Reproduction

```bash
make reproduce
```

This pipeline does not call model providers. It:

- regenerates deterministic segment-pack baselines;
- re-scores stored provider responses;
- regenerates routing recommendations;
- writes publication metrics;
- regenerates the visual Atlas and written report under `reports/atlas/`;
- rebuilds the 24-item human-validation subset;
- writes human-rating analysis scaffolding;
- runs repository validation.

## Regenerate Only the Atlas

```bash
make atlas
```

Primary outputs:

- `reports/atlas/index.html`
- `reports/atlas/report.md`
- `reports/atlas/atlas_data.json`
- `reports/atlas/model_frontier.svg`
- `reports/atlas/segment_heatmap.svg`
- `reports/atlas/segment_quadrants.svg`
- `reports/atlas/routing_ladder.svg`
- `reports/atlas/economic_regret.svg`

## Deterministic Baselines

```bash
make eval-pack-baselines
```

Outputs:

- `reports/eval_packs/baseline_responses.json`
- `reports/eval_packs/baseline_scores.json`
- `reports/eval_packs/baseline_summary.md`
- `reports/eval_packs/scorer_robustness.md`

## Re-Score Stored Responses

```bash
make eval-pack-score-stored
```

This recomputes scores and summaries for every `*_responses.json` file under `reports/eval_packs/`.

## Score Your Own Model Output

```bash
python3 -m merchbench.cli eval-pack-score \
  --responses path/to/model_responses.json \
  --output-scores reports/eval_packs/model_scores.json \
  --output-summary reports/eval_packs/model_summary.md
```

## Provider Runs

Copy the public template and add only the keys you need:

```bash
cp .env.example .env.local
```

OpenAI-compatible smoke test:

```bash
python3 -m merchbench.cli eval-pack-provider \
  --provider openai \
  --models gpt-4.1-nano \
  --items-per-pack 1 \
  --resume
```

Local Ollama run with memory-conscious unloading:

```bash
python3 -m merchbench.cli eval-pack-provider \
  --provider ollama \
  --models llama3.2:3b \
  --unload-after-item \
  --resume
```

## Result Metadata

Provider run manifests should preserve:

- provider;
- requested model;
- run timestamp;
- item coverage;
- retry settings;
- temperature and max tokens;
- prompt, completion, and total token counts when available;
- provider-reported failures;
- output response and score paths.

## Non-Determinism

Even at low temperature, provider-side model aliases, endpoint implementations, safety layers, pricing, and rate limits can change. Stored artifacts are the reference for published numbers. Provider reruns should be treated as fresh measurements.

## Publication Practice

For external claims, report:

- exact corpus and commit hash;
- model identifiers and providers;
- decoding settings;
- response artifacts;
- scoring code version;
- failed calls and retries;
- cost and token accounting;
- repeated-run variance where available;
- human-rater agreement where available.
