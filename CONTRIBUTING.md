# Contributing

Retail MerchBench contributions should improve benchmark quality, reproducibility, or interpretability.

## Good Contributions

- New retail eval-pack items with clear metadata, deterministic controls, expected failure modes, and scoring rationale.
- Better scoring diagnostics or adversarial baselines.
- Human-rater calibration data from qualified retail practitioners.
- Provider runs with complete metadata, stored responses, scores, costs, failures, and retry notes.
- Clearer methodology, data-card, or reproducibility documentation.
- Visual or analytical improvements that make routing decisions easier to inspect.

## Eval-Pack Contributions

Before submitting new items:

1. Match the item to one of the defined retail segments in `routing/retail_decision_segments.json`.
2. Add it to the relevant `eval_packs/<segment>/pack.json`.
3. Include required metadata: ambiguity type, risk level, reversibility, deterministic controls, escalation triggers, expected failure mode, and scoring rationale.
4. Make the item answerable from the prompt alone.
5. Run `make validate`.

Do not include proprietary retailer data unless you have explicit permission to publish it.

## Scoring Contributions

Scoring changes should preserve auditability:

- Criteria must be observable from the prompt and response.
- Deterministic baselines should remain below deployable model thresholds.
- Any scoring change should re-run stored response scoring.
- Score changes should be explained in the pull request.

## Model-Result Contributions

When adding model results, include:

- Provider and model identifier.
- Date of run.
- Decoding settings.
- Prompt and system prompt if changed.
- Retry and failure information.
- Stored responses, scores, summary, and manifest.
- Cost and latency fields where the provider returns them.

## Local Checks

Run before opening a pull request:

```bash
make validate
```

For changes that affect stored results or artifacts, run:

```bash
make reproduce
```
