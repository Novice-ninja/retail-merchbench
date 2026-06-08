# Retail MerchBench

Retail MerchBench is a research benchmark and model-routing toolkit for retail merchandise-planning workflows. It evaluates whether language models are economically sufficient for specific classes of retail decisions, not just whether they top a generic leaderboard.

The benchmark focuses on merchant and planner judgment: noisy demand reads, contaminated signals, operational constraints, open-to-buy pressure, vendor commitments, pricing and promotion risk, portfolio tradeoffs, and operational exception triage.

## What This Repository Contains

- A 100-item segment eval-pack corpus across eight retail decision segments.
- Stored full-suite results for a 14-model curated panel across local, hosted, and paid providers.
- Deterministic adversarial baselines that audit scorer robustness.
- A provider-agnostic runner for new model evaluations.
- A visual Atlas with cost-quality frontiers, segment heatmaps, routing quadrants, and workflow ladders.
- A LaTeX research paper describing the benchmark, methodology, results, limitations, and reproducibility protocol.
- Human-rater protocol scaffolding for retail-practitioner calibration.

## Core Question

For a given retail workflow, which model or workflow tier is economically sufficient once quality, latency, inference cost, downside risk, reversibility, deterministic controls, and human review are considered?

## Current Evidence Package

The release includes:

- 100 segment eval-pack items.
- Eight decision segments:
  - Low-risk summarization
  - Structured extraction
  - Constraint checking
  - Routine planning recommendation
  - Pricing and promotion
  - Ambiguous planning judgment
  - Portfolio tradeoff
  - Operational triage
- 14 real models with full scored coverage in the curated panel.
- Stored response and score artifacts for reproducibility.
- Publication metrics, routing recommendations, and visual artifacts.

## Headline Findings

- `openai/gpt-5.5` is the overall quality leader in the stored run.
- `openai/gpt-5.4-mini` is the broad economic default: near-frontier quality at materially lower observed artifact cost.
- `openai/gpt-5-mini` is the strongest cheap paid specialist for summarization, structured extraction, and portfolio triage.
- `cerebras/zai-glm-4.7` is the strongest free hosted comparator in the current artifact set.
- Pricing and promotion, routine planning, portfolio tradeoff, and high-risk operational triage still require deterministic controls or human review.

These are automated routing priors, not final human-validated production recommendations.

## Repository Map

| Path | Purpose |
| :--- | :--- |
| `eval_packs/` | Source 100-item retail eval corpus. |
| `merchbench/` | Scoring, provider runner, routing, and I/O library code. |
| `analysis/` | Artifact generation, rescoring, routing reports, and publication metrics. |
| `reports/atlas/` | Public visual Atlas and written report. |
| `reports/eval_packs/` | Stored model responses, scores, summaries, and scorer robustness report. |
| `reports/publication_metrics/` | Risk-weighted and cost-normalized metrics. |
| `reports/routing/` | Segment-level routing recommendations. |
| `paper/retail_merchbench.tex` | LaTeX research paper. |
| `docs/` | Methodology, data card, reproducibility, provider runner, and human-rater protocol. |
| `human_validation/` | Blind subset and rating-form scaffolding. |
| `routing/` | Segment policies, model profiles, and provider registry. |
| `schema/` | Eval-pack JSON schema. |
| `tests/` | Unit tests for scoring behavior. |

## Quickstart

Use Python 3.11 or newer.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
make validate
```

## Offline Reproduction

This rebuilds deterministic baselines, re-scores stored model responses, regenerates routing recommendations, publication metrics, the visual Atlas, and validation checks. It does not call model providers.

```bash
make reproduce
```

Open:

- `reports/atlas/index.html`
- `reports/atlas/report.md`
- `paper/retail_merchbench.tex`

## Run a New Model

Copy the public environment template and add only the provider keys you need:

```bash
cp .env.example .env.local
```

Small smoke test:

```bash
python3 -m merchbench.cli eval-pack-provider \
  --provider openai \
  --models gpt-4.1-nano \
  --items-per-pack 1 \
  --resume
```

Memory-conscious local Ollama run:

```bash
python3 -m merchbench.cli eval-pack-provider \
  --provider ollama \
  --models llama3.2:3b \
  --unload-after-item \
  --resume
```

Score an existing response artifact:

```bash
python3 -m merchbench.cli eval-pack-score \
  --responses path/to/model_responses.json \
  --output-scores reports/eval_packs/model_scores.json \
  --output-summary reports/eval_packs/model_summary.md
```

## Validation

```bash
make validate
```

The validator checks required release files, JSON syntax, markdown links, eval-pack schema compliance, routing artifacts, stored score artifacts, Python compilation, and unit tests.

## Interpretation Boundary

Retail MerchBench is designed to support model-routing decisions. It should be treated as:

- a public methodology and artifact package;
- a benchmark corpus for retail-specific judgment;
- a routing-prior generator for model, rules, cascade, and human-review workflow design.

It should not be treated as:

- a universal model leaderboard;
- a retailer-specific cost model;
- proof of autonomous readiness for pricing, portfolio, safety, legal, or executive override decisions.

## License

Code is released under the MIT License. Benchmark data, paper text, and reports are released under CC BY 4.0 unless otherwise noted.
