#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCORES_DIR = ROOT / "reports" / "eval_packs"
OUTPUT = SCORES_DIR / "full_suite_progress.md"


def load_json(path: Path) -> dict:
    with path.open() as handle:
        return json.load(handle)


def best_rows() -> list[dict]:
    best: dict[str, dict] = {}
    for path in sorted(SCORES_DIR.glob("*_scores.json")):
        doc = load_json(path)
        response_path = path.with_name(path.name.replace("_scores.json", "_responses.json"))
        responses = load_json(response_path) if response_path.exists() else {}
        for model_id, model in doc.get("models", {}).items():
            response_failures = response_failure_count(responses, model_id)
            row = {
                "model_id": model_id,
                "overall_average": model.get("overall_average", 0),
                "total_items": int(model.get("total_items") or 0),
                "available_items": int(model.get("available_items") or model.get("total_items") or 0),
                "failed_items": int(model.get("failed_items") or 0),
                "response_failures": response_failures,
                "source": str(path.relative_to(ROOT)),
            }
            prior = best.get(model_id)
            if prior is None or (row["total_items"], -row["failed_items"], row["source"]) > (
                prior["total_items"],
                -prior["failed_items"],
                prior["source"],
            ):
                best[model_id] = row
    return sorted(best.values(), key=lambda row: (row["model_id"].startswith("baseline/"), row["model_id"]))


def response_failure_count(responses: dict, model_id: str) -> int:
    if model_id.startswith("baseline/"):
        return 0
    model = responses.get("models", {}).get(model_id, {})
    failures = 0
    for pack in model.get("packs", {}).values():
        for record in pack.get("items", {}).values():
            if record.get("ok") is not True:
                failures += 1
    return failures


def render(rows: list[dict]) -> str:
    lines = [
        "# Full Suite Progress",
        "",
        "Coverage is reported against the expanded 100-item segment eval-pack corpus.",
        "",
        "| Model | Avg | Coverage | Score Failures | Response Failures | Source | Status |",
        "| :--- | ---: | ---: | ---: | ---: | :--- | :--- |",
    ]
    for row in rows:
        coverage = f"{row['total_items']}/{row['available_items']}"
        if row["total_items"] == row["available_items"] and row["failed_items"] == 0 and row["response_failures"] == 0:
            status = "complete"
        elif row["total_items"] == row["available_items"] and row["failed_items"] == 0:
            status = "score_complete_response_contract_failures"
        elif row["failed_items"]:
            status = "partial_with_failures"
        else:
            status = "partial_missing_items"
        lines.append(
            f"| `{row['model_id']}` | {row['overall_average']}/10 | {coverage} | "
            f"{row['failed_items']} | {row['response_failures']} | `{row['source']}` | {status} |"
        )
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    OUTPUT.write_text(render(best_rows()))
    print(f"Wrote {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
