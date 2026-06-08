#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import math
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = ROOT / "reports" / "eval_packs"
ATLAS_DIR = ROOT / "reports" / "atlas"
ATLAS_DATA = ATLAS_DIR / "atlas_data.json"
OUTPUT_HTML = ATLAS_DIR / "index.html"
OUTPUT_ANALYSIS = ATLAS_DIR / "analysis.md"
OUTPUT_FRONTIER_SVG = ATLAS_DIR / "model_frontier.svg"
OUTPUT_HEATMAP_SVG = ATLAS_DIR / "segment_heatmap.svg"

SEGMENT_ORDER = [
    "low_risk_summarization",
    "structured_extraction",
    "constraint_checking",
    "routine_planning_recommendation",
    "pricing_promotion",
    "ambiguous_planning_judgment",
    "portfolio_tradeoff",
    "operational_triage",
]

SEGMENT_LABELS = {
    "low_risk_summarization": "Summarization",
    "structured_extraction": "Extraction",
    "constraint_checking": "Constraint checks",
    "routine_planning_recommendation": "Routine planning",
    "pricing_promotion": "Pricing & promo",
    "ambiguous_planning_judgment": "Ambiguous judgment",
    "portfolio_tradeoff": "Portfolio tradeoff",
    "operational_triage": "Ops triage",
}

MIN_MODEL_PANEL_ITEMS = 100

MODEL_RATES_PER_MILLION = {
    "openai/gpt-4.1-nano": {"input": 0.10, "output": 0.40},
    "openai/gpt-5-nano": {"input": 0.05, "output": 0.40},
    "openai/gpt-5-mini": {"input": 0.25, "output": 2.00},
    "openai/gpt-5.4-mini": {"input": 0.75, "output": 4.50},
    "openai/gpt-5.4": {"input": 2.50, "output": 15.00},
    "openai/gpt-5.5": {"input": 5.00, "output": 30.00},
}

MODEL_META = {
    "openai/gpt-5.5": {
        "display_name": "GPT-5.5",
        "cluster": "Premium frontier",
        "tier": "frontier_model",
        "cost_basis": "metered_openai_api",
        "notes": "Overall quality leader in the 100-item run; best reserved for high-downside exceptions.",
    },
    "openai/gpt-5.4": {
        "display_name": "GPT-5.4",
        "cluster": "Frontier proprietary",
        "tier": "frontier_model",
        "cost_basis": "metered_openai_api",
        "notes": "Near-top overall quality and the strongest ambiguous-judgment/constraint-checking profile.",
    },
    "openai/gpt-5.4-mini": {
        "display_name": "GPT-5.4 Mini",
        "cluster": "Efficient frontier",
        "tier": "frontier_model",
        "cost_basis": "metered_openai_api",
        "notes": "Near-frontier quality at materially lower observed artifact cost than the premium models.",
    },
    "openai/gpt-5-mini": {
        "display_name": "GPT-5 Mini",
        "cluster": "Efficient mid-tier",
        "tier": "mid_model",
        "cost_basis": "metered_openai_api",
        "notes": "Best cheap paid default for summarization, extraction, and portfolio triage in this run.",
    },
    "openai/gpt-5-nano": {
        "display_name": "GPT-5 Nano",
        "cluster": "Small paid model",
        "tier": "small_model",
        "cost_basis": "metered_openai_api",
        "notes": "Very cheap paid baseline with useful quality for bounded, low-risk workflows.",
    },
    "openai/gpt-4.1-nano": {
        "display_name": "GPT-4.1 Nano",
        "cluster": "Small paid model",
        "tier": "small_model",
        "cost_basis": "metered_openai_api",
        "notes": "Small direct-OpenAI baseline for low-cost comparisons.",
    },
    "cerebras/zai-glm-4.7": {
        "display_name": "Z.ai GLM 4.7",
        "cluster": "Free hosted frontier",
        "tier": "frontier_model",
        "cost_basis": "free_tier_observed",
        "notes": "Strongest free hosted result; competitive with paid small models on several segments.",
    },
    "cerebras/gpt-oss-120b": {
        "display_name": "GPT-OSS 120B",
        "cluster": "Free hosted frontier",
        "tier": "frontier_model",
        "cost_basis": "free_tier_observed",
        "notes": "Strong open model and a good free-capacity comparator.",
    },
    "groq/meta-llama/llama-4-scout-17b-16e-instruct": {
        "display_name": "Llama 4 Scout 17B",
        "cluster": "Free hosted open",
        "tier": "mid_model",
        "cost_basis": "free_tier_observed",
        "notes": "Efficient hosted baseline, but below the paid OpenAI frontier.",
    },
    "groq/llama-3.3-70b-versatile": {
        "display_name": "Llama 3.3 70B",
        "cluster": "Free hosted open",
        "tier": "frontier_model",
        "cost_basis": "free_tier_observed",
        "notes": "Large open hosted comparator with solid but not leading quality.",
    },
    "groq/qwen/qwen3-32b": {
        "display_name": "Qwen3 32B",
        "cluster": "Free hosted open",
        "tier": "mid_model",
        "cost_basis": "free_tier_observed",
        "notes": "Best Groq-hosted model in the full-suite run; required higher caps to suppress thinking traces.",
    },
    "ollama/gemma4:e2b": {
        "display_name": "Gemma local",
        "cluster": "Local model",
        "tier": "local_model",
        "cost_basis": "local_hardware",
        "notes": "Best local score, but many rows returned empty or parse-invalid content; use only for tightly bounded local experiments.",
    },
    "ollama/llama3.2:3b": {
        "display_name": "Llama 3.2 local",
        "cluster": "Local small model",
        "tier": "small_model",
        "cost_basis": "local_hardware",
        "notes": "Reliable output producer, but materially weaker judgment.",
    },
    "ollama/lfm2.5-thinking:1.2b": {
        "display_name": "LFM local 1.2B",
        "cluster": "Local small model",
        "tier": "small_model",
        "cost_basis": "local_hardware",
        "notes": "Tiny local comparator with frequent empty or parse-invalid responses; not attractive for this eval shape.",
    },
}

SEGMENT_RECOMMENDATIONS = {
    "low_risk_summarization": {
        "default_route": "GPT-5 Mini for paid production; GPT-OSS 120B when free hosted quota is available.",
        "why": "GPT-5 Mini leads the full-suite readout at 8.0696/10 and remains inexpensive in the paid ladder.",
        "controls": "Source citation, numeric preservation, no-recommendation boundary check.",
        "human_review": "No, unless the summary becomes a decision recommendation or contains conflicting financial figures.",
    },
    "structured_extraction": {
        "default_route": "Rules/schema first, GPT-5 Mini fallback for messy source text.",
        "why": "GPT-5 Mini leads at 8.5700/10; structured extraction still needs deterministic validation.",
        "controls": "Schema validation, required-field checks, range checks, conflict detection.",
        "human_review": "Only for material missing values or field conflicts.",
    },
    "constraint_checking": {
        "default_route": "Deterministic checks first; GPT-5.4 for high-severity explanation, GPT-5 Mini for cheaper routine triage.",
        "why": "GPT-5.4 leads at 8.2879/10, while GPT-5 Mini remains the lower-cost paid option at 7.7792/10.",
        "controls": "OTB, MOQ, pack multiple, margin floor, capacity, and compliance gates.",
        "human_review": "Required when a violated constraint is overridden.",
    },
    "routine_planning_recommendation": {
        "default_route": "GPT-5.4 Mini with deterministic guardrails; escalate low-confidence recommendations.",
        "why": "GPT-5.5 and GPT-5.4 tie for the lead at 6.9939/10, which is below the proxy autonomy floor; GPT-5.4 Mini is the cheaper near-frontier option.",
        "controls": "Inventory cover, margin, pack, timing, and stockout-censoring checks.",
        "human_review": "Only for high inventory value, low confidence, or irreversible actions.",
    },
    "pricing_promotion": {
        "default_route": "GPT-5.5 or GPT-5.4 with margin and vendor-funding controls; human review for material decisions.",
        "why": "GPT-5.5 leads pricing/promotion at 6.7780/10, but no model clears the 7.0 proxy autonomy floor.",
        "controls": "Margin floor, vendor funding, inventory cover, pull-forward, and competitor response checks.",
        "human_review": "Yes for material price moves, below-floor margin, or high competitive-response uncertainty.",
    },
    "ambiguous_planning_judgment": {
        "default_route": "GPT-5.4 for ambiguous judgment; GPT-5.4 Mini when the decision is reversible and well-guardrailed.",
        "why": "GPT-5.4 leads at 8.5311/10; GPT-5.5 is second at 7.7152/10 and Z.ai GLM 4.7 is the strongest free hosted comparator at 7.4038/10.",
        "controls": "Evidence contamination, OTB, lead time, margin, opportunity cost, and confidence gates.",
        "human_review": "Recommended for vendor commitments, high markdown risk, or executive-pressure cases.",
    },
    "portfolio_tradeoff": {
        "default_route": "GPT-5 Mini or GPT-5.4 Mini plus human review.",
        "why": "GPT-5 Mini narrowly leads at 8.0774/10, with GPT-5.4 Mini close at 8.0008/10; cross-category OTB decisions remain high-downside.",
        "controls": "Portfolio OTB, opportunity cost, receiving capacity, leadership override, and customer-trust gates.",
        "human_review": "Yes. This should not be fully autonomous in the current evidence base.",
    },
    "operational_triage": {
        "default_route": "GPT-5.4 Mini for normal exceptions; GPT-5.5 or human review for safety/customer-trust risk.",
        "why": "GPT-5.5 leads at 7.5235/10; GPT-5.4 remains close at 7.2776/10, and GPT-5.4 Mini is the cheaper near-frontier option at 6.8261/10.",
        "controls": "Safety, labor capacity, service-level, compliance, and owner-routing checks.",
        "human_review": "Yes when safety, legal, public commitment, or customer-trust exposure appears.",
    },
}


def load_json(path: Path) -> Any:
    with path.open() as handle:
        return json.load(handle)


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def model_slug(model_id: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", model_id.lower()).strip("-")


def score_file_stem(path: Path) -> str:
    return path.name.removesuffix("_scores.json")


def matching_response_path(score_path: Path) -> Path:
    return score_path.with_name(score_path.name.replace("_scores.json", "_responses.json"))


def usage_for_model(response_path: Path, model_id: str) -> dict[str, int]:
    usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0, "reasoning_tokens": 0}
    if not response_path.exists():
        return usage
    data = load_json(response_path)
    model = data.get("models", {}).get(model_id, {})

    def walk(value: Any) -> None:
        if isinstance(value, dict):
            raw_usage = value.get("usage")
            if isinstance(raw_usage, dict):
                usage["prompt_tokens"] += int(raw_usage.get("prompt_tokens") or 0)
                usage["completion_tokens"] += int(raw_usage.get("completion_tokens") or 0)
                usage["total_tokens"] += int(raw_usage.get("total_tokens") or 0)
                details = raw_usage.get("completion_tokens_details") or {}
                usage["reasoning_tokens"] += int(details.get("reasoning_tokens") or 0)
            for child in value.values():
                walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)

    walk(model)
    return usage


def estimated_cost(model_id: str, usage: dict[str, int]) -> float:
    rates = MODEL_RATES_PER_MILLION.get(model_id)
    if not rates:
        return 0.0
    return round(
        (usage["prompt_tokens"] * rates["input"] / 1_000_000)
        + (usage["completion_tokens"] * rates["output"] / 1_000_000),
        6,
    )


def provider_for(model_id: str) -> str:
    return model_id.split("/", 1)[0]


def fallback_meta(model_id: str) -> dict[str, str]:
    return {
        "display_name": model_id,
        "cluster": "Other measured model",
        "tier": "model",
        "cost_basis": "unknown",
        "notes": "Measured in local artifacts; metadata needs curation.",
    }


def normalized_log_cost(records: list[dict[str, Any]]) -> None:
    positive_costs = [float(row["estimated_cost_usd"]) for row in records if float(row["estimated_cost_usd"]) > 0]
    if not positive_costs:
        for row in records:
            row["cost_index"] = 0.0
        return
    max_cost = max(positive_costs)
    floor = 0.001
    denom = math.log10(max_cost + floor) - math.log10(floor)
    for row in records:
        cost = float(row["estimated_cost_usd"])
        if cost <= 0:
            row["cost_index"] = 0.2
        else:
            row["cost_index"] = round(10 * (math.log10(cost + floor) - math.log10(floor)) / denom, 2)


def normalized_response_burden(records: list[dict[str, Any]]) -> None:
    max_completion = max((int(row["completion_tokens"]) for row in records), default=1)
    for row in records:
        row["experience_burden_index"] = round(10 * int(row["completion_tokens"]) / max_completion, 2) if max_completion else 0


def mark_pareto(records: list[dict[str, Any]]) -> None:
    for row in records:
        dominated = False
        for other in records:
            if other is row:
                continue
            other_cost = float(other["estimated_cost_usd"])
            row_cost = float(row["estimated_cost_usd"])
            other_score = float(other["overall_average"])
            row_score = float(row["overall_average"])
            if other_cost <= row_cost and other_score >= row_score and (other_cost < row_cost or other_score > row_score):
                if other["cost_basis"] == row["cost_basis"] or other_cost > 0:
                    dominated = True
                    break
        row["pareto_frontier"] = not dominated


def collect_model_records() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    records: list[dict[str, Any]] = []
    sanity_baselines: list[dict[str, Any]] = []
    for score_path in sorted(REPORTS_DIR.glob("*_scores.json")):
        score_doc = load_json(score_path)
        response_path = matching_response_path(score_path)
        for model_id, result in score_doc.get("models", {}).items():
            if int(result.get("attempted_items") or 0) < MIN_MODEL_PANEL_ITEMS:
                continue
            if model_id.startswith("baseline/"):
                sanity_baselines.append(
                    {
                        "model_id": model_id,
                        "overall_average": result.get("overall_average", 0),
                        "attempted_items": int(result.get("attempted_items") or 0),
                        "available_items": int(result.get("available_items") or result.get("attempted_items") or 0),
                        "packs_passing": sum(1 for pack in result.get("packs", {}).values() if pack.get("passes_pack_floor")),
                        "source_file": str(score_path.relative_to(ROOT)),
                    }
                )
                continue
            if int(result.get("failed_items") or 0) > 0:
                continue
            if int(result.get("total_items") or 0) < int(result.get("available_items") or 0):
                continue
            meta = MODEL_META.get(model_id, fallback_meta(model_id))
            usage = usage_for_model(response_path, model_id)
            segment_scores = {
                pack["task_segment"]: round(float(pack["average_score"]), 4)
                for pack in result.get("packs", {}).values()
            }
            records.append(
                {
                    "model_id": model_id,
                    "display_name": meta["display_name"],
                    "provider": provider_for(model_id),
                    "cluster": meta["cluster"],
                    "tier": meta["tier"],
                    "cost_basis": meta["cost_basis"],
                    "notes": meta["notes"],
                    "overall_average": round(float(result.get("overall_average") or 0), 4),
                    "attempted_items": int(result.get("attempted_items") or 0),
                    "available_items": int(result.get("available_items") or result.get("attempted_items") or 0),
                    "failed_items": int(result.get("failed_items") or 0),
                    "packs_passing": sum(1 for pack in result.get("packs", {}).values() if pack.get("passes_pack_floor")),
                    "prompt_tokens": usage["prompt_tokens"],
                    "completion_tokens": usage["completion_tokens"],
                    "total_tokens": usage["total_tokens"],
                    "reasoning_tokens": usage["reasoning_tokens"],
                    "estimated_cost_usd": estimated_cost(model_id, usage),
                    "source_score_file": str(score_path.relative_to(ROOT)),
                    "source_response_file": str(response_path.relative_to(ROOT)) if response_path.exists() else None,
                    "segment_scores": segment_scores,
                }
            )
    normalized_log_cost(records)
    normalized_response_burden(records)
    mark_pareto(records)
    records.sort(key=lambda row: (-float(row["overall_average"]), float(row["estimated_cost_usd"]), row["display_name"]))
    return records, sanity_baselines


def segment_summaries(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    summaries = []
    by_id = {row["model_id"]: row for row in records}
    for segment_id in SEGMENT_ORDER:
        ranked = sorted(
            [
                {
                    "model_id": row["model_id"],
                    "display_name": row["display_name"],
                    "score": row["segment_scores"].get(segment_id, 0),
                    "estimated_cost_usd": row["estimated_cost_usd"],
                    "cost_basis": row["cost_basis"],
                }
                for row in records
                if segment_id in row["segment_scores"]
            ],
            key=lambda row: (-float(row["score"]), float(row["estimated_cost_usd"]), row["display_name"]),
        )
        rec = SEGMENT_RECOMMENDATIONS[segment_id]
        economic_model_id = None
        if "GPT-5.4 Mini" in rec["default_route"]:
            economic_model_id = "openai/gpt-5.4-mini"
        elif "GPT-5 Mini" in rec["default_route"]:
            economic_model_id = "openai/gpt-5-mini"
        elif "GPT-5.4 " in rec["default_route"]:
            economic_model_id = "openai/gpt-5.4"
        if economic_model_id and economic_model_id in by_id:
            economic_pick = {
                "model_id": economic_model_id,
                "display_name": by_id[economic_model_id]["display_name"],
                "score": by_id[economic_model_id]["segment_scores"].get(segment_id, 0),
                "estimated_cost_usd": by_id[economic_model_id]["estimated_cost_usd"],
            }
        else:
            economic_pick = ranked[0] if ranked else {}

        summaries.append(
            {
                "segment_id": segment_id,
                "label": SEGMENT_LABELS[segment_id],
                "quality_leader": ranked[0] if ranked else {},
                "economic_pick": economic_pick,
                "top_models": ranked[:5],
                **rec,
            }
        )
    return summaries


def build_data() -> dict[str, Any]:
    records, sanity_baselines = collect_model_records()
    paid = [row for row in records if row["cost_basis"] == "metered_openai_api"]
    total_openai_cost = round(sum(float(row["estimated_cost_usd"]) for row in paid if row["model_id"].startswith("openai/gpt-5")), 4)
    benchmark_items = max([int(row.get("available_items") or 0) for row in records + sanity_baselines] or [0])
    model_panel_items = max([int(row.get("attempted_items") or 0) for row in records] or [0])
    return {
        "schema_version": "1.0",
        "generated_at_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "title": "MerchBench Retail AI Model Routing Atlas",
        "subtitle": "A real-results guide for choosing economically sufficient model tiers across retail planning workflows.",
        "status": (
            f"Evidence package: {benchmark_items} segment eval items, stored model panel covers "
            f"{model_panel_items}/{benchmark_items} items, automated scorer with human-calibration caveats."
        ),
        "benchmark_items": benchmark_items,
        "model_panel_items": model_panel_items,
        "data_caveat": (
            f"The corpus contains {benchmark_items} segment eval-pack items. Current provider model scores are "
            f"from full-coverage stored runs for the curated panel. OpenRouter free-tier probes are partial and excluded "
            "from the main frontier; xAI was unavailable because the account returned a no-credits/no-license error. "
            "Cost is estimated from recorded token usage where pricing is encoded. "
            "Latency is shown as response-token burden, not production p95 latency. "
            "Deterministic baseline scores are used as scorer sanity checks, not deployable model recommendations. "
            "Scores remain routing diagnostics until human-rater calibration is complete."
        ),
        "key_findings": [
            f"Retail MerchBench contains {benchmark_items} segment eval items, and the curated provider panel has {model_panel_items}/{benchmark_items} scored coverage for 14 real models plus deterministic baselines.",
            "GPT-5.5 is the overall leader at 7.4614/10, followed by GPT-5.4 at 7.3907/10 and GPT-5.4 Mini at 7.3693/10.",
            "GPT-5.4 Mini is the economic frontier result: it lands within 0.0921 points of GPT-5.5 at about 13 percent of the observed artifact cost.",
            "GPT-5 Mini is the best cheap paid specialist for summarization, structured extraction, and portfolio tradeoff.",
            "Z.ai GLM 4.7 is the strongest free hosted result at 6.8471/10, clearly ahead of GPT-OSS 120B, Groq-hosted open models, and local Ollama models in this run.",
            "The anti-echo scorer rejects shallow deterministic baselines: source echo scores 3.3530 and keyword guardrail stuffing scores 4.3280 on the 100-item corpus.",
            "Pricing/promotion and routine planning remain below the 7.0 proxy autonomy floor even for the strongest models; these workflows need deterministic controls and human review.",
            "Local Ollama models are useful for low-cost experimentation, but none clears deterministic keyword-guardrail baseline quality on this full-suite judgment benchmark.",
            "OpenRouter free-tier probes stopped at the daily free-model cap and xAI was unavailable; they are documented as capacity findings, not ranked model results.",
            "The scorer includes adversarial anti-echo baselines, but public benchmark claims still need human-rater calibration and repeated-run variance.",
        ],
        "openai_ladder_cost_usd": total_openai_cost,
        "model_records": records,
        "sanity_baselines": sanity_baselines,
        "segment_summaries": segment_summaries(records),
    }


def color_for_score(score: float) -> str:
    if score >= 8.25:
        return "#277c78"
    if score >= 7.5:
        return "#88a88f"
    if score >= 6.5:
        return "#c8912f"
    if score >= 5:
        return "#b85f42"
    return "#6d5375"


def render_frontier_svg(records: list[dict[str, Any]]) -> str:
    width, height = 980, 560
    plot_x, plot_y, plot_w, plot_h = 84, 56, 800, 410
    max_cost_index = 10
    min_score, max_score = 3.5, 8.2

    def px(row: dict[str, Any]) -> float:
        return plot_x + (float(row["cost_index"]) / max_cost_index) * plot_w

    def py(row: dict[str, Any]) -> float:
        score = float(row["overall_average"])
        return plot_y + (max_score - score) / (max_score - min_score) * plot_h

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        "<title>MerchBench model frontier</title>",
        "<desc>Scatter plot of model quality by estimated cost burden.</desc>",
        '<rect width="980" height="560" fill="#f7f4ee"/>',
        f'<rect x="{plot_x}" y="{plot_y}" width="{plot_w}" height="{plot_h}" rx="8" fill="#fffdf8" stroke="#d8ddd5"/>',
    ]
    for step in range(0, 11, 2):
        x = plot_x + (step / 10) * plot_w
        parts.append(f'<line x1="{x:.1f}" y1="{plot_y}" x2="{x:.1f}" y2="{plot_y + plot_h}" stroke="#e5e1d8"/>')
        parts.append(f'<text x="{x:.1f}" y="{plot_y + plot_h + 28}" text-anchor="middle" font-size="12" fill="#5e675f">{step}</text>')
    for score in [4, 5, 6, 7, 8]:
        y = plot_y + (max_score - score) / (max_score - min_score) * plot_h
        parts.append(f'<line x1="{plot_x}" y1="{y:.1f}" x2="{plot_x + plot_w}" y2="{y:.1f}" stroke="#e5e1d8"/>')
        parts.append(f'<text x="{plot_x - 16}" y="{y + 4:.1f}" text-anchor="end" font-size="12" fill="#5e675f">{score}</text>')
    parts.append(f'<text x="{plot_x + plot_w / 2}" y="530" text-anchor="middle" font-size="14" fill="#17211b">Estimated cost burden index</text>')
    parts.append(f'<text x="24" y="{plot_y + plot_h / 2}" transform="rotate(-90 24 {plot_y + plot_h / 2})" text-anchor="middle" font-size="14" fill="#17211b">Retail judgment quality score</text>')

    for row in sorted(records, key=lambda item: float(item["overall_average"])):
        if row["failed_items"] != 0:
            continue
        x, y = px(row), py(row)
        radius = 7 + float(row["experience_burden_index"]) * 0.9
        stroke = "#17211b" if row["pareto_frontier"] else "#fffdf8"
        opacity = "1" if row["pareto_frontier"] or row["provider"] == "openai" else ".72"
        parts.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{radius:.1f}" fill="{color_for_score(float(row["overall_average"]))}" '
            f'stroke="{stroke}" stroke-width="2" opacity="{opacity}"/>'
        )
        label_dx = 12
        label_anchor = "start"
        if x > plot_x + plot_w - 160:
            label_dx = -12
            label_anchor = "end"
        label = esc(row["display_name"])
        parts.append(f'<text x="{x + label_dx:.1f}" y="{y + 4:.1f}" text-anchor="{label_anchor}" font-size="12" fill="#17211b">{label}</text>')
    parts.append('<text x="84" y="32" font-size="20" font-weight="700" fill="#17211b">Quality-cost frontier</text>')
    parts.append('<text x="84" y="492" font-size="12" fill="#5e675f">Outlined marks are on the measured Pareto frontier. Bubble size reflects response-token burden, not p95 production latency.</text>')
    parts.append("</svg>")
    return "\n".join(parts)


def render_heatmap_svg(data: dict[str, Any]) -> str:
    records = [row for row in data["model_records"] if row["model_id"].startswith("openai/gpt-5")]
    records = sorted(records, key=lambda row: -float(row["overall_average"]))
    cell_w, cell_h = 98, 46
    left, top = 172, 86
    width = left + cell_w * len(SEGMENT_ORDER) + 34
    height = top + cell_h * len(records) + 42
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        "<title>OpenAI segment heatmap</title>",
        "<desc>Heatmap of OpenAI GPT-5 model scores by retail decision segment.</desc>",
        f'<rect width="{width}" height="{height}" fill="#f7f4ee"/>',
        '<text x="24" y="34" font-size="20" font-weight="700" fill="#17211b">OpenAI ladder by retail segment</text>',
    ]
    for idx, segment in enumerate(SEGMENT_ORDER):
        x = left + idx * cell_w + cell_w / 2
        label = SEGMENT_LABELS[segment]
        parts.append(f'<text x="{x:.1f}" y="72" transform="rotate(-35 {x:.1f} 72)" text-anchor="end" font-size="11" fill="#5e675f">{esc(label)}</text>')
    for r_idx, row in enumerate(records):
        y = top + r_idx * cell_h
        parts.append(f'<text x="24" y="{y + 29}" font-size="13" font-weight="700" fill="#17211b">{esc(row["display_name"])}</text>')
        for c_idx, segment in enumerate(SEGMENT_ORDER):
            x = left + c_idx * cell_w
            score = float(row["segment_scores"].get(segment, 0))
            fill = color_for_score(score)
            parts.append(f'<rect x="{x}" y="{y}" width="{cell_w - 4}" height="{cell_h - 4}" rx="4" fill="{fill}"/>')
            parts.append(f'<text x="{x + (cell_w - 4) / 2:.1f}" y="{y + 27}" text-anchor="middle" font-size="12" font-weight="700" fill="#fffdf8">{score:.1f}</text>')
    parts.append("</svg>")
    return "\n".join(parts)


def render_rank_table(records: list[dict[str, Any]]) -> str:
    rows = []
    for rank, row in enumerate(records[:12], 1):
        frontier = "Yes" if row["pareto_frontier"] else "No"
        cost = "$0" if float(row["estimated_cost_usd"]) == 0 else f"${float(row['estimated_cost_usd']):.4f}"
        rows.append(
            f"""
            <tr>
              <td>{rank}</td>
              <td><strong>{esc(row['display_name'])}</strong><br><span>{esc(row['model_id'])}</span></td>
              <td>{row['overall_average']}/10</td>
              <td>{cost}<br><span>{esc(row['cost_basis'])}</span></td>
              <td>{row['packs_passing']}/8</td>
              <td>{frontier}</td>
              <td>{esc(row['notes'])}</td>
            </tr>
            """
        )
    return "\n".join(rows)


def render_segment_cards(data: dict[str, Any]) -> str:
    cards = []
    for segment in data["segment_summaries"]:
        leader = segment["quality_leader"]
        economic = segment["economic_pick"]
        cards.append(
            f"""
            <article class="segment-card">
              <div class="segment-kicker">{esc(segment['label'])}</div>
              <h3>{esc(segment['default_route'])}</h3>
              <p>{esc(segment['why'])}</p>
              <dl>
                <dt>Quality leader</dt><dd>{esc(leader.get('display_name', 'n/a'))} · {leader.get('score', 0)}/10</dd>
                <dt>Economic pick</dt><dd>{esc(economic.get('display_name', 'n/a'))} · {economic.get('score', 0)}/10</dd>
                <dt>Controls</dt><dd>{esc(segment['controls'])}</dd>
                <dt>Human review</dt><dd>{esc(segment['human_review'])}</dd>
              </dl>
            </article>
            """
        )
    return "\n".join(cards)


def render_findings(data: dict[str, Any]) -> str:
    return "\n".join(f"<li>{esc(finding)}</li>" for finding in data["key_findings"])


def render_html(data: dict[str, Any]) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(data['title'])}</title>
  <link rel="icon" href="data:,">
  <style>
    :root {{
      --ink: #17211b;
      --muted: #5e675f;
      --line: #d8ddd5;
      --paper: #f7f4ee;
      --panel: #fffdf8;
      --sage: #88a88f;
      --teal: #277c78;
      --navy: #263d59;
      --gold: #c8912f;
      --clay: #b85f42;
      --plum: #6d5375;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      color: var(--ink);
      background: var(--paper);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.45;
    }}
    header {{
      padding: 48px clamp(18px, 5vw, 72px) 30px;
      border-bottom: 1px solid var(--line);
      background: var(--panel);
    }}
    .eyebrow {{
      max-width: 980px;
      color: var(--teal);
      font-weight: 700;
      font-size: 13px;
      text-transform: uppercase;
    }}
    h1 {{
      max-width: 1100px;
      margin: 18px 0 14px;
      font-size: clamp(42px, 7vw, 86px);
      line-height: .96;
      letter-spacing: 0;
    }}
    header p {{
      max-width: 880px;
      margin: 0;
      font-size: clamp(18px, 2vw, 24px);
      color: var(--muted);
    }}
    main {{ padding: 32px clamp(18px, 5vw, 72px) 72px; }}
    .metrics {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
      margin-bottom: 32px;
    }}
    .metric, .panel, .segment-card {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
    }}
    .metric {{ padding: 16px; }}
    .metric span {{ color: var(--muted); font-size: 12px; text-transform: uppercase; }}
    .metric strong {{ display: block; margin-top: 6px; font-size: 24px; }}
    .section-head {{
      display: flex;
      justify-content: space-between;
      gap: 24px;
      align-items: end;
      margin: 34px 0 16px;
    }}
    .section-head h2 {{ margin: 0; font-size: clamp(27px, 3vw, 42px); letter-spacing: 0; }}
    .section-head p {{ max-width: 720px; margin: 0; color: var(--muted); }}
    .panel {{ padding: 18px; overflow: auto; }}
    .visual-grid {{
      display: grid;
      grid-template-columns: minmax(0, 1.15fr) minmax(320px, .85fr);
      gap: 16px;
      align-items: start;
    }}
    img.visual {{
      display: block;
      width: 100%;
      height: auto;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
    }}
    .findings {{
      margin: 0;
      padding-left: 20px;
    }}
    .findings li {{ margin: 0 0 12px; }}
    .cards {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
    }}
    .segment-card {{
      min-height: 350px;
      padding: 16px;
      display: flex;
      flex-direction: column;
    }}
    .segment-kicker {{
      color: var(--teal);
      font-weight: 700;
      font-size: 12px;
      text-transform: uppercase;
    }}
    .segment-card h3 {{
      margin: 14px 0 10px;
      font-size: 20px;
      line-height: 1.14;
      letter-spacing: 0;
    }}
    .segment-card p {{ margin: 0 0 14px; color: var(--muted); }}
    dl {{ margin: auto 0 0; }}
    dt {{ color: var(--muted); font-size: 11px; text-transform: uppercase; margin-top: 10px; }}
    dd {{ margin: 3px 0 0; }}
    table {{
      width: 100%;
      border-collapse: collapse;
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      overflow: hidden;
    }}
    th, td {{
      padding: 12px 13px;
      border-bottom: 1px solid var(--line);
      text-align: left;
      vertical-align: top;
    }}
    th {{ color: var(--muted); font-size: 12px; text-transform: uppercase; background: #f1eadc; }}
    td span {{ color: var(--muted); font-size: 12px; }}
    .table-scroll {{
      overflow-x: auto;
      border-radius: 8px;
    }}
    .table-scroll table {{ min-width: 920px; }}
    .note {{
      margin-top: 14px;
      padding: 14px 16px;
      border-left: 4px solid var(--gold);
      background: rgba(200,145,47,.12);
      color: #5d4a24;
      border-radius: 6px;
    }}
    @media (max-width: 1100px) {{
      .metrics, .cards {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
      .visual-grid {{ grid-template-columns: 1fr; }}
    }}
    @media (max-width: 680px) {{
      .metrics, .cards {{ grid-template-columns: 1fr; }}
      .section-head {{ display: block; }}
    }}
  </style>
</head>
<body>
  <header>
    <div class="eyebrow">{esc(data['status'])}</div>
    <h1>{esc(data['title'])}</h1>
    <p>{esc(data['subtitle'])}</p>
  </header>
  <main>
    <section class="metrics" aria-label="Current Atlas summary">
      <article class="metric"><span>Benchmark corpus</span><strong>{int(data['benchmark_items'])} items</strong></article>
      <article class="metric"><span>Stored model panel</span><strong>{int(data['model_panel_items'])}/{int(data['benchmark_items'])}</strong></article>
      <article class="metric"><span>Best economic default</span><strong>GPT-5.4 Mini</strong></article>
      <article class="metric"><span>OpenAI ladder cost</span><strong>${float(data['openai_ladder_cost_usd']):.2f}</strong></article>
    </section>

    <section>
      <div class="section-head">
        <h2>Executive Readout</h2>
        <p>This is no longer a ceiling-chasing model leaderboard. The useful artifact is a routing map: when to use cheap models, when to buy frontier quality, and when to keep a human in the loop.</p>
      </div>
      <div class="visual-grid">
        <img class="visual" src="model_frontier.svg" alt="Scatter plot of model quality by estimated cost burden">
        <div class="panel">
          <ol class="findings">
            {render_findings(data)}
          </ol>
          <p class="note">{esc(data['data_caveat'])}</p>
        </div>
      </div>
    </section>

    <section>
      <div class="section-head">
        <h2>Segment Heatmap</h2>
        <p>Retail task class changes the model choice. GPT-5 Mini is strongest for clerical fidelity tasks; GPT-5.4 Mini is the best broad economic route; GPT-5.5 is the premium anchor.</p>
      </div>
      <img class="visual" src="segment_heatmap.svg" alt="Heatmap of OpenAI model scores by retail segment">
    </section>

    <section>
      <div class="section-head">
        <h2>Routing Cards</h2>
        <p>Recommended defaults by segment, with deterministic controls and human-review boundaries.</p>
      </div>
      <div class="cards">
        {render_segment_cards(data)}
      </div>
    </section>

    <section>
      <div class="section-head">
        <h2>Current Scored Panel</h2>
        <p>Stored model runs are retained as legacy-panel evidence after the corpus expansion. Free-tier and local results are useful comparators, but their production cost assumptions still need calibration.</p>
      </div>
      <div class="table-scroll">
        <table>
          <thead>
            <tr>
              <th>Rank</th>
              <th>Model</th>
              <th>Score</th>
              <th>Estimated Cost</th>
              <th>Packs Passing</th>
              <th>Pareto</th>
              <th>Readout</th>
            </tr>
          </thead>
          <tbody>
            {render_rank_table(data['model_records'])}
          </tbody>
        </table>
      </div>
    </section>
  </main>
</body>
</html>
"""


def render_analysis_markdown(data: dict[str, Any]) -> str:
    rows = []
    for row in data["model_records"][:12]:
        cost = "$0" if float(row["estimated_cost_usd"]) == 0 else f"${float(row['estimated_cost_usd']):.4f}"
        rows.append(
            f"| `{row['model_id']}` | {row['overall_average']}/10 | {row['attempted_items']}/{row.get('available_items', row['attempted_items'])} | "
            f"{row['packs_passing']}/8 | {cost} | {'Yes' if row['pareto_frontier'] else 'No'} |"
        )
    segment_rows = []
    for segment in data["segment_summaries"]:
        leader = segment["quality_leader"]
        economic = segment["economic_pick"]
        segment_rows.append(
            f"| {segment['label']} | `{leader.get('model_id', 'n/a')}` ({leader.get('score', 0)}/10) | "
            f"`{economic.get('model_id', 'n/a')}` ({economic.get('score', 0)}/10) | {segment['human_review']} |"
        )
    findings = "\n".join(f"- {finding}" for finding in data["key_findings"])
    return f"""# MerchBench Current Results Analysis

Generated: {data['generated_at_utc']}

## Executive Findings

{findings}

## Model Leaderboard

This table excludes deterministic sanity baselines and partial/failed provider probes.

| Model | Overall Avg | Coverage | Packs Passing | Estimated Artifact Cost | Pareto Frontier |
| :--- | ---: | ---: | ---: | ---: | :--- |
{chr(10).join(rows)}

## Segment Routing Readout

| Segment | Quality Leader | Economic Pick | Human Review Boundary |
| :--- | :--- | :--- | :--- |
{chr(10).join(segment_rows)}

## Cost Interpretation

The five-model OpenAI ladder has an estimated artifact cost of ${float(data['openai_ladder_cost_usd']):.4f} for the successful stored responses. That is enough evidence to populate the first economic-routing artifact, but production guidance still needs provider-specific latency, retry variance, and price-plan normalization.

## Scorer Caveat

The deterministic baselines remain useful as harness and scorer sanity checks. Anti-echo hardening now keeps source echo, keyword stuffing, generic, over-escalating, over-aggressive, over-conservative, and arithmetic-only baselines below deployable thresholds. Public benchmark claims should still distinguish model-run triage scores from final human-calibrated scores.

## Website Artifacts

- `reports/atlas/index.html`
- `reports/atlas/model_frontier.svg`
- `reports/atlas/segment_heatmap.svg`
- `reports/atlas/atlas_data.json`
"""


def main() -> int:
    ATLAS_DIR.mkdir(parents=True, exist_ok=True)
    data = build_data()
    write_json(ATLAS_DATA, data)
    OUTPUT_FRONTIER_SVG.write_text(render_frontier_svg(data["model_records"]))
    OUTPUT_HEATMAP_SVG.write_text(render_heatmap_svg(data))
    OUTPUT_HTML.write_text(render_html(data))
    OUTPUT_ANALYSIS.write_text(render_analysis_markdown(data))
    print(f"Wrote {ATLAS_DATA.relative_to(ROOT)}")
    print(f"Wrote {OUTPUT_FRONTIER_SVG.relative_to(ROOT)}")
    print(f"Wrote {OUTPUT_HEATMAP_SVG.relative_to(ROOT)}")
    print(f"Wrote {OUTPUT_HTML.relative_to(ROOT)}")
    print(f"Wrote {OUTPUT_ANALYSIS.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
