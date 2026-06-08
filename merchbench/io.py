from __future__ import annotations

import json
from pathlib import Path
from statistics import mean
from typing import Any


DIMENSION_SCALES = {
    "evidence_quality": 3,
    "problem_framing": 3,
    "constraint_handling": 3,
    "uncertainty_calibration": 3,
    "actionability": 3,
    "economic_impact": 5,
}


def load_json(path: str | Path) -> Any:
    with Path(path).open() as handle:
        return json.load(handle)


def write_json(path: str | Path, payload: Any) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2) + "\n")


def summarize_scores(score_paths: list[str | Path]) -> dict[str, dict[str, Any]]:
    """Combine MerchBench score documents into per-model summaries."""
    totals_by_model: dict[str, list[float]] = {}
    dimensions_by_model: dict[str, dict[str, list[float]]] = {}

    for path in score_paths:
        score_doc = load_json(path)
        for model, record in score_doc.get("models", {}).items():
            totals = totals_by_model.setdefault(model, [])
            dimensions = dimensions_by_model.setdefault(
                model,
                {dimension: [] for dimension in DIMENSION_SCALES},
            )
            for score in record.get("scores", {}).values():
                totals.append(float(score["total"]))
                for dimension, scale in DIMENSION_SCALES.items():
                    raw = float(score.get("dimensions", {}).get(dimension, {}).get("score", 0))
                    dimensions[dimension].append((raw / scale) * 100)

    summaries: dict[str, dict[str, Any]] = {}
    for model, totals in totals_by_model.items():
        dimension_indices = {
            dimension: round(mean(values), 2) if values else 0
            for dimension, values in dimensions_by_model[model].items()
        }
        summaries[model] = {
            "model": model,
            "scenario_count": len(totals),
            "average_score": round(mean(totals), 4) if totals else 0,
            "min_score": min(totals) if totals else 0,
            "max_score": max(totals) if totals else 0,
            "judgment_index": round((mean(totals) / 20) * 100, 2) if totals else 0,
            "dimension_indices": dimension_indices,
        }
    return summaries
