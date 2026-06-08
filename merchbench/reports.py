from __future__ import annotations

from pathlib import Path
from typing import Any


def _selected_label(rec: dict[str, Any]) -> str:
    selected = rec.get("selected_model")
    if rec.get("status") == "routing_prior_only":
        return f"Routing prior only: `{rec['recommended_strategy']}` until segment-specific scores exist."
    if not selected:
        return f"No current scored candidate clears the configured floor; use `{rec['recommended_strategy']}`."
    return (
        f"`{rec['recommended_strategy']}` "
        f"({selected['average_score']}/20 avg, fit {selected['economic_fit']})"
    )


def recommendations_markdown(recommendations: list[dict[str, Any]]) -> str:
    lines = [
        "# MerchBench Routing Recommendations",
        "",
        "This report is generated from current MerchBench score artifacts, model profiles, retail decision segments, and default routing policies.",
        "",
        "| Segment | Recommendation | Evidence | Human Review |",
        "| :--- | :--- | :--- | :--- |",
    ]
    for rec in recommendations:
        human_review = "Yes" if rec["human_review_expected"] else "No"
        lines.append(
            f"| `{rec['segment_id']}` | {_selected_label(rec)} | {rec['evidence_status']} | {human_review} |"
        )

    lines.extend(["", "## Segment Details", ""])
    for rec in recommendations:
        lines.extend(
            [
                f"### {rec['segment_name']}",
                "",
                f"- Default strategy: `{rec.get('default_strategy')}`",
                f"- Status: `{rec['status']}`",
                f"- Benchmark-backed: `{'true' if rec['benchmark_backed'] else 'false'}`",
                f"- Quality floor: `{rec['quality_floor']}/20`",
                f"- Recommendation: {_selected_label(rec)}",
                f"- Evidence status: `{rec['evidence_status']}`",
                f"- Eval pack: `{rec.get('eval_pack_path') or 'not specified'}`",
                f"- Human review expected: `{'true' if rec['human_review_expected'] else 'false'}`",
                f"- Deterministic controls: {', '.join(rec['deterministic_controls']) or 'None specified'}",
                f"- Escalation triggers: {', '.join(rec['escalation_triggers']) or 'None specified'}",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def write_markdown(path: str | Path, recommendations: list[dict[str, Any]]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(recommendations_markdown(recommendations))
