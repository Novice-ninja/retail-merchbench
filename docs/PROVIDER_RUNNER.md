# Provider Runner

MerchBench should not depend on one provider quota. The eval-pack runner supports a provider-agnostic path for OpenAI-compatible providers and keeps adapter stubs for native-provider integrations.

## Config Files

- `routing/provider_registry.json`: non-secret provider metadata, endpoints, default model candidates, and adapter status.
- `.env.local`: local secrets and provider endpoint overrides. This file is ignored by git.
- `.env.example`: public template for provider credentials.

## Supported Now

The `eval-pack-provider` command currently supports OpenAI-compatible chat-completions providers:

```bash
python3 -m merchbench.cli eval-pack-provider --provider ollama --dry-run --items-per-pack 1
python3 -m merchbench.cli eval-pack-provider --provider openrouter --dry-run --items-per-pack 1
python3 -m merchbench.cli eval-pack-provider --provider openai --dry-run --items-per-pack 1
python3 -m merchbench.cli eval-pack-provider --provider groq --dry-run --items-per-pack 1
python3 -m merchbench.cli eval-pack-provider --provider cerebras --dry-run --items-per-pack 1
python3 -m merchbench.cli eval-pack-provider --provider xai --dry-run --items-per-pack 1
```

Provider outputs default to ignored files under `reports/eval_packs/provider_<provider>_*.json` and `reports/eval_packs/provider_<provider>_*.md`.

## Local Ollama Layer

Ollama is the no-quota baseline provider. It exposes an OpenAI-compatible `/v1/chat/completions` endpoint at `http://localhost:11434/v1`.

Current scored local panel:

```bash
ollama list
# llama3.2:3b
# lfm2.5-thinking:1.2b
# gemma4:e2b
```

Recommended downloads for a 24 GB RAM Mac:

```bash
# Very small / throughput baseline.
ollama pull lfm2.5-thinking:1.2b

# Edge retail-agent baseline.
ollama pull gemma4:e2b

# Strong small-model baseline.
ollama pull qwen3.5:4b

# Main local quality baseline.
ollama pull lfm2.5
ollama pull qwen3.5:9b

# Larger local comparison, likely slower but still plausible on 24 GB RAM.
ollama pull gemma4:12b
```

Optional stretch candidates:

```bash
# Larger, use selectively because model file size approaches local RAM pressure.
ollama pull qwen3.5:27b
ollama pull gemma4:26b
```

Run local smoke:

```bash
python3 -m merchbench.cli eval-pack-provider \
  --provider ollama \
  --models llama3.2:3b \
  --max-items 1 \
  --resume
```

Run local full suite:

```bash
python3 -m merchbench.cli eval-pack-provider \
  --provider ollama \
  --models llama3.2:3b lfm2.5-thinking:1.2b gemma4:e2b qwen3.5:4b lfm2.5 qwen3.5:9b \
  --unload-after-item \
  --resume
```

Use `--unload-after-item` for local full-suite runs on memory-constrained machines. The current stored local results were run sequentially; `llama3.2:3b` produced clean structured coverage, while `gemma4:e2b` and `lfm2.5-thinking:1.2b` are scoreable but have response-contract failure caveats.

## Cloud Provider Placeholders

Fill these in inside `.env.local`:

```bash
GROQ_API_KEY=
XAI_API_KEY=
CEREBRAS_API_KEY=
OPENAI_API_KEY=
GITHUB_MODELS_API_KEY=
CLOUDFLARE_API_TOKEN=
CLOUDFLARE_ACCOUNT_ID=
```

Groq:

```bash
python3 -m merchbench.cli eval-pack-provider \
  --provider groq \
  --models llama-3.1-8b-instant llama-3.3-70b-versatile openai/gpt-oss-20b \
  --items-per-pack 2 \
  --resume
```

Cerebras:

```bash
python3 -m merchbench.cli eval-pack-provider \
  --provider cerebras \
  --models gpt-oss-120b zai-glm-4.7 \
  --items-per-pack 2 \
  --resume
```

OpenAI:

```bash
python3 -m merchbench.cli eval-pack-provider \
  --provider openai \
  --models gpt-4.1-nano \
  --items-per-pack 2 \
  --resume
```

xAI / Grok:

```bash
python3 -m merchbench.cli eval-pack-provider \
  --provider xai \
  --models grok-3-mini grok-3 \
  --items-per-pack 2 \
  --resume
```

GitHub Models and Cloudflare Workers AI are listed in the registry but still need native adapters. GitHub Models uses GitHub's model inference API/Azure AI Inference flow rather than the same OpenAI-compatible endpoint shape. Cloudflare Workers AI uses account-scoped native REST endpoints.

## Quota Strategy

1. Run Ollama first every day: no quota, full-suite baseline.
2. Run Groq next: likely the most useful free cloud quota pool for open models.
3. Use OpenRouter free models only for balanced probes unless credits are added.
4. Use Cerebras/xAI/GitHub/Cloudflare as separate daily pools after keys are configured.
5. Keep provider failures, parse failures, latency, and model score separate in reports.

## Source Notes

- Ollama model catalog and OpenAI compatibility: `https://ollama.com/search`, `https://docs.ollama.com/api/openai-compatibility`
- Groq API: `https://console.groq.com/docs/api-reference`
- Cerebras OpenAI compatibility: `https://inference-docs.cerebras.ai/resources/openai`
- xAI chat completions: `https://docs.x.ai/docs/guides/chat-completions`
- GitHub Models API and limits: `https://docs.github.com/en/github-models/use-github-models/prototyping-with-ai-models`
- Cloudflare Workers AI REST API: `https://developers.cloudflare.com/workers-ai/get-started/rest-api/`
