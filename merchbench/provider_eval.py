from __future__ import annotations

import json
import os
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests

from merchbench.eval_packs import load_packs, score_responses, write_scores_markdown
from merchbench.io import write_json
from merchbench.openrouter_eval import (
    SYSTEM_PROMPT,
    filter_packs,
    iter_tasks,
    item_already_done,
    load_env,
    parse_json_response,
    prompt_for_item,
    should_retry,
    utc_now,
)


@dataclass(frozen=True)
class ProviderSpec:
    provider: str
    transport: str
    base_url_env: str
    default_base_url: str
    api_key_env: str | None
    default_api_key: str | None
    auth_required: bool
    send_auth_header: bool
    default_models: tuple[str, ...]
    stop_run_signals: tuple[str, ...] = ()


PROVIDER_SPECS: dict[str, ProviderSpec] = {
    "ollama": ProviderSpec(
        provider="ollama",
        transport="openai_compatible",
        base_url_env="OLLAMA_BASE_URL",
        default_base_url="http://localhost:11434/v1",
        api_key_env="OLLAMA_API_KEY",
        default_api_key="ollama",
        auth_required=False,
        send_auth_header=False,
        default_models=("llama3.2:3b",),
    ),
    "openrouter": ProviderSpec(
        provider="openrouter",
        transport="openai_compatible",
        base_url_env="OPENROUTER_BASE_URL",
        default_base_url="https://openrouter.ai/api/v1",
        api_key_env="OPENROUTER_API_KEY",
        default_api_key=None,
        auth_required=True,
        send_auth_header=True,
        default_models=("liquid/lfm-2.5-1.2b-instruct:free", "nvidia/nemotron-nano-9b-v2:free", "poolside/laguna-xs.2:free"),
        stop_run_signals=("free-models-per-day",),
    ),
    "openai": ProviderSpec(
        provider="openai",
        transport="openai_compatible",
        base_url_env="OPENAI_BASE_URL",
        default_base_url="https://api.openai.com/v1",
        api_key_env="OPENAI_API_KEY",
        default_api_key=None,
        auth_required=True,
        send_auth_header=True,
        default_models=("gpt-4.1-nano", "gpt-4o-mini"),
    ),
    "groq": ProviderSpec(
        provider="groq",
        transport="openai_compatible",
        base_url_env="GROQ_BASE_URL",
        default_base_url="https://api.groq.com/openai/v1",
        api_key_env="GROQ_API_KEY",
        default_api_key=None,
        auth_required=True,
        send_auth_header=True,
        default_models=("llama-3.1-8b-instant", "llama-3.3-70b-versatile", "openai/gpt-oss-20b"),
    ),
    "cerebras": ProviderSpec(
        provider="cerebras",
        transport="openai_compatible",
        base_url_env="CEREBRAS_BASE_URL",
        default_base_url="https://api.cerebras.ai/v1",
        api_key_env="CEREBRAS_API_KEY",
        default_api_key=None,
        auth_required=True,
        send_auth_header=True,
        default_models=("gpt-oss-120b", "zai-glm-4.7"),
    ),
    "xai": ProviderSpec(
        provider="xai",
        transport="openai_compatible",
        base_url_env="XAI_BASE_URL",
        default_base_url="https://api.x.ai/v1",
        api_key_env="XAI_API_KEY",
        default_api_key=None,
        auth_required=True,
        send_auth_header=True,
        default_models=("grok-3-mini", "grok-3"),
    ),
    "github_models": ProviderSpec(
        provider="github_models",
        transport="github_models_rest_adapter_stub",
        base_url_env="GITHUB_MODELS_BASE_URL",
        default_base_url="https://models.github.ai/inference",
        api_key_env="GITHUB_MODELS_API_KEY",
        default_api_key=None,
        auth_required=True,
        send_auth_header=True,
        default_models=(),
    ),
    "cloudflare_workers_ai": ProviderSpec(
        provider="cloudflare_workers_ai",
        transport="cloudflare_workers_ai_adapter_stub",
        base_url_env="CLOUDFLARE_WORKERS_AI_BASE_URL",
        default_base_url="https://api.cloudflare.com/client/v4/accounts/${CLOUDFLARE_ACCOUNT_ID}/ai/run",
        api_key_env="CLOUDFLARE_API_TOKEN",
        default_api_key=None,
        auth_required=True,
        send_auth_header=True,
        default_models=("@cf/meta/llama-3.1-8b-instruct",),
    ),
}


def provider_spec(provider: str) -> ProviderSpec:
    try:
        return PROVIDER_SPECS[provider]
    except KeyError as exc:
        choices = ", ".join(sorted(PROVIDER_SPECS))
        raise ValueError(f"unknown provider {provider!r}; choose one of: {choices}") from exc


def provider_base_url(spec: ProviderSpec) -> str:
    return os.getenv(spec.base_url_env, spec.default_base_url).rstrip("/")


def provider_api_key(spec: ProviderSpec) -> str | None:
    if not spec.api_key_env:
        return None
    key = os.getenv(spec.api_key_env) or spec.default_api_key
    if spec.auth_required and not key:
        raise RuntimeError(f"{spec.api_key_env} is missing. Add it to .env.local or the environment.")
    return key


def provider_headers(spec: ProviderSpec) -> dict[str, str]:
    headers = {"Content-Type": "application/json"}
    key = provider_api_key(spec)
    if spec.send_auth_header and key:
        headers["Authorization"] = f"Bearer {key}"
    if spec.provider == "openrouter":
        referer = os.getenv("OPENROUTER_HTTP_REFERER")
        title = os.getenv("OPENROUTER_APP_TITLE", "MerchBench")
        if referer:
            headers["HTTP-Referer"] = referer
        if title:
            headers["X-Title"] = title
    return headers


def completion_token_limit_key(spec: ProviderSpec, model: str) -> str:
    if spec.provider == "openai" and (model.startswith("gpt-5") or model.startswith("o")):
        return "max_completion_tokens"
    return "max_tokens"


def should_send_temperature(spec: ProviderSpec, model: str) -> bool:
    return not (spec.provider == "openai" and (model.startswith("gpt-5") or model.startswith("o")))


def reasoning_effort_for_request(spec: ProviderSpec, model: str) -> str | None:
    if spec.provider != "openai":
        return None
    if model.startswith("gpt-5.1") or model.startswith("gpt-5.2") or model.startswith("gpt-5.3") or model.startswith("gpt-5.4") or model.startswith("gpt-5.5"):
        return "none"
    if model.startswith("gpt-5"):
        return "minimal"
    return None


def signal_in_text(signals: tuple[str, ...], text: str | None) -> bool:
    if not text:
        return False
    lowered = text.lower()
    return any(signal.lower() in lowered for signal in signals)


def result_indicates_stop(spec: ProviderSpec, result: dict[str, Any]) -> bool:
    if result.get("quota_exhausted") is True:
        return True
    return signal_in_text(spec.stop_run_signals, result.get("error")) or signal_in_text(spec.stop_run_signals, result.get("raw_text"))


def unload_provider_model(spec: ProviderSpec, model: str, *, reason: str, timeout: int = 30) -> None:
    if spec.provider != "ollama":
        return
    model_id = response_model_id(spec.provider, model)
    try:
        result = subprocess.run(
            ["ollama", "stop", model],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        print(f"Warning: could not unload {model_id} after {reason}: {exc!r}", flush=True)
        return

    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        print(f"Warning: ollama stop failed for {model_id} after {reason}: {detail}", flush=True)
        return
    print(f"Unloaded {model_id} after {reason}.", flush=True)


def post_openai_compatible(
    spec: ProviderSpec,
    payload: dict[str, Any],
    *,
    timeout: int,
    max_retries: int,
    retry_backoff: float,
) -> tuple[requests.Response | None, list[dict[str, Any]], str | None]:
    attempts: list[dict[str, Any]] = []
    url = f"{provider_base_url(spec)}/chat/completions"
    headers = provider_headers(spec)
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
            terminal_quota = signal_in_text(spec.stop_run_signals, response.text)
            retryable = should_retry(response.status_code) and not terminal_quota
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


def run_provider_item(
    *,
    spec: ProviderSpec,
    model: str,
    pack: dict[str, Any],
    item: dict[str, Any],
    timeout: int,
    max_retries: int,
    retry_backoff: float,
    temperature: float,
    max_tokens: int,
) -> dict[str, Any]:
    if spec.transport != "openai_compatible":
        return {
            "ok": False,
            "content": {"error": f"Provider transport {spec.transport!r} is not implemented yet."},
            "raw_text": "",
            "error": f"Provider transport {spec.transport!r} is not implemented yet.",
            "completed_at_utc": utc_now(),
        }

    payload: dict[str, Any] = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt_for_item(pack, item)},
        ],
    }
    if should_send_temperature(spec, model):
        payload["temperature"] = temperature
    if max_tokens > 0:
        payload[completion_token_limit_key(spec, model)] = max_tokens
    reasoning_effort = reasoning_effort_for_request(spec, model)
    if reasoning_effort:
        payload["reasoning_effort"] = reasoning_effort
    if spec.provider == "openai":
        payload["response_format"] = {"type": "json_object"}

    response, attempts, error = post_openai_compatible(
        spec,
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
            "quota_exhausted": signal_in_text(spec.stop_run_signals, error) or signal_in_text(spec.stop_run_signals, response.text),
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
            "content": {"error": f"Malformed {spec.provider} response: {exc!r}"},
            "raw_text": response.text[:4000],
            "error": f"Malformed {spec.provider} response: {exc!r}",
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


def response_model_id(provider: str, model: str) -> str:
    return f"{provider}/{model}"


def empty_provider_responses_doc(provider: str, models: list[str]) -> dict[str, Any]:
    return {
        "version": "0.1",
        "run_type": "segment_eval_pack_responses",
        "provider": provider,
        "started_at_utc": utc_now(),
        "models": {
            response_model_id(provider, model): {
                "source": provider,
                "provider_model_id": model,
                "packs": {},
            }
            for model in models
        },
    }


def load_or_initialize_provider_responses(path: Path, provider: str, models: list[str], resume: bool) -> dict[str, Any]:
    if resume and path.exists():
        return json.loads(path.read_text())
    return empty_provider_responses_doc(provider, models)


def put_provider_item_response(
    responses: dict[str, Any],
    *,
    provider: str,
    model: str,
    pack: dict[str, Any],
    item: dict[str, Any],
    result: dict[str, Any],
) -> None:
    model_id = response_model_id(provider, model)
    model_record = responses.setdefault("models", {}).setdefault(
        model_id,
        {
            "source": provider,
            "provider_model_id": model,
            "packs": {},
        },
    )
    pack_record = model_record.setdefault("packs", {}).setdefault(
        pack["id"],
        {
            "task_segment": pack["task_segment"],
            "items": {},
        },
    )
    pack_record["items"][item["id"]] = result


def summarize_provider_responses(responses: dict[str, Any]) -> dict[str, Any]:
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
            "provider_model_id": model_record.get("provider_model_id"),
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


def run_provider_eval(
    *,
    provider: str,
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
    unload_after_item: bool,
    unload_after_model: bool,
) -> dict[str, Any] | None:
    spec = provider_spec(provider)
    selected_models = models or list(spec.default_models)
    if not selected_models:
        raise RuntimeError(f"No default models configured for provider {provider!r}; pass --models explicitly.")

    packs = filter_packs(load_packs(pack_root), segments=segments, pack_ids=pack_ids)
    tasks = iter_tasks(packs, max_items=max_items, items_per_pack=items_per_pack)

    if dry_run:
        print(f"Dry run: would run provider {provider!r} over {len(selected_models)} model(s) and {len(tasks)} eval-pack item(s).")
        print(f"Transport: {spec.transport}")
        print(f"Base URL: {provider_base_url(spec)}")
        for model in selected_models:
            print(f"- {response_model_id(provider, model)}")
        for pack, item in tasks[:10]:
            print(f"  {pack['task_segment']} / {item['id']}: {item['title']}")
        if len(tasks) > 10:
            print(f"  ... {len(tasks) - 10} more item(s)")
        return None

    load_env(env_path)
    output_responses_path = Path(output_responses)
    output_responses_path.parent.mkdir(parents=True, exist_ok=True)
    responses = load_or_initialize_provider_responses(output_responses_path, provider, selected_models, resume)

    for model in selected_models:
        model_id = response_model_id(provider, model)
        responses.setdefault("models", {}).setdefault(model_id, {"source": provider, "provider_model_id": model, "packs": {}})
        stop_reason: str | None = None
        for pack, item in tasks:
            if resume and item_already_done(responses, model_id, pack["id"], item["id"]):
                print(f"Skipping existing ok result for {model_id} on {pack['id']}::{item['id']}.", flush=True)
                continue
            print(f"Running {model_id} on {pack['id']}::{item['id']}...", flush=True)
            result = run_provider_item(
                spec=spec,
                model=model,
                pack=pack,
                item=item,
                timeout=timeout,
                max_retries=max_retries,
                retry_backoff=retry_backoff,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            put_provider_item_response(responses, provider=provider, model=model, pack=pack, item=item, result=result)
            write_json(output_responses_path, responses)
            if unload_after_item:
                unload_provider_model(spec, model, reason=f"{pack['id']}::{item['id']}")
            if result_indicates_stop(spec, result):
                stop_reason = f"{provider}_quota_exhausted"
                responses["stop_reason"] = stop_reason
                responses["stopped_at_utc"] = utc_now()
                write_json(output_responses_path, responses)
                print(f"Stopping run: provider {provider!r} quota stop signal detected.", flush=True)
                break
            time.sleep(sleep)
        if unload_after_model and not unload_after_item:
            unload_provider_model(spec, model, reason="model run")
        if stop_reason:
            break

    responses["completed_at_utc"] = utc_now()
    write_json(output_responses_path, responses)

    if output_manifest:
        write_json(output_manifest, summarize_provider_responses(responses))
    if output_scores:
        scores = score_responses(pack_root, responses)
        write_json(output_scores, scores)
        if output_summary:
            write_scores_markdown(output_summary, scores)

    return responses
