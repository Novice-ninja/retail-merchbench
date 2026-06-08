#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from collections import defaultdict
from pathlib import Path
from statistics import mean, pstdev
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from merchbench.io import load_json, write_json


HUMAN_DIR = ROOT / "human_validation"
REPORT_DIR = ROOT / "reports" / "human_validation"
REPORT_JSON = REPORT_DIR / "human_rating_analysis.json"
REPORT_MD = REPORT_DIR / "human_rating_analysis.md"

DIMENSIONS = (
    "evidence_quality",
    "problem_framing",
    "constraint_handling",
    "causal_reasoning",
    "uncertainty_calibration",
    "actionability",
    "economic_risk",
    "escalation_appropriateness",
)


def parse_score(value: str) -> float | None:
    value = str(value or "").strip()
    if not value:
        return None
    try:
        score = float(value)
    except ValueError:
        return None
    if 1 <= score <= 5:
        return score
    return None


def completed_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(newline="") as handle:
        for row in csv.DictReader(handle):
            scores = {dimension: parse_score(row.get(dimension, "")) for dimension in DIMENSIONS}
            valid_scores = [score for score in scores.values() if score is not None]
            if len(valid_scores) != len(DIMENSIONS):
                continue
            row = dict(row)
            row["dimension_scores"] = scores
            row["composite_10"] = round(mean(valid_scores) * 2, 4)
            rows.append(row)
    return rows


def load_answer_key(path: Path) -> dict[str, Any]:
    doc = load_json(path)
    return doc.get("responses", {})


def score_lookup() -> dict[tuple[str, str], float]:
    lookup: dict[tuple[str, str], float] = {}
    for path in sorted((ROOT / "reports" / "eval_packs").glob("*_scores.json")):
        doc = load_json(path)
        for model_id, model in doc.get("models", {}).items():
            for pack in model.get("packs", {}).values():
                for item_id, item_score in pack.get("item_scores", {}).items():
                    lookup[(model_id, item_id)] = float(item_score.get("total", 0))
    return lookup


def pearson(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) < 2 or len(xs) != len(ys):
        return None
    mx, my = mean(xs), mean(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den_x = math.sqrt(sum((x - mx) ** 2 for x in xs))
    den_y = math.sqrt(sum((y - my) ** 2 for y in ys))
    if den_x == 0 or den_y == 0:
        return None
    return round(num / (den_x * den_y), 4)


def aggregate(rows: list[dict[str, Any]], answer_key: dict[str, Any]) -> dict[str, Any]:
    by_response: dict[str, list[float]] = defaultdict(list)
    by_model: dict[str, list[float]] = defaultdict(list)
    by_segment: dict[str, list[float]] = defaultdict(list)
    per_response_rows = []

    automated = score_lookup()
    human_scores: list[float] = []
    automated_scores: list[float] = []

    for row in rows:
        rid = row["response_id"]
        key = answer_key.get(rid, {})
        model_id = key.get("model_id", "unknown")
        segment = key.get("task_segment", row.get("task_segment", "unknown"))
        item_id = key.get("item_id", row.get("item_id", "unknown"))
        score = float(row["composite_10"])
        by_response[rid].append(score)
        by_model[model_id].append(score)
        by_segment[segment].append(score)
        auto = automated.get((model_id, item_id))
        if auto is not None:
            human_scores.append(score)
            automated_scores.append(auto)

    for rid, values in sorted(by_response.items()):
        key = answer_key.get(rid, {})
        per_response_rows.append(
            {
                "response_id": rid,
                "model_id": key.get("model_id", "unknown"),
                "task_segment": key.get("task_segment", "unknown"),
                "item_id": key.get("item_id", "unknown"),
                "ratings": len(values),
                "mean_human_score": round(mean(values), 4),
                "stddev_human_score": round(pstdev(values), 4) if len(values) > 1 else 0,
            }
        )

    return {
        "version": "0.1",
        "completed_rating_rows": len(rows),
        "response_summary": per_response_rows,
        "model_summary": [
            {
                "model_id": model_id,
                "ratings": len(values),
                "mean_human_score": round(mean(values), 4),
                "stddev_human_score": round(pstdev(values), 4) if len(values) > 1 else 0,
            }
            for model_id, values in sorted(by_model.items())
        ],
        "segment_summary": [
            {
                "task_segment": segment,
                "ratings": len(values),
                "mean_human_score": round(mean(values), 4),
                "stddev_human_score": round(pstdev(values), 4) if len(values) > 1 else 0,
            }
            for segment, values in sorted(by_segment.items())
        ],
        "automated_human_pearson": pearson(automated_scores, human_scores),
        "automated_human_pairs": len(automated_scores),
    }


def render_markdown(summary: dict[str, Any]) -> str:
    if summary["completed_rating_rows"] == 0:
        return """# Human Rating Analysis

No completed human ratings were found in the input file. This is expected until retail practitioners fill `human_validation/ratings_template.csv` or a copy of it.
"""

    model_rows = "\n".join(
        f"| `{row['model_id']}` | {row['ratings']} | {row['mean_human_score']}/10 | {row['stddev_human_score']} |"
        for row in summary["model_summary"]
    )
    segment_rows = "\n".join(
        f"| `{row['task_segment']}` | {row['ratings']} | {row['mean_human_score']}/10 | {row['stddev_human_score']} |"
        for row in summary["segment_summary"]
    )
    correlation = summary["automated_human_pearson"]
    correlation_label = "n/a" if correlation is None else str(correlation)
    return f"""# Human Rating Analysis

Completed rating rows: {summary['completed_rating_rows']}

Automated-vs-human Pearson correlation: {correlation_label} across {summary['automated_human_pairs']} matched response/item pairs.

## Model Summary

| Model | Ratings | Mean Human Score | Stddev |
| :--- | ---: | ---: | ---: |
{model_rows}

## Segment Summary

| Segment | Ratings | Mean Human Score | Stddev |
| :--- | ---: | ---: | ---: |
{segment_rows}
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze completed MerchBench human ratings.")
    parser.add_argument("--ratings", type=Path, default=HUMAN_DIR / "ratings_template.csv")
    parser.add_argument("--answer-key", type=Path, default=HUMAN_DIR / "rater_answer_key.json")
    parser.add_argument("--output-json", type=Path, default=REPORT_JSON)
    parser.add_argument("--output-md", type=Path, default=REPORT_MD)
    args = parser.parse_args()

    rows = completed_rows(args.ratings)
    answer_key = load_answer_key(args.answer_key) if args.answer_key.exists() else {}
    summary = aggregate(rows, answer_key)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    write_json(args.output_json, summary)
    args.output_md.write_text(render_markdown(summary))
    print(f"Wrote {args.output_json.relative_to(ROOT)}")
    print(f"Wrote {args.output_md.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
