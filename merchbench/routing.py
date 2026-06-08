from __future__ import annotations

from typing import Any


def build_frontier(
    score_summary: dict[str, dict[str, Any]],
    model_profiles: dict[str, Any],
) -> list[dict[str, Any]]:
    """Join quality scores to model profile metadata."""
    profiles = model_profiles.get("models", model_profiles)
    rows: list[dict[str, Any]] = []
    for model_id, score in score_summary.items():
        profile = profiles.get(model_id, {})
        rows.append(
            {
                **score,
                "model_id": model_id,
                "display_name": profile.get("display_name", model_id),
                "cluster": profile.get("cluster", "Unprofiled"),
                "strategy_tier": profile.get("strategy_tier", "unknown"),
                "cost_index": float(profile.get("cost_index", 10)),
                "latency_index": float(profile.get("latency_index", 10)),
                "notes": profile.get("notes", ""),
            }
        )
    return sorted(rows, key=lambda row: (-row["judgment_index"], row["cost_index"], row["latency_index"], row["model_id"]))


def clears_dimension_floors(row: dict[str, Any], required_dimension_floor: dict[str, float]) -> bool:
    dimensions = row.get("dimension_indices", {})
    for dimension, floor in required_dimension_floor.items():
        if float(dimensions.get(dimension, 0)) < float(floor):
            return False
    return True


def economic_fit(row: dict[str, Any], policy: dict[str, Any]) -> float:
    """Higher is better. Cost and latency are normalized 0-10 burdens."""
    cost_weight = float(policy.get("cost_weight", 0.4))
    latency_weight = float(policy.get("latency_weight", 0.3))
    return round(
        float(row["judgment_index"])
        - (float(row["cost_index"]) * 10 * cost_weight)
        - (float(row["latency_index"]) * 10 * latency_weight),
        2,
    )


def is_benchmark_backed(policy: dict[str, Any]) -> bool:
    """Return true when current score artifacts directly support a segment policy."""
    evidence_status = str(policy.get("evidence_status", ""))
    if evidence_status.startswith("routing_prior"):
        return False
    return "not_yet_covered" not in evidence_status


def _strategy_recommendation(segment: dict[str, Any], selected: dict[str, Any] | None) -> str:
    default_strategy = segment.get("default_strategy", "needs_policy_definition")
    fallback_strategy = segment.get("fallback_strategy")

    if not selected:
        if fallback_strategy:
            return f"{default_strategy}; fallback {fallback_strategy}"
        return default_strategy

    display_name = selected["display_name"]
    if default_strategy == "rules_only":
        fallback = fallback_strategy or selected.get("strategy_tier", "model")
        return f"rules_only; fallback strategy {fallback}; scored candidate {display_name}"
    if default_strategy == "cascade":
        return f"cascade anchored by {display_name}"
    if default_strategy == "frontier_plus_human_review":
        return f"{display_name} with human review"
    return f"{display_name} via {default_strategy}"


def recommend_for_segment(
    segment: dict[str, Any],
    policy: dict[str, Any],
    frontier: list[dict[str, Any]],
) -> dict[str, Any]:
    floor = float(policy.get("quality_floor", 0))
    required_dimensions = policy.get("required_dimension_floor", {})
    candidates = [
        {**row, "economic_fit": economic_fit(row, policy)}
        for row in frontier
        if float(row["average_score"]) >= floor and clears_dimension_floors(row, required_dimensions)
    ]
    candidates = sorted(candidates, key=lambda row: (-row["economic_fit"], -row["judgment_index"], row["cost_index"]))
    best_quality = max(frontier, key=lambda row: row["judgment_index"], default=None)
    benchmark_backed = is_benchmark_backed(policy)
    selected = candidates[0] if benchmark_backed and candidates else None

    if not benchmark_backed:
        recommendation = _strategy_recommendation(segment, None)
        status = "routing_prior_only"
    elif selected:
        recommendation = _strategy_recommendation(segment, selected)
        status = "candidate_clears_floor"
    else:
        recommendation = _strategy_recommendation(segment, None)
        status = "no_current_candidate_clears_floor"

    frontier_delta = None
    if selected and best_quality:
        frontier_delta = round(float(best_quality["judgment_index"]) - float(selected["judgment_index"]), 2)

    return {
        "segment_id": segment["id"],
        "segment_name": segment["name"],
        "default_strategy": segment.get("default_strategy"),
        "recommended_strategy": recommendation,
        "status": status,
        "benchmark_backed": benchmark_backed,
        "quality_floor": floor,
        "required_dimension_floor": required_dimensions,
        "human_review_expected": bool(policy.get("human_review_expected", segment.get("default_strategy") == "frontier_plus_human_review")),
        "deterministic_controls": segment.get("deterministic_controls", []),
        "escalation_triggers": segment.get("escalation_triggers", []),
        "evidence_status": policy.get("evidence_status", "unspecified"),
        "eval_pack_path": policy.get("eval_pack_path"),
        "selected_model": selected,
        "best_quality_model": best_quality,
        "frontier_delta_vs_selected": frontier_delta,
        "passing_candidates": candidates[:5] if benchmark_backed else [],
        "unapplied_candidates": candidates[:5] if not benchmark_backed else [],
    }


def recommend_segments(
    segments_doc: dict[str, Any],
    policies_doc: dict[str, Any],
    frontier: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    policies = policies_doc.get("policies", policies_doc)
    recommendations = []
    for segment in segments_doc.get("segments", []):
        policy = policies.get(segment["id"], {})
        recommendations.append(recommend_for_segment(segment, policy, frontier))
    return recommendations
