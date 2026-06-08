"""MerchBench routing and reporting helpers."""

from merchbench.io import load_json, summarize_scores
from merchbench.routing import build_frontier, recommend_segments
from merchbench.eval_packs import score_responses

__all__ = [
    "build_frontier",
    "load_json",
    "recommend_segments",
    "score_responses",
    "summarize_scores",
]
