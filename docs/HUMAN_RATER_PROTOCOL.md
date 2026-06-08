# Human-Rater Protocol

This protocol calibrates MerchBench automated scores against retail-practitioner judgment. It is intentionally separate from model execution: raters see the item context, the task question, deterministic controls, and anonymous responses, but not model names.

## Purpose

The goal is to measure whether MerchBench automated scoring aligns with expert retail judgment on evidence quality, problem framing, constraint handling, causal reasoning, uncertainty calibration, actionability, economic risk, and escalation appropriateness.

The protocol does not produce final public rankings until enough independent raters complete the subset and inter-rater reliability is reported.

## Rater Pool

Preferred raters are current or former retail merchants, planners, allocators, pricing leaders, supply-chain partners, store-operations leaders, or retail AI product owners.

Minimum target for the first calibration pass:

- 3 independent raters.
- 24 items across all 8 task segments.
- At least 5 anonymous responses per item when available.

## Blind Subset

Generate the subset with:

```bash
make human-validation-subset
```

Primary files:

- `human_validation/rater_subset.json`: item context plus anonymous responses.
- `human_validation/ratings_template.csv`: one row per rater-response rating.
- `human_validation/rater_answer_key.json`: hidden mapping from anonymous response IDs to source models or baselines.

Do not share `rater_answer_key.json` with raters.

## Rating Scale

Each dimension is scored from 1 to 5.

- 1: unsafe or materially wrong.
- 2: weak; misses important retail signal or control.
- 3: usable draft but requires meaningful correction.
- 4: strong; minor gaps or caveats.
- 5: retail-practitioner quality for the requested task.

Dimensions:

- Evidence quality.
- Problem framing.
- Constraint handling.
- Causal reasoning.
- Uncertainty calibration.
- Actionability.
- Economic risk.
- Escalation appropriateness.

## Rater Instructions

Raters should judge the answer for the specific task segment, not generic writing quality. Penalize fluent responses that ignore constraints, overstate evidence, skip causal drivers, hide uncertainty, or fail to escalate high-downside cases.

Raters should not reward source echoing unless the task is purely summarization and the output preserves caveats without becoming a recommendation.

## Analysis

After ratings are collected, run:

```bash
python3 analysis/analyze_human_ratings.py \
  --ratings human_validation/ratings_template.csv
```

The script writes:

- `reports/human_validation/human_rating_analysis.json`
- `reports/human_validation/human_rating_analysis.md`

Report at least:

- Mean human score by model and segment.
- Score dispersion by model and segment.
- Automated-vs-human correlation.
- Disagreement examples where automated and human ratings diverge.

## Publication Boundary

Until this protocol has completed ratings, MerchBench findings should be described as automated routing priors and scorer diagnostics, not final human-validated model rankings.
