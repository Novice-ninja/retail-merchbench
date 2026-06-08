#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import generate_atlas


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_JSON = ROOT / "reports" / "routing" / "recommendations.json"
OUTPUT_MD = ROOT / "reports" / "routing" / "segment_recommendations.md"


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def human_review_expected(text: str) -> bool:
    lowered = text.strip().lower()
    return not (lowered.startswith("no,") or lowered == "no")


def build_recommendations(data: dict[str, Any]) -> list[dict[str, Any]]:
    recommendations = []
    for segment in data.get("segment_summaries", []):
        economic_pick = segment.get("economic_pick", {})
        quality_leader = segment.get("quality_leader", {})
        recommendations.append(
            {
                "segment_id": segment["segment_id"],
                "segment_name": segment["label"],
                "status": "candidate_clears_floor",
                "benchmark_backed": True,
                "evidence_status": "full_100_item_segment_pack_scored_curated_panel",
                "eval_pack_path": f"eval_packs/{segment['segment_id']}/pack.json",
                "recommended_strategy": segment["default_route"],
                "recommendation_rationale": segment["why"],
                "deterministic_controls": [
                    item.strip()
                    for item in segment["controls"].split(",")
                    if item.strip()
                ],
                "human_review_expected": human_review_expected(segment["human_review"]),
                "human_review_boundary": segment["human_review"],
                "selected_model": {
                    "model_id": economic_pick.get("model_id"),
                    "display_name": economic_pick.get("display_name"),
                    "average_score": economic_pick.get("score"),
                    "estimated_cost_usd": economic_pick.get("estimated_cost_usd"),
                },
                "best_quality_model": {
                    "model_id": quality_leader.get("model_id"),
                    "display_name": quality_leader.get("display_name"),
                    "average_score": quality_leader.get("score"),
                    "estimated_cost_usd": quality_leader.get("estimated_cost_usd"),
                },
                "passing_candidates": segment.get("top_models", []),
                "unapplied_candidates": [],
            }
        )
    return recommendations


def recommendations_markdown(data: dict[str, Any], recommendations: list[dict[str, Any]]) -> str:
    lines = [
        "# MerchBench Routing Recommendations",
        "",
        "This report is generated from the current 100-item segment eval-pack score artifacts and mirrors the measured routing readout in the Atlas.",
        "",
        f"- Corpus: {data.get('benchmark_items', 0)} segment eval-pack items.",
        f"- Curated model panel: {data.get('model_panel_items', 0)}/{data.get('benchmark_items', 0)} scored items for the ranked provider panel.",
        "- Scope: automated routing priors until human-rater calibration and repeated-run variance are complete.",
        "",
        "| Segment | Quality Leader | Economic Pick | Human Review Boundary |",
        "| :--- | :--- | :--- | :--- |",
    ]
    for rec in recommendations:
        quality = rec["best_quality_model"]
        economic = rec["selected_model"]
        lines.append(
            "| "
            f"`{rec['segment_id']}` | "
            f"`{quality['display_name']}` ({quality['average_score']}/10) | "
            f"`{economic['display_name']}` ({economic['average_score']}/10) | "
            f"{rec['human_review_boundary']} |"
        )

    lines.extend(["", "## Segment Details", ""])
    for rec in recommendations:
        lines.extend(
            [
                f"### {rec['segment_name']}",
                "",
                f"- Recommended route: {rec['recommended_strategy']}",
                f"- Rationale: {rec['recommendation_rationale']}",
                f"- Evidence status: `{rec['evidence_status']}`",
                f"- Eval pack: `{rec['eval_pack_path']}`",
                f"- Human review expected: `{'true' if rec['human_review_expected'] else 'false'}`",
                f"- Human review boundary: {rec['human_review_boundary']}",
                f"- Deterministic controls: {', '.join(rec['deterministic_controls']) or 'None specified'}",
                "",
                "| Top Scored Models | Score | Artifact Cost |",
                "| :--- | ---: | ---: |",
            ]
        )
        for model in rec["passing_candidates"]:
            cost = float(model.get("estimated_cost_usd") or 0)
            cost_label = f"${cost:.4f}" if cost else "$0"
            lines.append(f"| `{model['display_name']}` | {model['score']}/10 | {cost_label} |")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    data = generate_atlas.build_data()
    recommendations = build_recommendations(data)
    payload = {
        "version": "0.2",
        "generated_at_utc": data.get("generated_at_utc"),
        "source": "reports/eval_packs/*_scores.json via analysis/generate_atlas.py",
        "benchmark_items": data.get("benchmark_items"),
        "model_panel_items": data.get("model_panel_items"),
        "status": "automated_routing_priors_pending_human_calibration",
        "recommendations": recommendations,
    }
    write_json(OUTPUT_JSON, payload)
    OUTPUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_MD.write_text(recommendations_markdown(data, recommendations))
    print(f"Wrote {OUTPUT_JSON.relative_to(ROOT)}")
    print(f"Wrote {OUTPUT_MD.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
