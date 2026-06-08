from __future__ import annotations

import json
import re
import shutil
import sys
import unittest
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from merchbench.eval_packs import BASELINE_IDS, score_responses


ROOT = Path(__file__).resolve().parents[1]
SEGMENT_EVAL_PACK_ROOT = ROOT / "eval_packs"
SEGMENT_EVAL_PACK_SCHEMA_PATH = ROOT / "schema" / "segment_eval_pack.schema.json"
ROUTING_RECOMMENDATIONS_PATH = ROOT / "reports" / "routing" / "recommendations.json"
EVAL_PACK_RESPONSES_PATH = ROOT / "reports" / "eval_packs" / "baseline_responses.json"
EVAL_PACK_SCORES_PATH = ROOT / "reports" / "eval_packs" / "baseline_scores.json"
MIN_SEGMENT_EVAL_ITEMS = 100
MARKDOWN_LINK = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")

SEGMENT_EVAL_ITEM_METADATA_KEYS = (
    "ambiguity_type",
    "risk_level",
    "reversibility",
    "deterministic_controls",
    "escalation_triggers",
    "expected_failure_mode",
    "scoring_rationale",
)

HIGH_RISK_SEGMENTS = {
    "pricing_promotion",
    "ambiguous_planning_judgment",
    "portfolio_tradeoff",
    "operational_triage",
}

REQUIRED_FILES = (
    ROOT / "README.md",
    ROOT / "CITATION.cff",
    ROOT / "CONTRIBUTING.md",
    ROOT / "LICENSE.md",
    ROOT / "requirements.txt",
    ROOT / "Makefile",
    ROOT / ".env.example",
    ROOT / ".gitignore",
    ROOT / ".github" / "workflows" / "validate.yml",
    ROOT / "analysis" / "analyze_human_ratings.py",
    ROOT / "analysis" / "build_human_validation_subset.py",
    ROOT / "analysis" / "generate_atlas.py",
    ROOT / "analysis" / "generate_publication_atlas.py",
    ROOT / "analysis" / "generate_publication_metrics.py",
    ROOT / "analysis" / "generate_routing_report.py",
    ROOT / "analysis" / "rescore_eval_pack_responses.py",
    ROOT / "analysis" / "summarize_eval_coverage.py",
    ROOT / "docs" / "DATA_CARD.md",
    ROOT / "docs" / "ECONOMIC_MODEL_ROUTING.md",
    ROOT / "docs" / "HUMAN_RATER_PROTOCOL.md",
    ROOT / "docs" / "METHODOLOGY.md",
    ROOT / "docs" / "PROVIDER_RUNNER.md",
    ROOT / "docs" / "REPRODUCIBILITY.md",
    ROOT / "eval_packs" / "README.md",
    ROOT / "human_validation" / "README.md",
    ROOT / "human_validation" / "rating_form.md",
    ROOT / "human_validation" / "rater_answer_key.json",
    ROOT / "human_validation" / "rater_subset.json",
    ROOT / "human_validation" / "ratings_template.csv",
    ROOT / "paper" / "retail_merchbench.tex",
    ROOT / "reports" / "atlas" / "README.md",
    ROOT / "reports" / "atlas" / "atlas_data.json",
    ROOT / "reports" / "atlas" / "index.html",
    ROOT / "reports" / "atlas" / "model_frontier.svg",
    ROOT / "reports" / "atlas" / "report.md",
    ROOT / "reports" / "atlas" / "routing_ladder.svg",
    ROOT / "reports" / "atlas" / "segment_heatmap.svg",
    ROOT / "reports" / "atlas" / "segment_quadrants.svg",
    ROOT / "reports" / "atlas" / "economic_regret.svg",
    ROOT / "reports" / "eval_packs" / "README.md",
    ROOT / "reports" / "eval_packs" / "baseline_responses.json",
    ROOT / "reports" / "eval_packs" / "baseline_scores.json",
    ROOT / "reports" / "eval_packs" / "baseline_summary.md",
    ROOT / "reports" / "eval_packs" / "scorer_robustness.md",
    ROOT / "reports" / "human_validation" / "human_rating_analysis.json",
    ROOT / "reports" / "human_validation" / "human_rating_analysis.md",
    ROOT / "reports" / "publication_metrics" / "economic_metrics.json",
    ROOT / "reports" / "publication_metrics" / "economic_metrics.md",
    ROOT / "reports" / "publication_metrics" / "repeated_run_plan.md",
    ROOT / "reports" / "routing" / "README.md",
    ROOT / "reports" / "routing" / "recommendations.json",
    ROOT / "reports" / "routing" / "segment_recommendations.md",
    ROOT / "routing" / "default_policies.json",
    ROOT / "routing" / "model_profiles.json",
    ROOT / "routing" / "provider_registry.json",
    ROOT / "routing" / "retail_decision_segments.json",
    ROOT / "schema" / "segment_eval_pack.schema.json",
    ROOT / "tests" / "test_eval_pack_scorer.py",
)

FORBIDDEN_PATH_PARTS = {
    ".venv",
    "__pycache__",
    ".pytest_cache",
    ".playwright-mcp",
}

FORBIDDEN_FILES = {
    ".env.local",
}


def load_json(path: Path) -> Any:
    with path.open() as handle:
        return json.load(handle)


def remove_generated_caches() -> None:
    for path in sorted(ROOT.rglob("__pycache__")):
        shutil.rmtree(path, ignore_errors=True)
    for path in sorted(ROOT.rglob("*.pyc")):
        if ".git" not in path.parts:
            path.unlink(missing_ok=True)


def validate_required_files() -> list[str]:
    return [f"missing required file: {path.relative_to(ROOT)}" for path in REQUIRED_FILES if not path.exists()]


def validate_no_forbidden_files() -> list[str]:
    errors: list[str] = []
    for path in ROOT.rglob("*"):
        if ".git" in path.parts:
            continue
        if any(part in FORBIDDEN_PATH_PARTS for part in path.parts):
            errors.append(f"forbidden generated/cache path: {path.relative_to(ROOT)}")
        if path.name in FORBIDDEN_FILES:
            errors.append(f"forbidden local secret file: {path.relative_to(ROOT)}")
        if path.suffix == ".pyc":
            errors.append(f"forbidden compiled Python file: {path.relative_to(ROOT)}")
    return errors


def validate_all_json() -> list[str]:
    errors: list[str] = []
    for path in sorted(ROOT.rglob("*.json")):
        if ".git" in path.parts:
            continue
        try:
            load_json(path)
        except json.JSONDecodeError as exc:
            errors.append(f"{path.relative_to(ROOT)}: invalid JSON: {exc}")
    return errors


def validate_markdown_links() -> list[str]:
    errors: list[str] = []
    for path in sorted(ROOT.rglob("*.md")):
        if ".git" in path.parts or ".venv" in path.parts:
            continue
        text = path.read_text()
        for match in MARKDOWN_LINK.finditer(text):
            raw_target = match.group(1).strip()
            target = raw_target.split("#", 1)[0].strip()
            if not target or target.startswith(("http://", "https://", "mailto:")):
                continue
            target = target.strip("<>")
            candidate = (path.parent / target).resolve()
            try:
                candidate.relative_to(ROOT)
            except ValueError:
                errors.append(f"{path.relative_to(ROOT)}: link escapes repo: {raw_target}")
                continue
            if not candidate.exists():
                errors.append(f"{path.relative_to(ROOT)}: broken local link: {raw_target}")
    return errors


def validate_segment_eval_packs() -> list[str]:
    schema = load_json(SEGMENT_EVAL_PACK_SCHEMA_PATH)
    validator = Draft202012Validator(schema)
    errors: list[str] = []
    pack_paths = sorted(SEGMENT_EVAL_PACK_ROOT.glob("*/pack.json"))
    if not pack_paths:
        return ["no segment eval packs found"]

    segment_ids = set()
    item_ids = set()
    total_items = 0
    hard_items = 0
    high_downside_items = 0
    high_risk_segment_items = 0

    for path in pack_paths:
        pack = load_json(path)
        segment_id = pack.get("task_segment")
        segment_ids.add(segment_id)
        items = pack.get("items", [])
        total_items += len(items)
        if path.parent.name != segment_id:
            errors.append(f"{path.relative_to(ROOT)}: directory name does not match task_segment {segment_id}")
        for error in sorted(validator.iter_errors(pack), key=lambda item: list(item.path)):
            location = ".".join(map(str, error.path)) or "<root>"
            errors.append(f"{path.relative_to(ROOT)}:{location}: {error.message}")
        for item in items:
            item_id = item.get("id")
            if item_id in item_ids:
                errors.append(f"{path.relative_to(ROOT)}: duplicate item id {item_id}")
            item_ids.add(item_id)
            missing = [key for key in SEGMENT_EVAL_ITEM_METADATA_KEYS if not item.get(key)]
            if missing:
                errors.append(f"{path.relative_to(ROOT)}:{item_id}: missing metadata {missing}")
            expected_output = item.get("expected_output", {})
            if not isinstance(expected_output, dict) or not expected_output:
                errors.append(f"{path.relative_to(ROOT)}:{item_id}: expected_output must be a non-empty object")
            if item.get("difficulty") == "hard":
                hard_items += 1
                if len(item.get("deterministic_checks", [])) < 2:
                    errors.append(f"{path.relative_to(ROOT)}:{item_id}: hard item needs at least two deterministic checks")
            if item.get("error_downside_band") in {"high", "severe"}:
                high_downside_items += 1
                if not item.get("escalation_triggers"):
                    errors.append(f"{path.relative_to(ROOT)}:{item_id}: high-downside item needs escalation triggers")
            if segment_id in HIGH_RISK_SEGMENTS:
                high_risk_segment_items += 1

    if total_items < MIN_SEGMENT_EVAL_ITEMS:
        errors.append(f"segment eval packs contain {total_items} items; expected at least {MIN_SEGMENT_EVAL_ITEMS}")
    if len(segment_ids) != 8:
        errors.append(f"expected 8 task segments, found {len(segment_ids)}: {sorted(segment_ids)}")
    if hard_items < 50:
        errors.append(f"expected at least 50 hard segment items, found {hard_items}")
    if high_downside_items < 35:
        errors.append(f"expected at least 35 high/severe downside items, found {high_downside_items}")
    if high_risk_segment_items < 40:
        errors.append(f"expected at least 40 high-risk segment items, found {high_risk_segment_items}")
    return errors


def validate_routing_reports() -> list[str]:
    errors: list[str] = []
    recommendations = load_json(ROUTING_RECOMMENDATIONS_PATH)
    recs = recommendations.get("recommendations", [])
    if len(recs) != 8:
        errors.append(f"routing recommendations contain {len(recs)} segments; expected 8")
    for rec in recs:
        if not rec.get("segment_id"):
            errors.append("routing recommendation missing segment_id")
        if not rec.get("recommended_strategy"):
            errors.append(f"{rec.get('segment_id')}: missing recommended_strategy")
        if "human_review_expected" not in rec:
            errors.append(f"{rec.get('segment_id')}: missing human_review_expected")
    return errors


def validate_eval_pack_reports() -> list[str]:
    errors: list[str] = []
    scores = load_json(EVAL_PACK_SCORES_PATH)
    responses = load_json(EVAL_PACK_RESPONSES_PATH)
    model_ids = set(scores.get("models", {}))
    response_model_ids = set(responses.get("models", {}))
    if model_ids != set(BASELINE_IDS):
        errors.append(f"baseline score models are {sorted(model_ids)}; expected {sorted(BASELINE_IDS)}")
    if response_model_ids != set(BASELINE_IDS):
        errors.append(f"baseline response models are {sorted(response_model_ids)}; expected {sorted(BASELINE_IDS)}")
    recomputed = score_responses(SEGMENT_EVAL_PACK_ROOT, responses)
    if recomputed != scores:
        errors.append("baseline_scores.json is stale relative to baseline_responses.json")
    curated_model_ids: set[str] = set()
    for path in sorted((ROOT / "reports" / "eval_packs").glob("*_scores.json")):
        if path.name == "baseline_scores.json":
            continue
        artifact = load_json(path)
        curated_model_ids.update(artifact.get("models", {}).keys())
    if len(curated_model_ids) < 14:
        errors.append(f"expected at least 14 scored real models, found {len(curated_model_ids)}")
    return errors


def validate_atlas_artifacts() -> list[str]:
    data = load_json(ROOT / "reports" / "atlas" / "atlas_data.json")
    errors: list[str] = []
    if data.get("benchmark_items") != 100:
        errors.append("atlas_data.json benchmark_items should be 100")
    if len(data.get("model_records", [])) < 14:
        errors.append("atlas_data.json should include at least 14 model records")
    forbidden_release_label = "v" + "2"
    if any(forbidden_release_label in str(value).lower() for value in (data.get("artifact_name"), data.get("data_caveat"))):
        errors.append("atlas_data.json should not use release-label wording")
    return errors


def validate_python_compiles() -> list[str]:
    errors: list[str] = []
    for path in sorted(ROOT.rglob("*.py")):
        if ".git" in path.parts or ".venv" in path.parts:
            continue
        try:
            compile(path.read_text(encoding="utf-8"), str(path), "exec")
        except SyntaxError as exc:
            errors.append(f"{path.relative_to(ROOT)}: {exc}")
    return errors


def validate_unit_tests() -> list[str]:
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"))
    result = unittest.TextTestRunner(stream=sys.stdout, verbosity=0).run(suite)
    errors = []
    for case, traceback in result.failures + result.errors:
        errors.append(f"{case.id()}: {traceback.splitlines()[-1] if traceback else 'test failed'}")
    return errors


def main() -> int:
    remove_generated_caches()
    checks = (
        ("required files", validate_required_files),
        ("forbidden files", validate_no_forbidden_files),
        ("json syntax", validate_all_json),
        ("markdown links", validate_markdown_links),
        ("segment eval packs", validate_segment_eval_packs),
        ("routing reports", validate_routing_reports),
        ("eval pack reports", validate_eval_pack_reports),
        ("atlas artifacts", validate_atlas_artifacts),
        ("python compilation", validate_python_compiles),
        ("unit tests", validate_unit_tests),
    )
    all_errors: list[str] = []
    for label, check in checks:
        errors = check()
        if errors:
            print(f"FAIL {label}")
            for error in errors:
                print(f"  - {error}")
            all_errors.extend(errors)
        else:
            print(f"OK {label}")
    if all_errors:
        print(f"Repository validation failed with {len(all_errors)} issue(s).")
        remove_generated_caches()
        return 1
    print("Repository validation passed.")
    remove_generated_caches()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
