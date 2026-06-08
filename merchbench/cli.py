from __future__ import annotations

import argparse
from pathlib import Path

from merchbench.eval_packs import run_baselines, score_responses, write_scores_markdown
from merchbench.io import load_json, write_json
from merchbench.openrouter_eval import DEFAULT_MODELS as DEFAULT_OPENROUTER_EVAL_MODELS
from merchbench.openrouter_eval import run_openrouter_eval
from merchbench.provider_eval import PROVIDER_SPECS, run_provider_eval


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SEGMENTS = ROOT / "routing" / "retail_decision_segments.json"
DEFAULT_POLICIES = ROOT / "routing" / "default_policies.json"
DEFAULT_MODEL_PROFILES = ROOT / "routing" / "model_profiles.json"
DEFAULT_JSON_OUTPUT = ROOT / "reports" / "routing" / "recommendations.json"
DEFAULT_MD_OUTPUT = ROOT / "reports" / "routing" / "segment_recommendations.md"
DEFAULT_EVAL_PACK_ROOT = ROOT / "eval_packs"
DEFAULT_EVAL_RESPONSES = ROOT / "reports" / "eval_packs" / "baseline_responses.json"
DEFAULT_EVAL_SCORES = ROOT / "reports" / "eval_packs" / "baseline_scores.json"
DEFAULT_EVAL_SUMMARY = ROOT / "reports" / "eval_packs" / "baseline_summary.md"
DEFAULT_EVAL_ROBUSTNESS = ROOT / "reports" / "eval_packs" / "scorer_robustness.md"
DEFAULT_OPENROUTER_EVAL_RESPONSES = ROOT / "reports" / "eval_packs" / "openrouter_responses.json"
DEFAULT_OPENROUTER_EVAL_SCORES = ROOT / "reports" / "eval_packs" / "openrouter_scores.json"
DEFAULT_OPENROUTER_EVAL_SUMMARY = ROOT / "reports" / "eval_packs" / "openrouter_summary.md"
DEFAULT_OPENROUTER_EVAL_MANIFEST = ROOT / "reports" / "eval_packs" / "openrouter_manifest.json"
DEFAULT_ENV_PATH = ROOT / ".env.local"


def provider_output_path(provider: str, suffix: str) -> Path:
    return ROOT / "reports" / "eval_packs" / f"provider_{provider}_{suffix}"


def cmd_eval_pack_baselines(args: argparse.Namespace) -> int:
    run_baselines(
        args.pack_root,
        args.output_responses,
        args.output_scores,
        args.output_summary,
        args.output_robustness,
    )
    print(f"Wrote {args.output_responses}")
    print(f"Wrote {args.output_scores}")
    print(f"Wrote {args.output_summary}")
    if args.output_robustness:
        print(f"Wrote {args.output_robustness}")
    return 0


def cmd_eval_pack_score(args: argparse.Namespace) -> int:
    responses = load_json(args.responses)
    scores = score_responses(args.pack_root, responses)
    write_json(args.output_scores, scores)
    if args.output_summary:
        write_scores_markdown(args.output_summary, scores)
        print(f"Wrote {args.output_summary}")
    print(f"Wrote {args.output_scores}")
    return 0


def cmd_eval_pack_openrouter(args: argparse.Namespace) -> int:
    run_openrouter_eval(
        pack_root=args.pack_root,
        output_responses=args.output_responses,
        output_scores=args.output_scores,
        output_summary=args.output_summary,
        output_manifest=args.output_manifest,
        env_path=args.env,
        models=args.models,
        segments=args.segments,
        pack_ids=args.pack_ids,
        max_items=args.max_items,
        items_per_pack=args.items_per_pack,
        dry_run=args.dry_run,
        resume=args.resume,
        sleep=args.sleep,
        timeout=args.timeout,
        max_retries=args.max_retries,
        retry_backoff=args.retry_backoff,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
    )
    if args.dry_run:
        return 0
    print(f"Wrote {args.output_responses}")
    if args.output_scores:
        print(f"Wrote {args.output_scores}")
    if args.output_summary:
        print(f"Wrote {args.output_summary}")
    if args.output_manifest:
        print(f"Wrote {args.output_manifest}")
    return 0


def cmd_eval_pack_provider(args: argparse.Namespace) -> int:
    output_responses = args.output_responses or provider_output_path(args.provider, "responses.json")
    output_scores = args.output_scores or provider_output_path(args.provider, "scores.json")
    output_summary = args.output_summary or provider_output_path(args.provider, "summary.md")
    output_manifest = args.output_manifest or provider_output_path(args.provider, "manifest.json")
    run_provider_eval(
        provider=args.provider,
        pack_root=args.pack_root,
        output_responses=output_responses,
        output_scores=output_scores,
        output_summary=output_summary,
        output_manifest=output_manifest,
        env_path=args.env,
        models=args.models,
        segments=args.segments,
        pack_ids=args.pack_ids,
        max_items=args.max_items,
        items_per_pack=args.items_per_pack,
        dry_run=args.dry_run,
        resume=args.resume,
        sleep=args.sleep,
        timeout=args.timeout,
        max_retries=args.max_retries,
        retry_backoff=args.retry_backoff,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        unload_after_item=args.unload_after_item,
        unload_after_model=args.unload_after_model,
    )
    if args.dry_run:
        return 0
    print(f"Wrote {output_responses}")
    if output_scores:
        print(f"Wrote {output_scores}")
    if output_summary:
        print(f"Wrote {output_summary}")
    if output_manifest:
        print(f"Wrote {output_manifest}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Retail MerchBench scoring and provider-runner tools.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    baseline_parser = subparsers.add_parser("eval-pack-baselines", help="Run deterministic baselines over segment eval packs.")
    baseline_parser.add_argument("--pack-root", type=Path, default=DEFAULT_EVAL_PACK_ROOT)
    baseline_parser.add_argument("--output-responses", type=Path, default=DEFAULT_EVAL_RESPONSES)
    baseline_parser.add_argument("--output-scores", type=Path, default=DEFAULT_EVAL_SCORES)
    baseline_parser.add_argument("--output-summary", type=Path, default=DEFAULT_EVAL_SUMMARY)
    baseline_parser.add_argument("--output-robustness", type=Path, default=DEFAULT_EVAL_ROBUSTNESS)
    baseline_parser.set_defaults(func=cmd_eval_pack_baselines)

    score_parser = subparsers.add_parser("eval-pack-score", help="Score a segment eval-pack response file.")
    score_parser.add_argument("--pack-root", type=Path, default=DEFAULT_EVAL_PACK_ROOT)
    score_parser.add_argument("--responses", type=Path, required=True)
    score_parser.add_argument("--output-scores", type=Path, required=True)
    score_parser.add_argument("--output-summary", type=Path)
    score_parser.set_defaults(func=cmd_eval_pack_score)

    openrouter_parser = subparsers.add_parser("eval-pack-openrouter", help="Run segment eval packs through OpenRouter.")
    openrouter_parser.add_argument("--pack-root", type=Path, default=DEFAULT_EVAL_PACK_ROOT)
    openrouter_parser.add_argument("--output-responses", type=Path, default=DEFAULT_OPENROUTER_EVAL_RESPONSES)
    openrouter_parser.add_argument("--output-scores", type=Path, default=DEFAULT_OPENROUTER_EVAL_SCORES)
    openrouter_parser.add_argument("--output-summary", type=Path, default=DEFAULT_OPENROUTER_EVAL_SUMMARY)
    openrouter_parser.add_argument("--output-manifest", type=Path, default=DEFAULT_OPENROUTER_EVAL_MANIFEST)
    openrouter_parser.add_argument("--env", type=Path, default=DEFAULT_ENV_PATH)
    openrouter_parser.add_argument("--models", nargs="+", default=DEFAULT_OPENROUTER_EVAL_MODELS)
    openrouter_parser.add_argument("--segments", nargs="*")
    openrouter_parser.add_argument("--pack-ids", nargs="*")
    openrouter_parser.add_argument("--max-items", type=int)
    openrouter_parser.add_argument("--items-per-pack", type=int)
    openrouter_parser.add_argument("--dry-run", action="store_true")
    openrouter_parser.add_argument("--resume", action="store_true")
    openrouter_parser.add_argument("--sleep", type=float, default=0.5)
    openrouter_parser.add_argument("--timeout", type=int, default=45)
    openrouter_parser.add_argument("--max-retries", type=int, default=3)
    openrouter_parser.add_argument("--retry-backoff", type=float, default=2.0)
    openrouter_parser.add_argument("--temperature", type=float, default=0.0)
    openrouter_parser.add_argument("--max-tokens", type=int, default=900)
    openrouter_parser.set_defaults(func=cmd_eval_pack_openrouter)

    provider_parser = subparsers.add_parser("eval-pack-provider", help="Run segment eval packs through a configured model provider.")
    provider_parser.add_argument("--provider", choices=sorted(PROVIDER_SPECS), required=True)
    provider_parser.add_argument("--pack-root", type=Path, default=DEFAULT_EVAL_PACK_ROOT)
    provider_parser.add_argument("--output-responses", type=Path)
    provider_parser.add_argument("--output-scores", type=Path)
    provider_parser.add_argument("--output-summary", type=Path)
    provider_parser.add_argument("--output-manifest", type=Path)
    provider_parser.add_argument("--env", type=Path, default=DEFAULT_ENV_PATH)
    provider_parser.add_argument("--models", nargs="+")
    provider_parser.add_argument("--segments", nargs="*")
    provider_parser.add_argument("--pack-ids", nargs="*")
    provider_parser.add_argument("--max-items", type=int)
    provider_parser.add_argument("--items-per-pack", type=int)
    provider_parser.add_argument("--dry-run", action="store_true")
    provider_parser.add_argument("--resume", action="store_true")
    provider_parser.add_argument("--sleep", type=float, default=0.5)
    provider_parser.add_argument("--timeout", type=int, default=45)
    provider_parser.add_argument("--max-retries", type=int, default=3)
    provider_parser.add_argument("--retry-backoff", type=float, default=2.0)
    provider_parser.add_argument("--temperature", type=float, default=0.0)
    provider_parser.add_argument("--max-tokens", type=int, default=900)
    provider_parser.add_argument("--unload-after-item", action="store_true", help="Unload a local provider model after every eval item.")
    provider_parser.add_argument("--unload-after-model", action="store_true", help="Unload a local provider model after each model run.")
    provider_parser.set_defaults(func=cmd_eval_pack_provider)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
