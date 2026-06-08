#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import random
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from merchbench.io import load_json, write_json


PACK_ROOT = ROOT / "eval_packs"
REPORTS_DIR = ROOT / "reports" / "eval_packs"
OUTPUT_DIR = ROOT / "human_validation"

RESPONSE_SOURCES = (
    ("reports/eval_packs/baseline_responses.json", "baseline/source_echo"),
    ("reports/eval_packs/baseline_responses.json", "baseline/keyword_guardrail"),
    ("reports/eval_packs/openai_gpt_5_mini_responses.json", "openai/gpt-5-mini"),
    ("reports/eval_packs/openai_gpt_54_mini_responses.json", "openai/gpt-5.4-mini"),
    ("reports/eval_packs/openai_gpt_55_responses.json", "openai/gpt-5.5"),
)

RATING_DIMENSIONS = (
    "evidence_quality",
    "problem_framing",
    "constraint_handling",
    "causal_reasoning",
    "uncertainty_calibration",
    "actionability",
    "economic_risk",
    "escalation_appropriateness",
)


def response_id(item_id: str, model_id: str) -> str:
    digest = hashlib.sha256(f"{item_id}|{model_id}".encode()).hexdigest()[:10]
    return f"resp_{digest}"


def pack_paths() -> list[Path]:
    return sorted(PACK_ROOT.glob("*/pack.json"))


def selected_items() -> list[tuple[dict[str, Any], dict[str, Any]]]:
    pairs: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for path in pack_paths():
        pack = load_json(path)
        for item in pack.get("items", [])[:3]:
            pairs.append((pack, item))
    return pairs


def load_response_sources() -> dict[str, dict[str, Any]]:
    sources: dict[str, dict[str, Any]] = {}
    for relative_path, model_id in RESPONSE_SOURCES:
        path = ROOT / relative_path
        if not path.exists():
            continue
        doc = load_json(path)
        model = doc.get("models", {}).get(model_id)
        if model:
            sources[model_id] = model
    return sources


def item_response(model: dict[str, Any], pack_id: str, item_id: str) -> dict[str, Any] | None:
    record = model.get("packs", {}).get(pack_id, {}).get("items", {}).get(item_id)
    if not record:
        return None
    if record.get("ok") is False and not record.get("parse_error"):
        return None
    return {
        "content": record.get("content", {}),
        "raw_text": record.get("raw_text", ""),
    }


def build_subset() -> tuple[dict[str, Any], dict[str, Any], list[dict[str, str]]]:
    sources = load_response_sources()
    subset_items = []
    answer_key = {"version": "0.1", "responses": {}}
    rating_rows: list[dict[str, str]] = []

    for pack, item in selected_items():
        responses = []
        for model_id, model in sources.items():
            response = item_response(model, pack["id"], item["id"])
            if not response:
                continue
            rid = response_id(item["id"], model_id)
            responses.append({"response_id": rid, **response})
            answer_key["responses"][rid] = {
                "model_id": model_id,
                "pack_id": pack["id"],
                "task_segment": pack["task_segment"],
                "item_id": item["id"],
            }
        rng = random.Random(item["id"])
        rng.shuffle(responses)

        subset_items.append(
            {
                "pack_id": pack["id"],
                "task_segment": pack["task_segment"],
                "item_id": item["id"],
                "title": item["title"],
                "category": item["category"],
                "risk_level": item.get("risk_level", item.get("error_downside_band")),
                "reversibility": item.get("reversibility"),
                "input": item["input"],
                "question": item["question"],
                "deterministic_controls": item.get("deterministic_controls", item.get("deterministic_checks", [])),
                "escalation_triggers": item.get("escalation_triggers", []),
                "expected_failure_mode": item.get("expected_failure_mode"),
                "responses": responses,
            }
        )
        for response in responses:
            row = {
                "rater_id": "",
                "pack_id": pack["id"],
                "task_segment": pack["task_segment"],
                "item_id": item["id"],
                "response_id": response["response_id"],
            }
            row.update({dimension: "" for dimension in RATING_DIMENSIONS})
            row["overall_notes"] = ""
            rating_rows.append(row)

    subset = {
        "version": "0.1",
        "purpose": "Blinded human-rater subset for calibrating MerchBench segment eval-pack scoring.",
        "instructions": "Raters should score each anonymous response from 1 to 5 on each dimension before seeing model identities.",
        "rating_dimensions": list(RATING_DIMENSIONS),
        "items": subset_items,
    }
    return subset, answer_key, rating_rows


def write_rating_template(rows: list[dict[str, str]]) -> None:
    path = OUTPUT_DIR / "ratings_template.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "rater_id",
        "pack_id",
        "task_segment",
        "item_id",
        "response_id",
        *RATING_DIMENSIONS,
        "overall_notes",
    ]
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    subset, answer_key, rows = build_subset()
    write_json(OUTPUT_DIR / "rater_subset.json", subset)
    write_json(OUTPUT_DIR / "rater_answer_key.json", answer_key)
    write_rating_template(rows)
    print(f"Wrote {OUTPUT_DIR.relative_to(ROOT)}/rater_subset.json with {len(subset['items'])} items.")
    print(f"Wrote {OUTPUT_DIR.relative_to(ROOT)}/ratings_template.csv with {len(rows)} response rows.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
