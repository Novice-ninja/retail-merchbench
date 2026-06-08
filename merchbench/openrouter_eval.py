from __future__ import annotations

import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

from merchbench.eval_packs import load_packs, score_responses, write_scores_markdown
from merchbench.io import write_json


DEFAULT_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODELS = [
    "google/gemma-4-31b-it:free",
    "openai/gpt-oss-120b:free",
]
RETRYABLE_STATUS_CODES = {408, 409, 425, 429, 500, 502, 503, 504}
JSON_FENCE_RE = re.compile(r"^```(?:json)?\s*(.*?)\s*```$", re.S)

SYSTEM_PROMPT = """You are completing a MerchBench retail eval-pack task.
Use only the supplied input. Return only valid JSON matching the requested fields.
Do not include markdown, commentary, hidden reasoning, or extra prose."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_env(path: str | Path) -> None:
    env_path = Path(path)
    if not env_path.exists():
        return
    for raw_line in env_path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def base_url() -> str:
    return os.getenv("OPENROUTER_BASE_URL", DEFAULT_BASE_URL).rstrip("/")


def api_headers() -> dict[str, str]:
    key = os.getenv("OPENROUTER_API_KEY")
    if not key:
        raise RuntimeError("OPENROUTER_API_KEY is missing. Add it to .env.local or the environment.")
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }
    referer = os.getenv("OPENROUTER_HTTP_REFERER")
    title = os.getenv("OPENROUTER_APP_TITLE", "MerchBench")
    if referer:
        headers["HTTP-Referer"] = referer
    if title:
        headers["X-Title"] = title
    return headers


def filter_packs(
    packs: list[dict[str, Any]],
    *,
    segments: list[str] | None = None,
    pack_ids: list[str] | None = None,
) -> list[dict[str, Any]]:
    selected = packs
    if segments:
        allowed_segments = set(segments)
        selected = [pack for pack in selected if pack["task_segment"] in allowed_segments]
    if pack_ids:
        allowed_pack_ids = set(pack_ids)
        selected = [pack for pack in selected if pack["id"] in allowed_pack_ids]
    return selected


def iter_tasks(
    packs: list[dict[str, Any]],
    *,
    max_items: int | None = None,
    items_per_pack: int | None = None,
) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    tasks: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for pack in packs:
        pack_count = 0
        for item in pack.get("items", []):
            if items_per_pack is not None and pack_count >= items_per_pack:
                break
            tasks.append((pack, item))
            pack_count += 1
            if max_items is not None and len(tasks) >= max_items:
                return tasks
    return tasks


def prompt_for_item(pack: dict[str, Any], item: dict[str, Any]) -> str:
    visible = {
        "task_segment": pack["task_segment"],
        "strategy_under_test": pack["recommended_strategy_under_test"],
        "output_contract": pack["output_contract"],
        "item": {
            "id": item["id"],
            "title": item["title"],
            "difficulty": item["difficulty"],
            "retail_function": item["retail_function"],
            "category": item["category"],
            "decision_value_band": item["decision_value_band"],
            "error_downside_band": item["error_downside_band"],
            "input": item["input"],
            "question": item["question"],
        },
    }
    return (
        "Complete the retail eval task below.\n"
        "Return exactly one JSON object with all required fields from output_contract.required_fields.\n"
        "Use null for unknown scalar values, [] for unknown arrays, and {} for unknown objects.\n\n"
        f"{json.dumps(visible, indent=2)}"
    )


def should_retry(status_code: int | None) -> bool:
    return status_code is None or status_code in RETRYABLE_STATUS_CODES


def text_indicates_daily_free_quota(text: str | None) -> bool:
    if not text:
        return False
    return "free-models-per-day" in text.lower()


def result_indicates_daily_free_quota(result: dict[str, Any]) -> bool:
    if result.get("quota_exhausted") is True:
        return True
    return text_indicates_daily_free_quota(result.get("error")) or text_indicates_daily_free_quota(result.get("raw_text"))


def post_with_retries(
    payload: dict[str, Any],
    *,
    timeout: int,
    max_retries: int,
    retry_backoff: float,
) -> tuple[requests.Response | None, list[dict[str, Any]], str | None]:
    attempts: list[dict[str, Any]] = []
    url = f"{base_url()}/chat/completions"
    headers = api_headers()
    for attempt in range(1, max_retries + 2):
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=timeout)
        except requests.RequestException as exc:
            attempts.append(
                {
                    "attempt": attempt,
                    "ok": False,
                    "status_code": None,
                    "retryable": True,
                    "error": repr(exc),
                    "timestamp_utc": utc_now(),
                }
            )
            if attempt > max_retries:
                return None, attempts, repr(exc)
        else:
            quota_exhausted = text_indicates_daily_free_quota(response.text)
            retryable = should_retry(response.status_code) and not quota_exhausted
            attempts.append(
                {
                    "attempt": attempt,
                    "ok": response.status_code < 400,
                    "status_code": response.status_code,
                    "retryable": retryable,
                    "timestamp_utc": utc_now(),
                }
            )
            if response.status_code < 400:
                return response, attempts, None
            if attempt > max_retries or not retryable:
                return response, attempts, response.text[:2000]

        time.sleep(retry_backoff * attempt)

    return None, attempts, "retry loop exited unexpectedly"


def strip_json_fence(raw_text: str) -> str:
    text = raw_text.strip()
    match = JSON_FENCE_RE.match(text)
    if match:
        return match.group(1).strip()
    return text


def extract_embedded_json(text: str) -> Any | None:
    decoder = json.JSONDecoder()
    for start in (index for index, char in enumerate(text) if char == "{"):
        try:
            value, _ = decoder.raw_decode(text[start:])
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            return value
    return None


def parse_json_response(raw_text: str) -> tuple[Any, str | None]:
    text = strip_json_fence(raw_text)
    try:
        return json.loads(text), None
    except json.JSONDecodeError as exc:
        embedded = extract_embedded_json(text)
        if embedded is not None:
            return embedded, None
        return {"raw_response": raw_text, "parse_error": str(exc)}, str(exc)


def run_item(
    *,
    model: str,
    pack: dict[str, Any],
    item: dict[str, Any],
    timeout: int,
    max_retries: int,
    retry_backoff: float,
    temperature: float,
    max_tokens: int,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt_for_item(pack, item)},
        ],
        "temperature": temperature,
    }
    if max_tokens > 0:
        payload["max_tokens"] = max_tokens

    response, attempts, error = post_with_retries(
        payload,
        timeout=timeout,
        max_retries=max_retries,
        retry_backoff=retry_backoff,
    )
    if response is None:
        return {
            "ok": False,
            "content": {"error": error},
            "raw_text": "",
            "error": error,
            "attempts": attempts,
            "completed_at_utc": utc_now(),
        }
    if response.status_code >= 400:
        return {
            "ok": False,
            "status_code": response.status_code,
            "content": {"error": error or response.text[:2000]},
            "raw_text": response.text[:4000],
            "error": error or response.text[:2000],
            "quota_exhausted": text_indicates_daily_free_quota(error) or text_indicates_daily_free_quota(response.text),
            "attempts": attempts,
            "completed_at_utc": utc_now(),
        }

    try:
        data = response.json()
        raw_text = data["choices"][0]["message"]["content"].strip()
    except (ValueError, KeyError, IndexError) as exc:
        return {
            "ok": False,
            "status_code": response.status_code,
            "content": {"error": f"Malformed OpenRouter response: {exc!r}"},
            "raw_text": response.text[:4000],
            "error": f"Malformed OpenRouter response: {exc!r}",
            "attempts": attempts,
            "completed_at_utc": utc_now(),
        }

    content, parse_error = parse_json_response(raw_text)
    return {
        "ok": parse_error is None,
        "status_code": response.status_code,
        "content": content,
        "raw_text": raw_text,
        "parse_error": parse_error,
        "usage": data.get("usage", {}),
        "raw_model": data.get("model"),
        "attempts": attempts,
        "completed_at_utc": utc_now(),
    }


def empty_responses_doc(models: list[str]) -> dict[str, Any]:
    return {
        "version": "0.1",
        "run_type": "segment_eval_pack_responses",
        "provider": "openrouter",
        "started_at_utc": utc_now(),
        "models": {
            model: {
                "source": "openrouter",
                "packs": {},
            }
            for model in models
        },
    }


def load_or_initialize_responses(path: Path, models: list[str], resume: bool) -> dict[str, Any]:
    if resume and path.exists():
        return json.loads(path.read_text())
    return empty_responses_doc(models)


def item_already_done(responses: dict[str, Any], model: str, pack_id: str, item_id: str) -> bool:
    item_record = (
        responses.get("models", {})
        .get(model, {})
        .get("packs", {})
        .get(pack_id, {})
        .get("items", {})
        .get(item_id)
    )
    return bool(item_record and item_record.get("ok") is True)


def put_item_response(
    responses: dict[str, Any],
    *,
    model: str,
    pack: dict[str, Any],
    item: dict[str, Any],
    result: dict[str, Any],
) -> None:
    model_record = responses.setdefault("models", {}).setdefault(model, {"source": "openrouter", "packs": {}})
    pack_record = model_record.setdefault("packs", {}).setdefault(
        pack["id"],
        {
            "task_segment": pack["task_segment"],
            "items": {},
        },
    )
    pack_record["items"][item["id"]] = result


def summarize_openrouter_responses(responses: dict[str, Any]) -> dict[str, Any]:
    by_model: dict[str, Any] = {}
    total = 0
    ok = 0
    failed = 0
    for model, model_record in responses.get("models", {}).items():
        model_total = 0
        model_ok = 0
        model_failed = 0
        for pack in model_record.get("packs", {}).values():
            for item in pack.get("items", {}).values():
                model_total += 1
                if item.get("ok") is True:
                    model_ok += 1
                else:
                    model_failed += 1
        total += model_total
        ok += model_ok
        failed += model_failed
        by_model[model] = {
            "total": model_total,
            "ok": model_ok,
            "failed": model_failed,
        }
    return {
        "provider": responses.get("provider"),
        "started_at_utc": responses.get("started_at_utc"),
        "completed_at_utc": utc_now(),
        "stop_reason": responses.get("stop_reason"),
        "total": total,
        "ok": ok,
        "failed": failed,
        "by_model": by_model,
    }


def run_openrouter_eval(
    *,
    pack_root: str | Path,
    output_responses: str | Path,
    output_scores: str | Path | None,
    output_summary: str | Path | None,
    output_manifest: str | Path | None,
    env_path: str | Path,
    models: list[str] | None,
    segments: list[str] | None,
    pack_ids: list[str] | None,
    max_items: int | None,
    items_per_pack: int | None,
    dry_run: bool,
    resume: bool,
    sleep: float,
    timeout: int,
    max_retries: int,
    retry_backoff: float,
    temperature: float,
    max_tokens: int,
) -> dict[str, Any] | None:
    selected_models = models or DEFAULT_MODELS
    packs = filter_packs(load_packs(pack_root), segments=segments, pack_ids=pack_ids)
    tasks = iter_tasks(packs, max_items=max_items, items_per_pack=items_per_pack)

    if dry_run:
        print(f"Dry run: would run {len(selected_models)} model(s) over {len(tasks)} eval-pack item(s).")
        for model in selected_models:
            print(f"- {model}")
        for pack, item in tasks[:10]:
            print(f"  {pack['task_segment']} / {item['id']}: {item['title']}")
        if len(tasks) > 10:
            print(f"  ... {len(tasks) - 10} more item(s)")
        return None

    load_env(env_path)
    output_responses_path = Path(output_responses)
    output_responses_path.parent.mkdir(parents=True, exist_ok=True)
    responses = load_or_initialize_responses(output_responses_path, selected_models, resume)

    for model in selected_models:
        responses.setdefault("models", {}).setdefault(model, {"source": "openrouter", "packs": {}})
        stop_reason: str | None = None
        for pack, item in tasks:
            if resume and item_already_done(responses, model, pack["id"], item["id"]):
                print(f"Skipping existing ok result for {model} on {pack['id']}::{item['id']}.", flush=True)
                continue
            print(f"Running {model} on {pack['id']}::{item['id']}...", flush=True)
            result = run_item(
                model=model,
                pack=pack,
                item=item,
                timeout=timeout,
                max_retries=max_retries,
                retry_backoff=retry_backoff,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            put_item_response(responses, model=model, pack=pack, item=item, result=result)
            write_json(output_responses_path, responses)
            if result_indicates_daily_free_quota(result):
                stop_reason = "openrouter_free_model_daily_limit_exhausted"
                responses["stop_reason"] = stop_reason
                responses["stopped_at_utc"] = utc_now()
                write_json(output_responses_path, responses)
                print("Stopping run: OpenRouter free-model daily request limit is exhausted.", flush=True)
                break
            time.sleep(sleep)
        if stop_reason:
            break

    responses["completed_at_utc"] = utc_now()
    write_json(output_responses_path, responses)

    if output_manifest:
        write_json(output_manifest, summarize_openrouter_responses(responses))
    if output_scores:
        scores = score_responses(pack_root, responses)
        write_json(output_scores, scores)
        if output_summary:
            write_scores_markdown(output_summary, scores)

    return responses
