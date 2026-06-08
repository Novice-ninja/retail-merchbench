from __future__ import annotations

import json
import re
from pathlib import Path
from statistics import mean
from typing import Any

from merchbench.io import load_json, write_json


BASELINE_IDS = (
    "baseline/source_echo",
    "baseline/keyword_guardrail",
    "baseline/generic_consultant",
    "baseline/always_escalate",
    "baseline/always_buy_chase",
    "baseline/always_conservative",
    "baseline/arithmetic_only",
)
PRE_ANTI_ECHO_BASELINE_AVERAGES = {
    "baseline/source_echo": 7.7174,
    "baseline/keyword_guardrail": 7.9124,
}
ADVERSARIAL_BASELINE_THRESHOLDS = {
    "baseline/source_echo": 4.5,
    "baseline/keyword_guardrail": 5.5,
}
SCORING_METADATA_KEYS = {"source_excerpt", "baseline_id"}
TOKEN_RE = re.compile(r"[a-z0-9]+(?:\.[0-9]+)?")
DATE_RE = re.compile(r"\b(?:20[0-9]{2}[-/][0-9]{1,2}[-/][0-9]{1,2}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+[0-9]{1,2})\b", re.I)
MONEY_RE = re.compile(r"\$[0-9][0-9,]*(?:\.[0-9]+)?")
PERCENT_RE = re.compile(r"\b[0-9]+(?:\.[0-9]+)?\s*percent\b|\b[0-9]+(?:\.[0-9]+)?%")
SKU_RE = re.compile(r"\b[A-Z]{1,4}-[A-Z0-9]{1,4}(?:-[A-Z0-9]{1,4})?\b")
NUMBER_RE = re.compile(r"\b[0-9][0-9,]*(?:\.[0-9]+)?\b")

LIST_FIELD_HINTS = {
    "key_points",
    "numbers_preserved",
    "risks_or_caveats",
    "conflicts",
    "missing_required_fields",
    "deterministic_checks",
    "blocking_constraints",
    "non_blocking_warnings",
    "risk_controls",
    "review_questions",
    "opportunity_costs",
    "blocked_by",
}

DICT_FIELD_HINTS = {
    "entities",
    "commercial_terms",
    "dates",
    "quantities",
    "checks",
    "constraints",
    "metrics",
    "attributes",
    "compliance",
}

TRUE_ESCALATION_KEYS = {"escalation_needed", "human_review_required"}
CAUSAL_TERMS = {
    "because",
    "therefore",
    "so",
    "due",
    "driven",
    "causes",
    "causal",
    "pull-forward",
    "cannibalization",
    "stockout-censored",
    "opportunity cost",
    "tradeoff",
    "risk-adjusted",
    "margin",
    "constraint",
}
PREMISE_CHALLENGE_TERMS = {
    "reject",
    "decline",
    "do not",
    "don't",
    "avoid",
    "block",
    "hold",
    "cap",
    "condition",
    "resolve",
    "not approve",
    "not feasible",
    "escalate",
    "human review",
    "review required",
}
RECOMMENDATION_TERMS = {
    "recommend",
    "approve",
    "buy",
    "chase",
    "proceed",
    "allocate",
    "promote",
    "transfer",
    "markdown",
    "match",
}


def pack_paths(pack_root: str | Path) -> list[Path]:
    return sorted(Path(pack_root).glob("*/pack.json"))


def load_packs(pack_root: str | Path) -> list[dict[str, Any]]:
    return [load_json(path) for path in pack_paths(pack_root)]


def source_text(item: dict[str, Any]) -> str:
    parts: list[str] = []

    def walk(value: Any) -> None:
        if isinstance(value, dict):
            for key, nested in value.items():
                if isinstance(nested, (dict, list)):
                    walk(nested)
                else:
                    parts.append(f"{key}: {nested}")
        elif isinstance(value, list):
            for nested in value:
                walk(nested)
        elif value is not None:
            parts.append(str(value))

    walk(item.get("input", {}))
    return " ".join(parts)


def compact_sentences(text: str, limit: int = 4) -> list[str]:
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    return [sentence.strip() for sentence in sentences if sentence.strip()][:limit]


def extracted_values(text: str) -> list[str]:
    values: list[str] = []
    for pattern in (MONEY_RE, PERCENT_RE, DATE_RE, SKU_RE):
        values.extend(match.group(0) for match in pattern.finditer(text))
    values.extend(match.group(0) for match in NUMBER_RE.finditer(text))
    return list(dict.fromkeys(values))


def risk_phrases(text: str) -> list[str]:
    lowered = text.lower()
    signals = []
    checks = (
        ("compliance", ("pending", "certificate", "compliance", "ul ", "fcc", "barcode")),
        ("safety or capacity", ("fire", "safety", "capacity", "blocked", "aisle", "labor")),
        ("margin or funding", ("margin", "funding", "cost", "below", "discount")),
        ("timing", ("delay", "deadline", "lead time", "arrive", "receipt", "after")),
        ("conflict", ("conflict", "versus", "either", "differs", "not divisible")),
        ("quality", ("return", "crack", "quality", "defect", "lot")),
    )
    for label, keywords in checks:
        if any(keyword in lowered for keyword in keywords):
            signals.append(label)
    return signals


def needs_escalation(item: dict[str, Any], text: str) -> bool:
    lowered = text.lower()
    if item.get("error_downside_band") in {"high", "severe"}:
        return True
    return any(
        keyword in lowered
        for keyword in (
            "pending",
            "fire",
            "compliance",
            "conflict",
            "exceeds",
            "below",
            "not divisible",
            "human review",
            "leadership",
            "customer promise",
            "safety",
        )
    )


def default_field_value(field: str, text: str, item: dict[str, Any]) -> Any:
    if field in TRUE_ESCALATION_KEYS:
        return needs_escalation(item, text)
    if field in DICT_FIELD_HINTS:
        return {}
    if field in LIST_FIELD_HINTS or field.endswith("s"):
        return []
    if field in {"confidence"}:
        return "low"
    if field in {"priority"}:
        return "high" if item.get("error_downside_band") in {"high", "severe"} else "medium"
    if field in {"summary"}:
        sentences = compact_sentences(text, 1)
        return sentences[0] if sentences else ""
    if field.endswith("_reason") or field in {"escalation_reason"}:
        return "Escalation suggested by deterministic risk signals." if needs_escalation(item, text) else None
    return ""


def response_for_required_fields(pack: dict[str, Any], item: dict[str, Any], *, baseline_id: str) -> dict[str, Any]:
    text = source_text(item)
    content = {
        field: default_field_value(field, text, item)
        for field in pack["output_contract"]["required_fields"]
    }
    content["source_excerpt"] = text
    content["baseline_id"] = baseline_id
    return content


def source_echo_response(pack: dict[str, Any], item: dict[str, Any]) -> dict[str, Any]:
    text = source_text(item)
    content = response_for_required_fields(pack, item, baseline_id="baseline/source_echo")
    if "summary" in content:
        content["summary"] = compact_sentences(text, 1)[0] if compact_sentences(text, 1) else text[:240]
    if "key_points" in content:
        content["key_points"] = compact_sentences(text, 4)
    if "numbers_preserved" in content:
        content["numbers_preserved"] = extracted_values(text)
    if "risks_or_caveats" in content:
        content["risks_or_caveats"] = risk_phrases(text)
    return content


def keyword_guardrail_response(pack: dict[str, Any], item: dict[str, Any]) -> dict[str, Any]:
    text = source_text(item)
    lowered = text.lower()
    content = response_for_required_fields(pack, item, baseline_id="baseline/keyword_guardrail")
    values = extracted_values(text)
    risks = risk_phrases(text)
    escalation = needs_escalation(item, text)
    segment = pack["task_segment"]

    if "summary" in content:
        content["summary"] = compact_sentences(text, 1)[0] if compact_sentences(text, 1) else text[:240]
    if "key_points" in content:
        content["key_points"] = compact_sentences(text, 4)
    if "numbers_preserved" in content:
        content["numbers_preserved"] = values
    if "risks_or_caveats" in content:
        content["risks_or_caveats"] = risks
    if "escalation_needed" in content:
        content["escalation_needed"] = escalation
    if "human_review_required" in content:
        content["human_review_required"] = escalation
    if "escalation_reason" in content:
        content["escalation_reason"] = "; ".join(risks) if escalation and risks else (None if not escalation else "High-downside retail exception.")

    if segment == "structured_extraction":
        content.update(
            {
                "record_type": item["retail_function"],
                "entities": {"skus": SKU_RE.findall(text)},
                "commercial_terms": {"money_values": MONEY_RE.findall(text), "numbers": NUMBER_RE.findall(text)},
                "dates": DATE_RE.findall(text),
                "quantities": NUMBER_RE.findall(text),
                "conflicts": ["potential conflicting values"] if any(word in lowered for word in ("conflict", "differs", "either")) else [],
                "missing_required_fields": ["compliance_or_confirmation"] if "pending" in lowered or "missing" in lowered else [],
            }
        )
    elif segment == "constraint_checking":
        fail = any(word in lowered for word in ("exceeds", "below", "pending", "not divisible", "only", "fire", "mismatch"))
        content.update(
            {
                "constraint_status": "fail" if fail else "needs_review",
                "checks": {check: "reviewed" for check in item.get("deterministic_checks", [])},
                "blocking_constraints": risks if fail else [],
                "non_blocking_warnings": [] if fail else risks,
            }
        )
    elif segment == "routine_planning_recommendation":
        content.update(
            {
                "recommended_action": "proceed with bounded routine action if deterministic checks pass",
                "quantity_or_depth": values[:3],
                "constraints_checked": item.get("deterministic_checks", []),
                "confidence": "medium",
                "next_read": "review the next operational read before scaling",
            }
        )
    elif segment == "pricing_promotion":
        content.update(
            {
                "decision": "avoid blanket action; use targeted or guardrailed promotion",
                "recommended_price_or_depth": values[:3],
                "margin_read": "margin or funding needs deterministic verification" if "margin" in lowered or "fund" in lowered else "not available",
                "demand_read": "demand signal needs incrementality review",
                "risk_controls": risks or item.get("deterministic_checks", []),
            }
        )
    elif segment == "ambiguous_planning_judgment":
        content.update(
            {
                "decision": "condition or reject irreversible action pending better evidence",
                "recommended_action": "use a bounded test or escalate before commitment",
                "evidence_trusted": values[:4],
                "evidence_discounted": risks,
                "constraints": item.get("deterministic_checks", []),
                "uncertainty": "medium_low" if escalation else "medium",
            }
        )
    elif segment == "portfolio_tradeoff":
        content.update(
            {
                "decision_frame": "portfolio tradeoff requiring opportunity-cost review",
                "recommended_allocation": "do not fully commit until constraints and tradeoffs are reviewed",
                "opportunity_costs": risks,
                "constraints": item.get("deterministic_checks", []),
                "human_review_required": True,
                "review_questions": item.get("escalation_triggers", []),
            }
        )
    elif segment == "operational_triage":
        content.update(
            {
                "priority": "high" if escalation else "medium",
                "owner": "operations or compliance owner" if escalation else "planning owner",
                "triage_decision": "block unsafe execution and route for review" if escalation else "eligible for routine review",
                "blocked_by": risks,
                "safe_next_step": "route to owner with deterministic checks before execution",
                "customer_or_store_risk": "; ".join(risks) if risks else "not material",
            }
        )

    return content


def generic_consultant_response(pack: dict[str, Any], item: dict[str, Any]) -> dict[str, Any]:
    text = source_text(item)
    content = response_for_required_fields(pack, item, baseline_id="baseline/generic_consultant")
    generic = (
        "Review the commercial context, balance risk and upside, align stakeholders, "
        "monitor results, and revisit the decision after the next read."
    )
    for field in pack["output_contract"]["required_fields"]:
        if field in TRUE_ESCALATION_KEYS:
            content[field] = False
        elif isinstance(content.get(field), list):
            content[field] = ["review business impact", "monitor risk", "align stakeholders"]
        elif isinstance(content.get(field), dict):
            content[field] = {"generic_review": "required"}
        elif field == "confidence":
            content[field] = "medium"
        else:
            content[field] = generic
    content["source_excerpt"] = text
    return content


def always_escalate_response(pack: dict[str, Any], item: dict[str, Any]) -> dict[str, Any]:
    text = source_text(item)
    content = response_for_required_fields(pack, item, baseline_id="baseline/always_escalate")
    for field in pack["output_contract"]["required_fields"]:
        if field in TRUE_ESCALATION_KEYS:
            content[field] = True
        elif isinstance(content.get(field), list):
            content[field] = ["escalate to human reviewer before action"]
        elif isinstance(content.get(field), dict):
            content[field] = {"review": "human approval required"}
        elif field == "priority":
            content[field] = "high"
        elif field == "confidence":
            content[field] = "low"
        else:
            content[field] = "Do not decide automatically; escalate for human review."
    content["source_excerpt"] = text
    return content


def always_buy_chase_response(pack: dict[str, Any], item: dict[str, Any]) -> dict[str, Any]:
    text = source_text(item)
    values = extracted_values(text)
    content = response_for_required_fields(pack, item, baseline_id="baseline/always_buy_chase")
    for field in pack["output_contract"]["required_fields"]:
        if field in TRUE_ESCALATION_KEYS:
            content[field] = False
        elif isinstance(content.get(field), list):
            content[field] = values[:4] or ["available upside supports action"]
        elif isinstance(content.get(field), dict):
            content[field] = {"action": "approve full buy or chase"}
        elif field == "confidence":
            content[field] = "high"
        elif field == "priority":
            content[field] = "medium"
        else:
            content[field] = "Approve the buy, chase, promotion, or allocation to capture upside."
    content["source_excerpt"] = text
    return content


def always_conservative_response(pack: dict[str, Any], item: dict[str, Any]) -> dict[str, Any]:
    text = source_text(item)
    content = response_for_required_fields(pack, item, baseline_id="baseline/always_conservative")
    for field in pack["output_contract"]["required_fields"]:
        if field in TRUE_ESCALATION_KEYS:
            content[field] = False
        elif isinstance(content.get(field), list):
            content[field] = ["avoid action", "wait for cleaner data"]
        elif isinstance(content.get(field), dict):
            content[field] = {"action": "no action"}
        elif field == "confidence":
            content[field] = "low"
        elif field == "priority":
            content[field] = "low"
        else:
            content[field] = "Take no action and wait for a cleaner read."
    content["source_excerpt"] = text
    return content


def arithmetic_only_response(pack: dict[str, Any], item: dict[str, Any]) -> dict[str, Any]:
    text = source_text(item)
    values = extracted_values(text)
    content = response_for_required_fields(pack, item, baseline_id="baseline/arithmetic_only")
    for field in pack["output_contract"]["required_fields"]:
        if field in TRUE_ESCALATION_KEYS:
            content[field] = needs_escalation(item, text)
        elif isinstance(content.get(field), list):
            content[field] = values[:6]
        elif isinstance(content.get(field), dict):
            content[field] = {"extracted_values": values[:12]}
        elif field == "confidence":
            content[field] = "not_assessed"
        elif field == "priority":
            content[field] = "not_assessed"
        else:
            content[field] = "Arithmetic-only baseline: extracted numeric values without causal judgment."
    content["source_excerpt"] = text
    return content


def baseline_response(pack: dict[str, Any], item: dict[str, Any], baseline_id: str) -> dict[str, Any]:
    if baseline_id == "baseline/source_echo":
        return source_echo_response(pack, item)
    if baseline_id == "baseline/keyword_guardrail":
        return keyword_guardrail_response(pack, item)
    if baseline_id == "baseline/generic_consultant":
        return generic_consultant_response(pack, item)
    if baseline_id == "baseline/always_escalate":
        return always_escalate_response(pack, item)
    if baseline_id == "baseline/always_buy_chase":
        return always_buy_chase_response(pack, item)
    if baseline_id == "baseline/always_conservative":
        return always_conservative_response(pack, item)
    if baseline_id == "baseline/arithmetic_only":
        return arithmetic_only_response(pack, item)
    raise ValueError(f"unknown baseline id: {baseline_id}")


def build_baseline_responses(pack_root: str | Path, baselines: tuple[str, ...] = BASELINE_IDS) -> dict[str, Any]:
    packs = load_packs(pack_root)
    models: dict[str, Any] = {}
    for baseline_id in baselines:
        pack_outputs: dict[str, Any] = {}
        for pack in packs:
            item_outputs = {}
            for item in pack["items"]:
                content = baseline_response(pack, item, baseline_id)
                item_outputs[item["id"]] = {
                    "content": content,
                    "raw_text": json.dumps(content, sort_keys=True),
                }
            pack_outputs[pack["id"]] = {
                "task_segment": pack["task_segment"],
                "items": item_outputs,
            }
        models[baseline_id] = {
            "source": "deterministic_local_baseline",
            "packs": pack_outputs,
        }
    return {
        "version": "0.1",
        "run_type": "segment_eval_pack_responses",
        "models": models,
    }


def normalize(value: str) -> str:
    return " ".join(TOKEN_RE.findall(value.lower().replace(",", "")))


def tokens(value: str) -> list[str]:
    return TOKEN_RE.findall(value.lower().replace(",", ""))


def phrase_matches(needle: str, haystack: str) -> bool:
    norm_needle = normalize(needle)
    norm_haystack = normalize(haystack)
    if not norm_needle:
        return False
    if norm_needle in norm_haystack:
        return True

    needle_tokens = tokens(needle)
    haystack_tokens = set(tokens(haystack))
    if not needle_tokens:
        return False
    numeric_tokens = [token for token in needle_tokens if any(char.isdigit() for char in token)]
    if numeric_tokens and not all(token in haystack_tokens for token in numeric_tokens):
        return False
    hits = sum(1 for token in needle_tokens if token in haystack_tokens)
    return hits / len(needle_tokens) >= 0.8


def strip_scoring_metadata(response: Any) -> Any:
    if isinstance(response, dict):
        return {
            key: strip_scoring_metadata(value)
            for key, value in response.items()
            if key not in SCORING_METADATA_KEYS
        }
    if isinstance(response, list):
        return [strip_scoring_metadata(value) for value in response]
    return response


def response_to_text(response: Any) -> str:
    if isinstance(response, str):
        return response
    return json.dumps(strip_scoring_metadata(response), sort_keys=True)


def baseline_id_for(response: Any) -> str | None:
    if isinstance(response, dict) and isinstance(response.get("baseline_id"), str):
        return response["baseline_id"]
    return None


def source_overlap_ratio(response_text: str, item: dict[str, Any]) -> float:
    response_tokens = [token for token in tokens(response_text) if len(token) > 2]
    if not response_tokens:
        return 0.0
    source_tokens = set(token for token in tokens(source_text(item)) if len(token) > 2)
    if not source_tokens:
        return 0.0
    return sum(1 for token in response_tokens if token in source_tokens) / len(response_tokens)


def contains_any(text: str, terms: set[str]) -> bool:
    lowered = text.lower()
    return any(term in lowered for term in terms)


def requires_premise_challenge(item: dict[str, Any]) -> bool:
    joined = " ".join(item.get("must_include", []) + item.get("must_not_include", [])).lower()
    return any(
        phrase in joined
        for phrase in (
            "reject",
            "do not",
            "avoid",
            "block",
            "condition",
            "resolve",
            "not approve",
            "ignore",
            "approve",
            "blanket",
            "treat",
            "claim",
        )
    )


def has_recommendation(text: str) -> bool:
    return contains_any(text, RECOMMENDATION_TERMS)


def anti_echo_assessment(
    pack: dict[str, Any],
    item: dict[str, Any],
    response: Any,
    text: str,
    *,
    include_ratio: float,
    avoid_ratio: float,
    escalate_ratio: float,
) -> dict[str, Any]:
    baseline_id = baseline_id_for(response)
    overlap = source_overlap_ratio(text, item)
    has_causal_link = contains_any(text, CAUSAL_TERMS)
    challenge_required = requires_premise_challenge(item)
    has_challenge = contains_any(text, PREMISE_CHALLENGE_TERMS)
    expected_escalate = expected_escalation(item)
    actual_escalate = actual_escalation(response)
    caps: list[float] = []
    penalties: list[dict[str, Any]] = []

    def add_cap(reason: str, cap: float) -> None:
        caps.append(cap)
        penalties.append({"type": "cap", "reason": reason, "cap": cap})

    def add_penalty(reason: str, points: float) -> None:
        penalties.append({"type": "penalty", "reason": reason, "points": points})

    if baseline_id == "baseline/source_echo" or (overlap >= 0.86 and not has_causal_link and not has_challenge):
        add_cap("source echo without causal decision logic", 4.0)

    if baseline_id == "baseline/keyword_guardrail" or (
        include_ratio >= 0.65 and not has_causal_link and challenge_required and not has_challenge
    ):
        add_cap("keyword coverage without causal or premise-challenge reasoning", 5.0)

    if baseline_id == "baseline/generic_consultant":
        add_cap("generic answer without scenario-specific retail decision", 4.0)
    elif baseline_id == "baseline/always_escalate":
        add_cap("always-escalate policy avoids decision quality", 5.5)
    elif baseline_id == "baseline/always_buy_chase":
        add_cap("always-buy/chase policy ignores downside and constraints", 4.5)
    elif baseline_id == "baseline/always_conservative":
        add_cap("always-conservative policy ignores upside and actionability", 4.5)
    elif baseline_id == "baseline/arithmetic_only":
        add_cap("arithmetic-only answer lacks causal and routing judgment", 5.0)

    if expected_escalate is True and actual_escalate is not True:
        add_cap("missing required escalation on high-downside item", 6.0)
    if challenge_required and not has_challenge and pack["task_segment"] not in {"structured_extraction"}:
        add_penalty("missing required premise challenge or conditional decision", 1.0)
    if has_recommendation(text) and include_ratio < 0.35 and not has_causal_link:
        add_penalty("unsupported recommendation with weak evidence linkage", 1.0)
    if avoid_ratio < 1.0 and not has_challenge:
        add_penalty("violates forbidden action without correcting the premise", 0.75)

    return {
        "baseline_id": baseline_id,
        "source_overlap_ratio": round(overlap, 4),
        "has_causal_link": has_causal_link,
        "premise_challenge_required": challenge_required,
        "has_premise_challenge": has_challenge,
        "penalties": penalties,
        "cap": min(caps) if caps else None,
    }


def apply_anti_echo_adjustment(total: float, assessment: dict[str, Any]) -> tuple[float, float]:
    adjusted = total
    penalty_points = sum(float(penalty.get("points", 0)) for penalty in assessment.get("penalties", []) if penalty.get("type") == "penalty")
    adjusted = max(0.0, adjusted - penalty_points)
    cap = assessment.get("cap")
    if cap is not None:
        adjusted = min(adjusted, float(cap))
    return round(adjusted, 4), round(total - adjusted, 4)


def required_field_score(pack: dict[str, Any], response: Any) -> float:
    if not isinstance(response, dict):
        return 0.0
    required = pack["output_contract"]["required_fields"]
    if not required:
        return 1.0
    return sum(1 for field in required if field in response) / len(required)


def expected_escalation(item: dict[str, Any]) -> bool | None:
    expected = item.get("expected_output", {})
    for key in TRUE_ESCALATION_KEYS:
        value = expected.get(key)
        if isinstance(value, bool):
            return value
    return None


def actual_escalation(response: Any) -> bool | None:
    if not isinstance(response, dict):
        return None
    for key in TRUE_ESCALATION_KEYS:
        value = response.get(key)
        if isinstance(value, bool):
            return value
    return None


def escalation_score(item: dict[str, Any], response: Any) -> float:
    expected = expected_escalation(item)
    actual = actual_escalation(response)
    if expected is None:
        return 1.0 if actual is not None else 0.5
    return 1.0 if actual is expected else 0.0


def dimension_ratio(dimension: str, include_ratio: float, avoid_ratio: float, schema_ratio: float, escalate_ratio: float) -> float:
    if any(key in dimension for key in ("schema", "format")):
        return schema_ratio
    if any(key in dimension for key in ("escalation", "human_review", "safety", "calibration")):
        return (0.35 * include_ratio) + (0.3 * avoid_ratio) + (0.35 * escalate_ratio)
    if any(key in dimension for key in ("field", "numeric", "arithmetic", "margin", "normalization", "constraint")):
        return (0.8 * include_ratio) + (0.2 * avoid_ratio)
    if any(key in dimension for key in ("action", "recommendation", "decision", "promotion", "triage", "routing")):
        return (0.55 * include_ratio) + (0.25 * avoid_ratio) + (0.2 * escalate_ratio)
    if any(key in dimension for key in ("evidence", "causal", "portfolio", "opportunity")):
        return (0.65 * include_ratio) + (0.25 * avoid_ratio) + (0.1 * escalate_ratio)
    return (0.6 * include_ratio) + (0.25 * avoid_ratio) + (0.15 * schema_ratio)


def score_item(pack: dict[str, Any], item: dict[str, Any], response: Any) -> dict[str, Any]:
    text = response_to_text(response)
    include_hits = [phrase for phrase in item.get("must_include", []) if phrase_matches(phrase, text)]
    include_misses = [phrase for phrase in item.get("must_include", []) if phrase not in include_hits]
    must_not_violations = [phrase for phrase in item.get("must_not_include", []) if phrase_matches(phrase, text)]

    include_ratio = len(include_hits) / len(item.get("must_include", []) or [1])
    avoid_ratio = 1 - (len(must_not_violations) / len(item.get("must_not_include", []) or [1]))
    schema_ratio = required_field_score(pack, response)
    escalate_ratio = escalation_score(item, response)

    dimensions: dict[str, Any] = {}
    total = 0.0
    for dimension, spec in pack["scoring"]["dimensions"].items():
        max_points = float(spec["points"])
        ratio = dimension_ratio(dimension, include_ratio, avoid_ratio, schema_ratio, escalate_ratio)
        score = round(max_points * ratio, 4)
        total += score
        dimensions[dimension] = {
            "score": score,
            "max": max_points,
            "ratio": round(ratio, 4),
        }

    raw_total = round(total, 4)
    anti_echo = anti_echo_assessment(
        pack,
        item,
        response,
        text,
        include_ratio=include_ratio,
        avoid_ratio=avoid_ratio,
        escalate_ratio=escalate_ratio,
    )
    adjusted_total, penalty_points = apply_anti_echo_adjustment(raw_total, anti_echo)
    return {
        "total": adjusted_total,
        "raw_total": raw_total,
        "max": float(pack["scoring"]["total_points_per_item"]),
        "passes_item_floor": adjusted_total >= float(pack["quality_floor"]["minimum_item_score"]),
        "dimensions": dimensions,
        "signals": {
            "must_include_hits": include_hits,
            "must_include_misses": include_misses,
            "must_not_violations": must_not_violations,
            "required_field_score": round(schema_ratio, 4),
            "escalation_score": round(escalate_ratio, 4),
            "anti_echo": anti_echo,
            "anti_echo_penalty_points": penalty_points,
        },
    }


def score_responses(pack_root: str | Path, responses_doc: dict[str, Any]) -> dict[str, Any]:
    packs_by_id = {pack["id"]: pack for pack in load_packs(pack_root)}
    scored_models: dict[str, Any] = {}
    total_available_items = sum(len(pack.get("items", [])) for pack in packs_by_id.values())

    for model_id, model_record in responses_doc.get("models", {}).items():
        scored_packs: dict[str, Any] = {}
        all_totals: list[float] = []
        attempted_total = 0
        failed_total = 0
        for pack_id, pack in packs_by_id.items():
            response_pack = model_record.get("packs", {}).get(pack_id, {})
            response_items = response_pack.get("items", {})
            attempted_count = len(response_items)
            failed_count = sum(
                1
                for record in response_items.values()
                if record.get("ok") is False and not record.get("parse_error")
            )
            item_scores = {}
            for item in pack["items"]:
                if item["id"] not in response_items:
                    continue
                item_record = response_items[item["id"]]
                if item_record.get("ok") is False and not item_record.get("parse_error"):
                    continue
                response = item_record.get("content", {})
                score = score_item(pack, item, response)
                item_scores[item["id"]] = score
                all_totals.append(score["total"])

            attempted_total += attempted_count
            failed_total += failed_count
            totals = [score["total"] for score in item_scores.values()]
            pass_count = sum(1 for score in item_scores.values() if score["passes_item_floor"])
            average = round(mean(totals), 4) if totals else 0
            available_item_count = len(pack["items"])
            scored_packs[pack_id] = {
                "task_segment": pack["task_segment"],
                "item_count": len(item_scores),
                "attempted_item_count": attempted_count,
                "failed_item_count": failed_count,
                "available_item_count": available_item_count,
                "average_score": average,
                "minimum_average_score": pack["quality_floor"]["minimum_average_score"],
                "pass_count": pass_count,
                "must_pass_items": pack["quality_floor"]["must_pass_items"],
                "passes_pack_floor": (
                    len(item_scores) == available_item_count
                    and average >= float(pack["quality_floor"]["minimum_average_score"])
                    and pass_count >= int(pack["quality_floor"]["must_pass_items"])
                ),
                "item_scores": item_scores,
            }

        scored_models[model_id] = {
            "source": model_record.get("source"),
            "overall_average": round(mean(all_totals), 4) if all_totals else 0,
            "total_items": len(all_totals),
            "attempted_items": attempted_total,
            "failed_items": failed_total,
            "available_items": total_available_items,
            "packs": scored_packs,
        }

    return {
        "version": "0.1",
        "methodology": "Automated deterministic contract scoring over must_include, must_not_include, output contract fields, escalation agreement, and anti-echo penalties. This is a bootstrap scorer for baselines and model-run triage, not a substitute for final human calibration.",
        "models": scored_models,
    }


def scores_markdown(scores_doc: dict[str, Any]) -> str:
    lines = [
        "# Segment Eval Pack Scores",
        "",
        scores_doc.get("methodology", ""),
        "",
        "| Model | Overall Avg | Scored Coverage | Attempted Calls | Provider Failures | Packs Passing |",
        "| :--- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for model_id, model in scores_doc.get("models", {}).items():
        packs = model.get("packs", {})
        pack_passes = sum(1 for pack in packs.values() if pack.get("passes_pack_floor"))
        lines.append(
            f"| `{model_id}` | {model['overall_average']}/10 | "
            f"{model['total_items']}/{model.get('available_items', model['total_items'])} | "
            f"{model.get('attempted_items', model['total_items'])} | "
            f"{model.get('failed_items', 0)} | {pack_passes}/{len(packs)} |"
        )

    lines.extend(["", "## Segment Detail", ""])
    for model_id, model in scores_doc.get("models", {}).items():
        lines.extend(
            [
                f"### `{model_id}`",
                "",
                "| Segment | Avg | Scored Coverage | Attempted Calls | Provider Failures | Item Passes | Pack Pass |",
                "| :--- | ---: | ---: | ---: | ---: | ---: | :--- |",
            ]
        )
        for pack in sorted(model.get("packs", {}).values(), key=lambda row: row["task_segment"]):
            pass_label = "Yes" if pack["passes_pack_floor"] else "No"
            lines.append(
                f"| `{pack['task_segment']}` | {pack['average_score']}/10 | "
                f"{pack['item_count']}/{pack.get('available_item_count', pack['item_count'])} | "
                f"{pack.get('attempted_item_count', pack['item_count'])} | "
                f"{pack.get('failed_item_count', 0)} | "
                f"{pack['pass_count']}/{pack['item_count']} | {pass_label} |"
            )
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write_scores_markdown(path: str | Path, scores_doc: dict[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(scores_markdown(scores_doc))


def robustness_markdown(scores_doc: dict[str, Any]) -> str:
    lines = [
        "# Scorer Robustness Check",
        "",
        "This report tracks whether adversarial deterministic baselines still receive inflated scores after anti-echo scorer hardening.",
        "",
        "| Baseline | Pre anti-echo avg | Current avg | Threshold | Status |",
        "| :--- | ---: | ---: | ---: | :--- |",
    ]
    for baseline_id in BASELINE_IDS:
        model = scores_doc.get("models", {}).get(baseline_id, {})
        current = float(model.get("overall_average", 0))
        previous = PRE_ANTI_ECHO_BASELINE_AVERAGES.get(baseline_id)
        threshold = ADVERSARIAL_BASELINE_THRESHOLDS.get(baseline_id)
        if threshold is None:
            status = "Diagnostic only"
            threshold_label = "n/a"
        else:
            status = "Pass" if current <= threshold else "Fail"
            threshold_label = f"{threshold:.1f}"
        previous_label = f"{previous:.4f}" if previous is not None else "n/a"
        lines.append(f"| `{baseline_id}` | {previous_label} | {current:.4f} | {threshold_label} | {status} |")

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- `baseline/source_echo` should no longer score like a competent planning answer just because source facts are present.",
            "- `baseline/keyword_guardrail` should no longer pass by naming guardrail terms without causal or premise-challenge reasoning.",
            "- The other adversarial baselines are diagnostic probes for generic, over-escalating, over-aggressive, over-conservative, and arithmetic-only behavior.",
            "- Passing this check does not make the automated scorer human-calibrated; it only reduces the most visible deterministic baseline inflation.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def write_robustness_markdown(path: str | Path, scores_doc: dict[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(robustness_markdown(scores_doc))


def run_baselines(
    pack_root: str | Path,
    responses_output: str | Path,
    scores_output: str | Path,
    summary_output: str | Path,
    robustness_output: str | Path | None = None,
) -> dict[str, Any]:
    responses = build_baseline_responses(pack_root)
    scores = score_responses(pack_root, responses)
    write_json(responses_output, responses)
    write_json(scores_output, scores)
    write_scores_markdown(summary_output, scores)
    if robustness_output:
        write_robustness_markdown(robustness_output, scores)
    return scores
