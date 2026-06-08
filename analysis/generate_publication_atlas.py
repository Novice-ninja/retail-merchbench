#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis"))

import generate_atlas
import generate_publication_metrics


ATLAS_DIR = ROOT / "reports" / "atlas"
DATA_PATH = ATLAS_DIR / "atlas_data.json"
REPORT_PATH = ATLAS_DIR / "report.md"
HTML_PATH = ATLAS_DIR / "index.html"
FRONTIER_PATH = ATLAS_DIR / "model_frontier.svg"
HEATMAP_PATH = ATLAS_DIR / "segment_heatmap.svg"
SEGMENT_QUADRANTS_PATH = ATLAS_DIR / "segment_quadrants.svg"
ROUTING_LADDER_PATH = ATLAS_DIR / "routing_ladder.svg"
ECONOMIC_REGRET_PATH = ATLAS_DIR / "economic_regret.svg"
README_PATH = ATLAS_DIR / "README.md"

COLOR_INK = "#17211b"
COLOR_MUTED = "#5e675f"
COLOR_LINE = "#d8ddd5"
COLOR_PAPER = "#f7f4ee"
COLOR_PANEL = "#fffdf8"
COLOR_TEAL = "#277c78"
COLOR_SAGE = "#88a88f"
COLOR_GOLD = "#c8912f"
COLOR_CLAY = "#b85f42"
COLOR_PURPLE = "#6d5375"

CLUSTER_COLORS = {
    "Premium frontier": COLOR_TEAL,
    "Frontier proprietary": "#315f7f",
    "Efficient frontier": COLOR_GOLD,
    "Efficient mid-tier": "#a7a13a",
    "Small paid model": COLOR_CLAY,
    "Free hosted frontier": "#4f8a64",
    "Free hosted open": "#6b7f9b",
    "Local model": COLOR_PURPLE,
    "Local small model": "#8c6f95",
}

MODEL_SHORT_LABELS = {
    "openai/gpt-5.5": "5.5",
    "openai/gpt-5.4": "5.4",
    "openai/gpt-5.4-mini": "5.4M",
    "openai/gpt-5-mini": "5M",
    "openai/gpt-5-nano": "5N",
    "openai/gpt-4.1-nano": "4.1N",
    "cerebras/zai-glm-4.7": "GLM",
    "cerebras/gpt-oss-120b": "OSS",
    "groq/qwen/qwen3-32b": "Qwen",
    "groq/meta-llama/llama-4-scout-17b-16e-instruct": "Scout",
    "groq/llama-3.3-70b-versatile": "L3.3",
    "ollama/gemma4:e2b": "Gemma",
    "ollama/llama3.2:3b": "L3.2",
    "ollama/lfm2.5-thinking:1.2b": "LFM",
}


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def money(value: float | int | None) -> str:
    if not value:
        return "$0"
    return f"${float(value):.4f}"


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def clean_text(text: str) -> str:
    return "\n".join(line.rstrip() for line in text.splitlines()) + "\n"


def model_by_id(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {row["model_id"]: row for row in data.get("model_records", [])}


def economic_by_id(metrics: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {row["model_id"]: row for row in metrics.get("models", [])}


def enrich_data(data: dict[str, Any], metrics: dict[str, Any]) -> dict[str, Any]:
    data = json.loads(json.dumps(data))
    data.pop("version", None)
    data["schema_version"] = "1.0"
    data["artifact_name"] = "Retail MerchBench Atlas"
    data["generated_at_utc"] = datetime.now(UTC).isoformat(timespec="seconds")
    data["publication_metrics"] = metrics
    data["decision_readout"] = {
        "decision": "Use GPT-5.4 Mini as the broad economic default; reserve GPT-5.5 for high-downside exceptions; use GPT-5 Mini for clerical fidelity and portfolio triage; treat Z.ai GLM 4.7 as the best free hosted comparator.",
        "evidence": "100 segment eval-pack items, 14 real models with full scored coverage in the curated panel, deterministic anti-echo baselines, and token-derived artifact cost estimates where pricing is encoded.",
        "non_claim": "Retail MerchBench is not a human-validated public ranking, not a production latency study, and not a retailer-specific cost model.",
    }
    return data


def report_leaderboard(data: dict[str, Any], metrics: dict[str, Any]) -> str:
    metric_rows = economic_by_id(metrics)
    lines = [
        "| Rank | Model | Overall | Risk-Weighted | Artifact Cost | Cost / 1k Calls | Routing Readout |",
        "| ---: | :--- | ---: | ---: | ---: | ---: | :--- |",
    ]
    for rank, row in enumerate(data["model_records"][:14], 1):
        metric = metric_rows.get(row["model_id"], {})
        per_1000 = metric.get("estimated_cost_per_1000_workflow_calls_usd")
        per_1000_label = "n/a" if per_1000 is None else f"${float(per_1000):.4f}"
        lines.append(
            f"| {rank} | `{row['model_id']}` | {row['overall_average']}/10 | "
            f"{metric.get('risk_weighted_average', 'n/a')}/10 | {money(row['estimated_cost_usd'])} | "
            f"{per_1000_label} | {row['notes']} |"
        )
    return "\n".join(lines)


def segment_report_rows(data: dict[str, Any]) -> str:
    lines = [
        "| Segment | Quality Leader | Economic Pick | Default Route | Human Review Boundary |",
        "| :--- | :--- | :--- | :--- | :--- |",
    ]
    for segment in data["segment_summaries"]:
        leader = segment["quality_leader"]
        economic = segment["economic_pick"]
        lines.append(
            f"| {segment['label']} | `{leader.get('model_id')}` ({leader.get('score')}/10) | "
            f"`{economic.get('model_id')}` ({economic.get('score')}/10) | "
            f"{segment['default_route']} | {segment['human_review']} |"
        )
    return "\n".join(lines)


def provider_panel_rows(data: dict[str, Any]) -> str:
    provider_groups: dict[str, list[dict[str, Any]]] = {}
    for row in data["model_records"]:
        provider_groups.setdefault(row["provider"], []).append(row)
    lines = [
        "| Provider | Models in Ranked Panel | Best Model | Best Score | Notes |",
        "| :--- | ---: | :--- | ---: | :--- |",
    ]
    for provider in sorted(provider_groups):
        rows = sorted(provider_groups[provider], key=lambda item: -float(item["overall_average"]))
        best = rows[0]
        if provider == "ollama":
            note = "Local/no-quota, but current local scores are below deployable thresholds; two local runs have response-contract caveats."
        elif provider == "openai":
            note = "Paid ladder defines the quality-cost frontier in Retail MerchBench."
        elif provider == "cerebras":
            note = "Strongest free hosted result comes from Z.ai GLM 4.7."
        elif provider == "groq":
            note = "Useful free hosted open-model comparator pool."
        else:
            note = "Curated full-coverage panel member."
        lines.append(f"| `{provider}` | {len(rows)} | `{best['model_id']}` | {best['overall_average']}/10 | {note} |")
    return "\n".join(lines)


def cluster_color(row: dict[str, Any]) -> str:
    return CLUSTER_COLORS.get(str(row.get("cluster", "")), COLOR_MUTED)


def short_model_label(model_id: str) -> str:
    return MODEL_SHORT_LABELS.get(model_id, model_id.rsplit("/", 1)[-1][:8])


def stage_for_model(model_id: str) -> str:
    if model_id in {"openai/gpt-5.5", "openai/gpt-5.4"}:
        return "premium"
    if model_id == "openai/gpt-5.4-mini":
        return "efficient"
    if model_id == "openai/gpt-5-mini":
        return "mini"
    if "nano" in model_id or model_id.startswith(("ollama/", "groq/")):
        return "small"
    if model_id.startswith("cerebras/"):
        return "mini"
    return "small"


def render_segment_quadrants_svg(data: dict[str, Any]) -> str:
    width, height = 1280, 1580
    cols = 2
    panel_w, panel_h = 580, 320
    gap_x, gap_y = 38, 42
    start_x, start_y = 40, 116
    plot_pad_l, plot_pad_t, plot_pad_r, plot_pad_b = 42, 48, 20, 52
    min_score, max_score = 2.0, 9.0
    cost_threshold, score_threshold = 7.5, 7.0
    records = data["model_records"]
    segment_lookup = {segment["segment_id"]: segment for segment in data["segment_summaries"]}

    def px(plot_x: float, plot_w: float, row: dict[str, Any]) -> float:
        return plot_x + min(max(float(row.get("cost_index", 0)), 0), 10) / 10 * plot_w

    def py(plot_y: float, plot_h: float, score: float) -> float:
        bounded = min(max(score, min_score), max_score)
        return plot_y + (max_score - bounded) / (max_score - min_score) * plot_h

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        "<title>MerchBench segment routing quadrants</title>",
        "<desc>Small-multiple 2x2 charts plotting model segment quality by economic burden.</desc>",
        f'<rect width="{width}" height="{height}" fill="{COLOR_PAPER}"/>',
        f'<text x="34" y="42" font-size="24" font-weight="800" fill="{COLOR_INK}">Segment routing quadrants</text>',
        f'<text x="34" y="68" font-size="13" fill="{COLOR_MUTED}">Each panel plots segment score against cost burden. Black rings mark economic picks; star labels mark quality leaders.</text>',
        f'<text x="34" y="92" font-size="12" fill="{COLOR_MUTED}">Crosshairs: score 7.0 proxy floor and cost-burden 7.5 premium boundary. Bubble size reflects response-token burden.</text>',
    ]

    for index, segment_id in enumerate(generate_atlas.SEGMENT_ORDER):
        col = index % cols
        row_index = index // cols
        x0 = start_x + col * (panel_w + gap_x)
        y0 = start_y + row_index * (panel_h + gap_y)
        plot_x = x0 + plot_pad_l
        plot_y = y0 + plot_pad_t
        plot_w = panel_w - plot_pad_l - plot_pad_r
        plot_h = panel_h - plot_pad_t - plot_pad_b
        cost_x = plot_x + cost_threshold / 10 * plot_w
        score_y = py(plot_y, plot_h, score_threshold)
        segment = segment_lookup[segment_id]
        leader_id = segment["quality_leader"].get("model_id")
        economic_id = segment["economic_pick"].get("model_id")

        parts.extend(
            [
                f'<rect x="{x0}" y="{y0}" width="{panel_w}" height="{panel_h}" rx="10" fill="{COLOR_PANEL}" stroke="{COLOR_LINE}"/>',
                f'<text x="{x0 + 14}" y="{y0 + 28}" font-size="15" font-weight="800" fill="{COLOR_INK}">{esc(segment["label"])}</text>',
                f'<rect x="{plot_x}" y="{plot_y}" width="{cost_x - plot_x}" height="{score_y - plot_y}" fill="#dfeee8"/>',
                f'<rect x="{cost_x}" y="{plot_y}" width="{plot_x + plot_w - cost_x}" height="{score_y - plot_y}" fill="#f3e7c8"/>',
                f'<rect x="{plot_x}" y="{score_y}" width="{cost_x - plot_x}" height="{plot_y + plot_h - score_y}" fill="#f6e7dc"/>',
                f'<rect x="{cost_x}" y="{score_y}" width="{plot_x + plot_w - cost_x}" height="{plot_y + plot_h - score_y}" fill="#eee7f1"/>',
                f'<rect x="{plot_x}" y="{plot_y}" width="{plot_w}" height="{plot_h}" fill="none" stroke="{COLOR_LINE}"/>',
                f'<line x1="{cost_x:.1f}" y1="{plot_y}" x2="{cost_x:.1f}" y2="{plot_y + plot_h}" stroke="{COLOR_INK}" stroke-width="1" stroke-dasharray="4 4" opacity=".42"/>',
                f'<line x1="{plot_x}" y1="{score_y:.1f}" x2="{plot_x + plot_w}" y2="{score_y:.1f}" stroke="{COLOR_INK}" stroke-width="1" stroke-dasharray="4 4" opacity=".42"/>',
                f'<text x="{plot_x - 9}" y="{py(plot_y, plot_h, 9) + 4:.1f}" text-anchor="end" font-size="10" fill="{COLOR_MUTED}">9</text>',
                f'<text x="{plot_x - 9}" y="{score_y + 4:.1f}" text-anchor="end" font-size="10" fill="{COLOR_MUTED}">7</text>',
                f'<text x="{plot_x - 9}" y="{py(plot_y, plot_h, 2) + 4:.1f}" text-anchor="end" font-size="10" fill="{COLOR_MUTED}">2</text>',
                f'<text x="{plot_x}" y="{plot_y + plot_h + 20}" font-size="10" fill="{COLOR_MUTED}">low cost</text>',
                f'<text x="{plot_x + plot_w}" y="{plot_y + plot_h + 20}" text-anchor="end" font-size="10" fill="{COLOR_MUTED}">premium</text>',
            ]
        )

        for record in sorted(records, key=lambda item: float(item.get("overall_average", 0))):
            score = float(record["segment_scores"].get(segment_id, 0))
            x = px(plot_x, plot_w, record)
            y = py(plot_y, plot_h, score)
            radius = 4.5 + min(float(record.get("experience_burden_index", 0)), 10) * 0.38
            stroke = COLOR_INK if record["model_id"] == economic_id else COLOR_PANEL
            stroke_width = 2.8 if record["model_id"] == economic_id else 1.4
            opacity = "1" if record["model_id"] in {leader_id, economic_id} or record.get("provider") == "openai" else ".68"
            parts.append(
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{radius:.1f}" fill="{cluster_color(record)}" stroke="{stroke}" stroke-width="{stroke_width}" opacity="{opacity}"/>'
            )
            if record["model_id"] == leader_id:
                parts.append(f'<text x="{x:.1f}" y="{y - radius - 4:.1f}" text-anchor="middle" font-size="13" font-weight="900" fill="{COLOR_INK}">*</text>')
            if record["model_id"] in {leader_id, economic_id}:
                anchor = "start" if x < plot_x + plot_w * 0.56 else "end"
                dx = 8 if anchor == "start" else -8
                dy = 3
                if leader_id != economic_id:
                    dy = -12 if record["model_id"] == leader_id else 16
                label = short_model_label(record["model_id"])
                parts.append(f'<text x="{x + dx:.1f}" y="{y + dy:.1f}" text-anchor="{anchor}" font-size="10" font-weight="700" fill="{COLOR_INK}">{esc(label)}</text>')

        parts.append(
            f'<text x="{x0 + 14}" y="{y0 + panel_h - 14}" font-size="10" fill="{COLOR_MUTED}">Pick: {esc(segment["economic_pick"].get("display_name", "n/a"))} | Leader: {esc(segment["quality_leader"].get("display_name", "n/a"))}</text>'
        )

    legend_y = height - 42
    legend_x = 34
    legend_items = [
        ("Premium frontier", COLOR_TEAL),
        ("Efficient frontier", COLOR_GOLD),
        ("Free hosted", "#4f8a64"),
        ("Small paid/open", COLOR_CLAY),
        ("Local", COLOR_PURPLE),
    ]
    for label, color in legend_items:
        parts.append(f'<circle cx="{legend_x}" cy="{legend_y}" r="6" fill="{color}"/>')
        parts.append(f'<text x="{legend_x + 12}" y="{legend_y + 4}" font-size="12" fill="{COLOR_MUTED}">{esc(label)}</text>')
        legend_x += 170
    parts.append(f'<text x="{legend_x + 12}" y="{legend_y + 4}" font-size="12" fill="{COLOR_MUTED}">Black ring = economic pick; * = quality leader</text>')
    parts.append("</svg>")
    return "\n".join(parts)


def render_routing_ladder_svg(data: dict[str, Any]) -> str:
    width, height = 1280, 690
    left, top = 210, 128
    row_h = 58
    stage_x = {
        "rules": 245,
        "small": 410,
        "mini": 575,
        "efficient": 740,
        "premium": 905,
        "human": 1070,
    }
    stage_labels = [
        ("rules", "Rules/checks"),
        ("small", "Small/local"),
        ("mini", "Mini/mid"),
        ("efficient", "Efficient frontier"),
        ("premium", "Premium frontier"),
        ("human", "Human review"),
    ]
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        "<title>MerchBench routing ladder</title>",
        "<desc>Workflow ladder showing recommended model tiers and review boundaries for each retail segment.</desc>",
        f'<rect width="{width}" height="{height}" fill="{COLOR_PAPER}"/>',
        f'<text x="34" y="44" font-size="24" font-weight="800" fill="{COLOR_INK}">Retail model-routing ladder</text>',
        f'<text x="34" y="70" font-size="13" fill="{COLOR_MUTED}">Each row shows the default model tier, premium escalation point, and whether human review remains part of the workflow.</text>',
    ]
    for key, label in stage_labels:
        x = stage_x[key]
        parts.append(f'<text x="{x}" y="106" text-anchor="middle" font-size="12" font-weight="800" fill="{COLOR_MUTED}">{label}</text>')
        parts.append(f'<line x1="{x}" y1="{top - 6}" x2="{x}" y2="{top + row_h * len(data["segment_summaries"]) - 16}" stroke="{COLOR_LINE}" stroke-dasharray="3 5"/>')

    for idx, segment in enumerate(data["segment_summaries"]):
        y = top + idx * row_h
        cy = y + 22
        economic_id = str(segment["economic_pick"].get("model_id", ""))
        leader_id = str(segment["quality_leader"].get("model_id", ""))
        econ_stage = stage_for_model(economic_id)
        leader_stage = stage_for_model(leader_id)
        review_text = str(segment["human_review"])
        review_required = review_text.startswith("Yes") or review_text.startswith("Required") or review_text.startswith("Recommended")
        review_conditional = review_text.startswith("Only")

        parts.append(f'<text x="34" y="{cy + 4}" font-size="13" font-weight="800" fill="{COLOR_INK}">{esc(segment["label"])}</text>')
        parts.append(f'<line x1="{left}" y1="{cy}" x2="{stage_x["human"]}" y2="{cy}" stroke="{COLOR_LINE}" stroke-width="3"/>')
        parts.append(f'<circle cx="{stage_x["rules"]}" cy="{cy}" r="7" fill="{COLOR_PANEL}" stroke="{COLOR_MUTED}" stroke-width="2"/>')

        ex = stage_x[econ_stage]
        lx = stage_x[leader_stage]
        if leader_id and leader_id != economic_id and leader_stage == econ_stage:
            ex -= 15
            lx += 15
        parts.append(f'<circle cx="{ex}" cy="{cy}" r="12" fill="{COLOR_TEAL}" stroke="{COLOR_INK}" stroke-width="2.5"/>')
        parts.append(f'<text x="{ex}" y="{cy + 4}" text-anchor="middle" font-size="9" font-weight="800" fill="#ffffff">E</text>')
        if leader_id and leader_id != economic_id:
            parts.append(f'<circle cx="{lx}" cy="{cy}" r="10" fill="{COLOR_GOLD}" stroke="{COLOR_INK}" stroke-width="1.6"/>')
            parts.append(f'<text x="{lx}" y="{cy + 4}" text-anchor="middle" font-size="9" font-weight="800" fill="#ffffff">L</text>')
        if review_required or review_conditional:
            fill = COLOR_PURPLE if review_required else COLOR_PANEL
            stroke = COLOR_PURPLE
            dash = "" if review_required else ' stroke-dasharray="3 3"'
            parts.append(f'<circle cx="{stage_x["human"]}" cy="{cy}" r="11" fill="{fill}" stroke="{stroke}" stroke-width="2"{dash}/>')
            label_fill = "#ffffff" if review_required else COLOR_PURPLE
            parts.append(f'<text x="{stage_x["human"]}" y="{cy + 4}" text-anchor="middle" font-size="9" font-weight="800" fill="{label_fill}">H</text>')

        label = f'{segment["economic_pick"].get("display_name", "n/a")} default'
        if leader_id != economic_id:
            label += f'; {segment["quality_leader"].get("display_name", "n/a")} leader'
        parts.append(f'<text x="{left}" y="{cy + 24}" font-size="10" fill="{COLOR_MUTED}">{esc(label)}</text>')

    legend_y = height - 42
    legend_items = [
        ("E", "economic pick", 220),
        ("L", "quality leader", 220),
        ("H", "human review required", 260),
        ("dashed H", "conditional review", 260),
    ]
    lx = 34
    for symbol, label, item_w in legend_items:
        parts.append(f'<text x="{lx}" y="{legend_y}" font-size="12" font-weight="800" fill="{COLOR_INK}">{esc(symbol)}</text>')
        label_dx = 66 if symbol == "dashed H" else 34
        parts.append(f'<text x="{lx + label_dx}" y="{legend_y}" font-size="12" fill="{COLOR_MUTED}">{esc(label)}</text>')
        lx += item_w
    parts.append("</svg>")
    return "\n".join(parts)


def render_economic_regret_svg(data: dict[str, Any]) -> str:
    width, height = 1280, 600
    left, top = 250, 118
    bar_h, gap = 28, 20
    max_regret = 1.4
    chart_w = 720
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        "<title>MerchBench economic regret by segment</title>",
        "<desc>Bar chart showing quality gap between quality leader and economic pick by retail segment.</desc>",
        f'<rect width="{width}" height="{height}" fill="{COLOR_PAPER}"/>',
        f'<text x="34" y="42" font-size="24" font-weight="800" fill="{COLOR_INK}">Economic regret by segment</text>',
        f'<text x="34" y="66" font-size="13" fill="{COLOR_MUTED}">Regret is the quality gap between the segment leader and the recommended economic pick. Lower is better.</text>',
    ]
    for tick in [0, 0.25, 0.5, 0.75, 1.0, 1.25]:
        x = left + tick / max_regret * chart_w
        parts.append(f'<line x1="{x:.1f}" y1="{top - 16}" x2="{x:.1f}" y2="{top + 8 * (bar_h + gap) - gap + 18}" stroke="{COLOR_LINE}"/>')
        parts.append(f'<text x="{x:.1f}" y="{top - 24}" text-anchor="middle" font-size="10" fill="{COLOR_MUTED}">{tick:g}</text>')

    for idx, segment in enumerate(data["segment_summaries"]):
        y = top + idx * (bar_h + gap)
        leader = segment["quality_leader"]
        economic = segment["economic_pick"]
        regret = max(0.0, float(leader.get("score", 0)) - float(economic.get("score", 0)))
        bar_w = min(regret, max_regret) / max_regret * chart_w
        fill = COLOR_TEAL if regret <= 0.12 else COLOR_GOLD if regret <= 0.55 else COLOR_CLAY
        parts.append(f'<text x="34" y="{y + 19}" font-size="13" font-weight="800" fill="{COLOR_INK}">{esc(segment["label"])}</text>')
        parts.append(f'<rect x="{left}" y="{y}" width="{chart_w}" height="{bar_h}" rx="5" fill="{COLOR_PANEL}" stroke="{COLOR_LINE}"/>')
        parts.append(f'<rect x="{left}" y="{y}" width="{bar_w:.1f}" height="{bar_h}" rx="5" fill="{fill}"/>')
        parts.append(f'<text x="{left + bar_w + 8:.1f}" y="{y + 19}" font-size="12" font-weight="800" fill="{COLOR_INK}">{regret:.3f}</text>')
        parts.append(
            f'<text x="{left + chart_w + 74}" y="{y + 12}" font-size="10" fill="{COLOR_MUTED}">Leader: {esc(leader.get("display_name", "n/a"))} ({leader.get("score", 0)})</text>'
        )
        parts.append(
            f'<text x="{left + chart_w + 74}" y="{y + 27}" font-size="10" fill="{COLOR_MUTED}">Pick: {esc(economic.get("display_name", "n/a"))} ({economic.get("score", 0)})</text>'
        )
    parts.append(f'<text x="{left}" y="{height - 28}" font-size="12" fill="{COLOR_MUTED}">Green: near-zero tradeoff. Orange/red: the cheaper default gives up material quality.</text>')
    parts.append("</svg>")
    return "\n".join(parts)


def render_report(data: dict[str, Any], metrics: dict[str, Any]) -> str:
    findings = "\n".join(f"- {finding}" for finding in data["key_findings"])
    return f"""# Retail MerchBench Report

Generated: {data['generated_at_utc']}

## Executive Summary

Retail MerchBench reframes the benchmark around economic model routing for retail decisions. The question is not only which model scores highest. The question is which model or workflow tier is economically sufficient for each class of retail work once quality, cost, latency burden, deterministic controls, downside risk, and human review are considered.

The current evidence package contains {data['benchmark_items']} segment eval-pack items and a curated provider panel with {data['model_panel_items']}/{data['benchmark_items']} scored coverage for 14 real models. The scored panel spans local Ollama, hosted Groq/Cerebras, and the paid OpenAI ladder. OpenRouter free-tier probes and xAI availability are documented as capacity findings, not ranked results.

## Decision Readout

- Broad economic default: `openai/gpt-5.4-mini`.
- Premium quality anchor: `openai/gpt-5.5`.
- Cheap paid specialist: `openai/gpt-5-mini`.
- Strongest free hosted comparator: `cerebras/zai-glm-4.7`.
- Non-autonomous segments: pricing/promotion, routine planning, portfolio tradeoff, and high-risk operational triage still need deterministic controls and human review boundaries.

## Key Findings

{findings}

## Model Leaderboard

{report_leaderboard(data, metrics)}

## Segment Routing Matrix

{segment_report_rows(data)}

## Visual Routing System

The visual package contains four complementary views:

- `model_frontier.svg`: master cost-quality frontier across the full model panel.
- `segment_quadrants.svg`: eight segment-level 2x2s plotting each model by segment quality and economic burden.
- `routing_ladder.svg`: model-tier workflow ladder showing default route, premium escalation, and human-review boundary by segment.
- `economic_regret.svg`: segment-level quality gap between the quality leader and the economic pick.

## Provider Coverage

{provider_panel_rows(data)}

## How To Consume Retail MerchBench

Use as a routing prior:

- Route low-risk summarization and structured extraction to the cheapest model that preserves numbers, caveats, and schema contracts.
- Put deterministic checks before model judgment for constraints, pricing, margin floors, pack multiples, OTB, labor capacity, and safety/compliance.
- Use `gpt-5.4-mini` as the default judgment model where the decision is reversible and guardrailed.
- Escalate to `gpt-5.5`, `gpt-5.4`, or human review when the downside is high, the action is irreversible, or the model is asked to override a hard constraint.
- Treat free hosted and local models as useful comparators and capacity buffers, not as autonomous retail decision engines in the current evidence base.

## Validity Boundaries

Retail MerchBench remains an automated-score artifact. It should not be marketed as a final human-validated public benchmark ranking until three missing pieces are complete:

- Human-rater calibration and inter-rater reliability.
- Repeated-run variance and rank stability.
- Production latency, retry, cache, and provider price normalization.

## Artifact Index

- `reports/atlas/index.html`: executive Atlas.
- `reports/atlas/report.md`: this written report.
- `reports/atlas/atlas_data.json`: structured data payload.
- `reports/atlas/model_frontier.svg`: quality-cost frontier.
- `reports/atlas/segment_heatmap.svg`: OpenAI segment heatmap.
- `reports/atlas/segment_quadrants.svg`: grid of segment-level 2x2 routing charts.
- `reports/atlas/routing_ladder.svg`: workflow-tier ladder by segment.
- `reports/atlas/economic_regret.svg`: quality gap between leader and economic pick by segment.
"""


def html_model_cards(data: dict[str, Any], metrics: dict[str, Any]) -> str:
    metric_rows = economic_by_id(metrics)
    cards = []
    for row in data["model_records"][:6]:
        metric = metric_rows.get(row["model_id"], {})
        risk = metric.get("risk_weighted_average", "n/a")
        cost = money(row["estimated_cost_usd"])
        cards.append(
            f"""
            <article class="model-card">
              <div class="kicker">{esc(row['cluster'])}</div>
              <h3>{esc(row['display_name'])}</h3>
              <div class="score">{row['overall_average']}<span>/10</span></div>
              <p>{esc(row['notes'])}</p>
              <dl>
                <dt>Risk weighted</dt><dd>{risk}/10</dd>
                <dt>Artifact cost</dt><dd>{cost}</dd>
                <dt>Coverage</dt><dd>{row['attempted_items']}/{row['available_items']}</dd>
              </dl>
            </article>
            """
        )
    return "\n".join(cards)


def html_segment_rows(data: dict[str, Any]) -> str:
    rows = []
    for segment in data["segment_summaries"]:
        leader = segment["quality_leader"]
        economic = segment["economic_pick"]
        rows.append(
            f"""
            <tr>
              <td><strong>{esc(segment['label'])}</strong></td>
              <td>{esc(leader.get('display_name'))}<br><span>{leader.get('score')}/10</span></td>
              <td>{esc(economic.get('display_name'))}<br><span>{economic.get('score')}/10</span></td>
              <td>{esc(segment['default_route'])}</td>
              <td>{esc(segment['human_review'])}</td>
            </tr>
            """
        )
    return "\n".join(rows)


def html_findings(data: dict[str, Any]) -> str:
    return "\n".join(f"<li>{esc(finding)}</li>" for finding in data["key_findings"][:7])


def render_html(data: dict[str, Any], metrics: dict[str, Any]) -> str:
    leader = data["model_records"][0]
    efficient = model_by_id(data)["openai/gpt-5.4-mini"]
    mini = model_by_id(data)["openai/gpt-5-mini"]
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Retail MerchBench Atlas</title>
  <link rel="icon" href="data:,">
  <style>
    :root {{
      --ink: #18221e;
      --muted: #64706b;
      --paper: #f5f1e8;
      --panel: #fffdf8;
      --line: #d9d4c8;
      --teal: #1f776f;
      --blue: #2e5575;
      --gold: #c08b2c;
      --clay: #b95f45;
      --green: #769b7d;
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
      min-height: 92vh;
      display: grid;
      grid-template-columns: minmax(0, 1.05fr) minmax(340px, .95fr);
      gap: clamp(24px, 5vw, 70px);
      align-items: center;
      padding: clamp(28px, 6vw, 76px);
      background:
        linear-gradient(120deg, rgba(255,253,248,.96), rgba(255,253,248,.72)),
        radial-gradient(circle at 15% 20%, rgba(31,119,111,.16), transparent 34%),
        linear-gradient(135deg, #f8f2e4, #e8eadf);
      border-bottom: 1px solid var(--line);
    }}
    .eyebrow {{
      color: var(--teal);
      font-weight: 800;
      letter-spacing: .08em;
      text-transform: uppercase;
      font-size: 13px;
    }}
    h1 {{
      margin: 18px 0 18px;
      max-width: 920px;
      font-size: clamp(48px, 7vw, 96px);
      line-height: .95;
      letter-spacing: 0;
    }}
    .lede {{
      max-width: 760px;
      color: var(--muted);
      font-size: clamp(18px, 2vw, 25px);
      margin: 0 0 28px;
    }}
    .hero-grid {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 10px;
      max-width: 760px;
    }}
    .stat, .panel, .model-card {{
      background: rgba(255,253,248,.94);
      border: 1px solid var(--line);
      border-radius: 8px;
      box-shadow: 0 18px 60px rgba(54,45,31,.08);
    }}
    .stat {{ padding: 15px; }}
    .stat span, .kicker, th {{
      color: var(--muted);
      font-size: 12px;
      font-weight: 800;
      letter-spacing: .06em;
      text-transform: uppercase;
    }}
    .stat strong {{ display: block; margin-top: 8px; font-size: 25px; }}
    .hero-panel {{ padding: 20px; }}
    .hero-panel h2 {{ margin: 0 0 14px; font-size: 27px; letter-spacing: 0; }}
    .decision-list {{ display: grid; gap: 8px; margin: 0; padding: 0; list-style: none; }}
    .decision-list li {{
      display: flex;
      gap: 10px;
      align-items: start;
      color: var(--muted);
    }}
    .decision-list li::before {{
      content: "";
      flex: 0 0 8px;
      width: 8px;
      height: 8px;
      margin-top: 7px;
      border-radius: 50%;
      background: var(--teal);
    }}
    main {{ padding: 36px clamp(18px, 5vw, 72px) 78px; }}
    .section-head {{
      display: flex;
      justify-content: space-between;
      align-items: end;
      gap: 24px;
      margin: 42px 0 18px;
    }}
    .section-head h2 {{ margin: 0; font-size: clamp(30px, 4vw, 52px); letter-spacing: 0; }}
    .section-head p {{ max-width: 720px; margin: 0; color: var(--muted); }}
    .visual-grid {{
      display: grid;
      grid-template-columns: minmax(0, 1.12fr) minmax(320px, .88fr);
      gap: 16px;
      align-items: start;
    }}
    .visual {{
      width: 100%;
      height: auto;
      display: block;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
    }}
    .panel {{ padding: 20px; }}
    .findings {{ margin: 0; padding-left: 21px; }}
    .findings li {{ margin-bottom: 12px; }}
    .model-grid {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 13px;
    }}
    .model-card {{ padding: 17px; }}
    .model-card h3 {{ margin: 10px 0 8px; font-size: 23px; letter-spacing: 0; }}
    .score {{ font-size: 42px; font-weight: 850; color: var(--teal); }}
    .score span {{ font-size: 18px; color: var(--muted); }}
    .model-card p {{ color: var(--muted); min-height: 68px; }}
    dl {{ display: grid; grid-template-columns: 1fr 1fr; gap: 6px 10px; margin: 14px 0 0; }}
    dt {{ color: var(--muted); font-size: 12px; }}
    dd {{ margin: 0; font-weight: 700; }}
    table {{
      width: 100%;
      border-collapse: collapse;
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      overflow: hidden;
    }}
    th, td {{ padding: 13px 14px; border-bottom: 1px solid var(--line); text-align: left; vertical-align: top; }}
    th {{ background: #efe7d6; }}
    td span {{ color: var(--muted); font-size: 12px; }}
    .table-scroll {{ overflow-x: auto; border-radius: 8px; }}
    .table-scroll table {{ min-width: 980px; }}
    .callout {{
      border-left: 5px solid var(--gold);
      background: rgba(192,139,44,.13);
      padding: 18px 20px;
      border-radius: 8px;
      color: #5e4b24;
    }}
    @media (max-width: 1080px) {{
      header, .visual-grid {{ grid-template-columns: 1fr; }}
      .model-grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
    }}
    @media (max-width: 680px) {{
      header {{ min-height: auto; padding: 20px; gap: 18px; }}
      .hero-grid {{ grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 8px; }}
      .stat {{ padding: 10px; }}
      .stat strong {{ font-size: 20px; }}
      .hero-panel {{ padding: 14px; }}
      .decision-list li {{ font-size: 15px; line-height: 1.35; }}
      .model-grid {{ grid-template-columns: 1fr; }}
      .section-head {{ display: block; }}
      dl {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <header>
    <div>
      <div class="eyebrow">Retail MerchBench · Retail AI Model Routing Atlas</div>
      <h1>The model choice is an economic decision.</h1>
      <p class="lede">A visual and written routing guide for choosing the cheapest safe model tier across retail planning workflows.</p>
      <div class="hero-grid" aria-label="Retail MerchBench evidence summary">
        <div class="stat"><span>Corpus</span><strong>{data['benchmark_items']} items</strong></div>
        <div class="stat"><span>Ranked panel</span><strong>14 models</strong></div>
        <div class="stat"><span>Coverage</span><strong>{data['model_panel_items']}/{data['benchmark_items']}</strong></div>
      </div>
    </div>
    <aside class="panel hero-panel">
      <h2>Retail MerchBench answer</h2>
      <ul class="decision-list">
        <li><strong>{esc(efficient['display_name'])}</strong>: broad default, {efficient['overall_average']}/10, {money(efficient['estimated_cost_usd'])} artifact cost.</li>
        <li><strong>{esc(leader['display_name'])}</strong>: premium quality anchor, {leader['overall_average']}/10.</li>
        <li><strong>{esc(mini['display_name'])}</strong>: cheap paid specialist for clerical fidelity and portfolio triage.</li>
        <li><strong>Human review</strong>: keep for pricing, portfolio, and high-risk operations.</li>
      </ul>
    </aside>
  </header>

  <main>
    <section>
      <div class="section-head">
        <h2>Frontier Map</h2>
        <p>Quality, cost, and response burden separate model clusters more usefully than a one-dimensional leaderboard.</p>
      </div>
      <div class="visual-grid">
        <img class="visual" src="model_frontier.svg" alt="Quality-cost frontier scatter plot">
        <div class="panel">
          <ol class="findings">{html_findings(data)}</ol>
        </div>
      </div>
    </section>

    <section>
      <div class="section-head">
        <h2>Segment 2x2 Grid</h2>
        <p>Each retail workflow has its own routing geometry. Black rings identify economic picks; star markers identify quality leaders.</p>
      </div>
      <img class="visual" src="segment_quadrants.svg" alt="Grid of segment-level cost versus quality quadrants">
    </section>

    <section>
      <div class="section-head">
        <h2>Routing Ladder</h2>
        <p>This translates model scores into the operating model: rules, small models, mini models, efficient frontier, premium escalation, and human review.</p>
      </div>
      <img class="visual" src="routing_ladder.svg" alt="Model-tier routing ladder by retail segment">
    </section>

    <section>
      <div class="section-head">
        <h2>Economic Regret</h2>
        <p>The regret chart shows how much quality is given up when the economic pick is cheaper than the quality leader.</p>
      </div>
      <img class="visual" src="economic_regret.svg" alt="Economic regret bar chart by retail segment">
    </section>

    <section>
      <div class="section-head">
        <h2>Leaders And Defaults</h2>
        <p>The premium winner is not always the right economic choice. Retail MerchBench separates quality anchors from routing defaults.</p>
      </div>
      <div class="model-grid">{html_model_cards(data, metrics)}</div>
    </section>

    <section>
      <div class="section-head">
        <h2>Segment Heatmap</h2>
        <p>Retail task class changes the answer. The same model is not optimal for extraction, pricing, portfolio tradeoff, and operational triage.</p>
      </div>
      <img class="visual" src="segment_heatmap.svg" alt="OpenAI model performance heatmap by retail segment">
    </section>

    <section>
      <div class="section-head">
        <h2>Routing Matrix</h2>
        <p>Recommended quality leader, economic pick, and human-review boundary by segment.</p>
      </div>
      <div class="table-scroll">
        <table>
          <thead>
            <tr>
              <th>Segment</th>
              <th>Quality Leader</th>
              <th>Economic Pick</th>
              <th>Default Route</th>
              <th>Human Review</th>
            </tr>
          </thead>
          <tbody>{html_segment_rows(data)}</tbody>
        </table>
      </div>
    </section>

    <section>
      <div class="section-head">
        <h2>Validity Boundary</h2>
        <p>Retail MerchBench is a routing-prior artifact, not a final human-validated benchmark ranking.</p>
      </div>
      <div class="callout">
        Scores are automated routing diagnostics. Human-rater calibration, repeated-run variance, production latency, retry behavior, caching, and provider price-plan normalization remain open before external benchmark claims should be treated as final.
      </div>
    </section>
  </main>
</body>
</html>
"""


def render_readme() -> str:
    return """# Retail MerchBench Artifacts

This directory contains the current executive artifact package.

- `index.html`: visual Atlas.
- `report.md`: written report.
- `atlas_data.json`: structured data used by the Atlas and report.
- `model_frontier.svg`: quality-cost frontier.
- `segment_heatmap.svg`: OpenAI segment heatmap.
- `segment_quadrants.svg`: segment-level cost-quality 2x2 grid.
- `routing_ladder.svg`: workflow-tier routing ladder.
- `economic_regret.svg`: quality gap between segment quality leader and economic pick.

Regenerate with:

```bash
make atlas
```
"""


def main() -> int:
    ATLAS_DIR.mkdir(parents=True, exist_ok=True)
    data = generate_atlas.build_data()
    write_json(DATA_PATH, data)
    metrics = generate_publication_metrics.build_metrics()
    enriched = enrich_data(data, metrics)
    write_json(DATA_PATH, enriched)
    FRONTIER_PATH.write_text(clean_text(generate_atlas.render_frontier_svg(enriched["model_records"])))
    HEATMAP_PATH.write_text(clean_text(generate_atlas.render_heatmap_svg(enriched)))
    SEGMENT_QUADRANTS_PATH.write_text(clean_text(render_segment_quadrants_svg(enriched)))
    ROUTING_LADDER_PATH.write_text(clean_text(render_routing_ladder_svg(enriched)))
    ECONOMIC_REGRET_PATH.write_text(clean_text(render_economic_regret_svg(enriched)))
    REPORT_PATH.write_text(clean_text(render_report(enriched, metrics)))
    HTML_PATH.write_text(clean_text(render_html(enriched, metrics)))
    README_PATH.write_text(clean_text(render_readme()))
    print(f"Wrote {DATA_PATH.relative_to(ROOT)}")
    print(f"Wrote {FRONTIER_PATH.relative_to(ROOT)}")
    print(f"Wrote {HEATMAP_PATH.relative_to(ROOT)}")
    print(f"Wrote {SEGMENT_QUADRANTS_PATH.relative_to(ROOT)}")
    print(f"Wrote {ROUTING_LADDER_PATH.relative_to(ROOT)}")
    print(f"Wrote {ECONOMIC_REGRET_PATH.relative_to(ROOT)}")
    print(f"Wrote {REPORT_PATH.relative_to(ROOT)}")
    print(f"Wrote {HTML_PATH.relative_to(ROOT)}")
    print(f"Wrote {README_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
