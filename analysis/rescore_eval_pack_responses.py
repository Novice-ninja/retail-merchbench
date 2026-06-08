#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from merchbench.eval_packs import score_responses, write_scores_markdown
from merchbench.io import load_json, write_json


PACK_ROOT = ROOT / "eval_packs"
REPORTS_DIR = ROOT / "reports" / "eval_packs"


def score_path_for(response_path: Path) -> Path:
    return response_path.with_name(response_path.name.replace("_responses.json", "_scores.json"))


def summary_path_for(response_path: Path) -> Path:
    return response_path.with_name(response_path.name.replace("_responses.json", "_summary.md"))


def main() -> int:
    response_paths = sorted(REPORTS_DIR.glob("*_responses.json"))
    if not response_paths:
        print("No response files found.")
        return 0

    for response_path in response_paths:
        scores = score_responses(PACK_ROOT, load_json(response_path))
        score_path = score_path_for(response_path)
        summary_path = summary_path_for(response_path)
        write_json(score_path, scores)
        write_scores_markdown(summary_path, scores)
        print(f"Scored {response_path.relative_to(ROOT)} -> {score_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
