# Repeated-Run Plan

Repeated runs are not executed in this repository update because they require external model credits or local inference time. This file defines the next measurable protocol.

## Representative Subset

Use the 24-item human-validation subset as the first repeated-run subset. It covers three items per segment and already includes deterministic controls, risk level, reversibility, and expected failure mode metadata.

## Candidate Models

Prioritize these stored-artifact leaders or economically useful comparators:

- `openai/gpt-5.5`
- `openai/gpt-5.4-mini`
- `openai/gpt-5.4`
- `cerebras/zai-glm-4.7`
- `openai/gpt-5-mini`
- `cerebras/gpt-oss-120b`
- `groq/qwen/qwen3-32b`
- `openai/gpt-5-nano`

## Protocol

1. Run each selected model three times on the 24-item subset with temperature and seed policy recorded.
2. Expand to five repeats for models within 0.25 points of each other or models being recommended for production routing.
3. Report mean score, standard deviation, 95 percent confidence interval, segment-level variance, failed-item rate, retry count, total tokens, and latency if the provider returns it.
4. Mark score gaps below one pooled standard deviation as not meaningfully separated.
5. Recompute the Atlas only after repeated-run summaries are written.

## Required Output

- `reports/publication_metrics/repeated_run_results.json`
- `reports/publication_metrics/repeated_run_results.md`
- Updated `reports/atlas/analysis.md` rank-stability section.

## Current Status

Blocked on external model execution by design. No repeated-run claims should be made from the current single-run artifact set.
