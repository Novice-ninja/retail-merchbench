#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from merchbench.io import load_json, write_json


ATLAS_DATA = ROOT / "reports" / "atlas" / "atlas_data.json"
REPORTS_DIR = ROOT / "reports" / "publication_metrics"
METRICS_JSON = REPORTS_DIR / "economic_metrics.json"
METRICS_MD = REPORTS_DIR / "economic_metrics.md"
REPEATED_RUN_PLAN = REPORTS_DIR / "repeated_run_plan.md"

SEGMENT_WEIGHTS = {
    "low_risk_summarization": 0.8,
    "structured_extraction": 0.9,
    "constraint_checking": 1.1,
    "routine_planning_recommendation": 1.2,
    "pricing_promotion": 1.7,
    "ambiguous_planning_judgment": 1.6,
    "portfolio_tradeoff": 1.8,
    "operational_triage": 1.5,
}

QUALITY_FLOOR = 7.0


def estimated_cost_label(cost: float) -> str:
    if cost == 0:
        return "$0"
    return f"${cost:.4f}"


def weighted_average(segment_scores: dict[str, float]) -> float:
    numerator = 0.0
    denominator = 0.0
    for segment, score in segment_scores.items():
        weight = SEGMENT_WEIGHTS.get(segment, 1.0)
        numerator += float(score) * weight
        denominator += weight
    if denominator == 0:
        return 0.0
    return round(numerator / denominator, 4)


def cost_metrics(record: dict[str, Any], leader_score: float) -> dict[str, Any]:
    score = float(record["overall_average"])
    cost = float(record["estimated_cost_usd"])
    score_per_dollar = None if cost <= 0 else round(score / cost, 4)
    score_gap = round(leader_score - score, 4)
    calls_per_1000_cost = None if cost <= 0 or int(record["attempted_items"]) == 0 else round(cost * 1000 / int(record["attempted_items"]), 4)
    return {
        "model_id": record["model_id"],
        "overall_average": score,
        "risk_weighted_average": weighted_average(record.get("segment_scores", {})),
        "estimated_artifact_cost_usd": cost,
        "estimated_cost_per_1000_workflow_calls_usd": calls_per_1000_cost,
        "score_per_artifact_dollar": score_per_dollar,
        "quality_gap_to_current_leader": score_gap,
        "clears_proxy_quality_floor": score >= QUALITY_FLOOR,
        "pareto_frontier": bool(record.get("pareto_frontier")),
        "coverage": f"{record.get('attempted_items', 0)}/{record.get('available_items', record.get('attempted_items', 0))}",
    }


def response_run_counts() -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for path in sorted((ROOT / "reports" / "eval_packs").glob("*_responses.json")):
        doc = load_json(path)
        for model_id in doc.get("models", {}):
            counts[model_id] += 1
    return dict(counts)


def build_metrics() -> dict[str, Any]:
    atlas = load_json(ATLAS_DATA)
    records = atlas.get("model_records", [])
    leader_score = max((float(row["overall_average"]) for row in records), default=0.0)
    counts = response_run_counts()
    rows = [cost_metrics(record, leader_score) for record in records]
    for row in rows:
        row["stored_response_runs"] = counts.get(row["model_id"], 0)
        row["repeated_run_status"] = "single_run_only" if row["stored_response_runs"] <= 1 else "repeated_runs_available"
    rows.sort(key=lambda row: (-row["risk_weighted_average"], row["estimated_artifact_cost_usd"], row["model_id"]))
    return {
        "version": "0.1",
        "quality_floor": QUALITY_FLOOR,
        "segment_weights": SEGMENT_WEIGHTS,
        "status": "Offline metrics from stored artifacts. Repeated-run variance is planned but not yet measured.",
        "models": rows,
    }


def render_metrics(metrics: dict[str, Any]) -> str:
    rows = []
    for model in metrics["models"][:16]:
        cost = estimated_cost_label(float(model["estimated_artifact_cost_usd"]))
        per_1000 = model["estimated_cost_per_1000_workflow_calls_usd"]
        per_1000_label = "n/a" if per_1000 is None else f"${per_1000:.4f}"
        score_per_dollar = model["score_per_artifact_dollar"]
        score_per_dollar_label = "free/local" if score_per_dollar is None else f"{score_per_dollar:.2f}"
        rows.append(
            f"| `{model['model_id']}` | {model['overall_average']}/10 | {model['risk_weighted_average']}/10 | "
            f"{cost} | {per_1000_label} | {score_per_dollar_label} | {model['coverage']} | "
            f"{'Yes' if model['clears_proxy_quality_floor'] else 'No'} |"
        )
    return f"""# Publication Metrics

{metrics['status']}

The risk-weighted average is a proxy designed to keep low-risk summarization and extraction from hiding failures in pricing, portfolio, ambiguous judgment, or operational triage. It is not a retailer-specific value model.

| Model | Overall Avg | Risk-Weighted Avg | Artifact Cost | Est. Cost / 1k Calls | Score / Dollar | Coverage | Clears {metrics['quality_floor']}/10 Floor |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | :--- |
{chr(10).join(rows)}

## Interpretation Rules

- Use `overall_average` for broad diagnostic comparison.
- Use `risk_weighted_average` when evaluating merchant-facing decision support.
- Use `estimated_cost_per_1000_workflow_calls_usd` only as a rough artifact-scale proxy; production cost needs live token, cache, retry, and latency telemetry.
- Treat all `single_run_only` models as variance-unknown until repeated runs are completed.
"""


def render_repeated_run_plan(metrics: dict[str, Any]) -> str:
    candidates = [row["model_id"] for row in metrics["models"][:8] if not row["model_id"].startswith("baseline/")]
    candidate_lines = "\n".join(f"- `{model_id}`" for model_id in candidates)
    return f"""# Repeated-Run Plan

Repeated runs are not executed in this repository update because they require external model credits or local inference time. This file defines the next measurable protocol.

## Representative Subset

Use the 24-item human-validation subset as the first repeated-run subset. It covers three items per segment and already includes deterministic controls, risk level, reversibility, and expected failure mode metadata.

## Candidate Models

Prioritize these stored-artifact leaders or economically useful comparators:

{candidate_lines}

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
"""


def main() -> int:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    metrics = build_metrics()
    write_json(METRICS_JSON, metrics)
    METRICS_MD.write_text(render_metrics(metrics))
    REPEATED_RUN_PLAN.write_text(render_repeated_run_plan(metrics))
    print(f"Wrote {METRICS_JSON.relative_to(ROOT)}")
    print(f"Wrote {METRICS_MD.relative_to(ROOT)}")
    print(f"Wrote {REPEATED_RUN_PLAN.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
