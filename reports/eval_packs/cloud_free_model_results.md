# Cloud and Local Capacity Model Results

Run date: 2026-06-07 UTC refresh after Session 2 anti-echo scorer hardening.

This report summarizes the local, free-tier, and low-cost comparator models in the current stored artifact set after full-suite reruns. Scores cover the 100-item segment eval-pack corpus for the curated local/Groq/Cerebras panel. OpenRouter free-tier probes stopped at the daily free-model cap and are not included in the combined leaderboard below.

## Executive Readout

`cerebras/zai-glm-4.7` is the strongest non-OpenAI-paid comparator at 6.8471/10. `cerebras/gpt-oss-120b` follows at 5.9780/10. The Groq models remain useful throughput and provider-diversity comparators, with `groq/qwen/qwen3-32b` leading the Groq subset at 5.6355/10. The local Ollama models are materially weaker on the expanded judgment-heavy corpus.

Pricing/promotion remains weak across this capacity tier. These models should be treated as drafting, triage, or research candidates, not autonomous routes for material price moves.

## Combined Leaderboard

| Rank | Model | Provider | Overall Avg | Scoreable Items | Pack Floors Passed | Tokens Recorded |
| ---: | :--- | :--- | ---: | ---: | ---: | ---: |
| 1 | `cerebras/zai-glm-4.7` | cerebras | 6.8471/10 | 100/100 | 0/8 | 197,078 |
| 2 | `cerebras/gpt-oss-120b` | cerebras | 5.9780/10 | 100/100 | 0/8 | 128,285 |
| 3 | `groq/qwen/qwen3-32b` | groq | 5.6355/10 | 100/100 | 0/8 | 120,643 |
| 4 | `groq/meta-llama/llama-4-scout-17b-16e-instruct` | groq | 5.3578/10 | 100/100 | 0/8 | 64,361 |
| 5 | `openai/gpt-4.1-nano` | openai | 5.1859/10 | 100/100 | 0/8 | 63,975 |
| 6 | `groq/llama-3.3-70b-versatile` | groq | 4.8350/10 | 100/100 | 0/8 | 64,350 |
| 7 | `ollama/gemma4:e2b` | ollama | 3.4145/10 | 100/100 | 0/8 | 138,087 |
| 8 | `ollama/llama3.2:3b` | ollama | 3.2148/10 | 100/100 | 0/8 | 57,309 |
| 9 | `ollama/lfm2.5-thinking:1.2b` | ollama | 2.3328/10 | 100/100 | 0/8 | 164,325 |

## Routing Guidance

- Use `cerebras/zai-glm-4.7` as the strongest free-hosted comparator when output-token budget is available.
- Treat local Ollama models as local-capacity experiments or low-risk drafting aids, not decision-routing defaults for this benchmark shape.
- Treat Groq models as useful throughput and model-family diversity probes, not current quality leaders.
- Keep all high-downside pricing, portfolio, safety, compliance, and customer-trust cases behind deterministic checks and human review.

## Current Source Artifacts

- `reports/eval_packs/cerebras_zai_glm_47_summary.md`
- `reports/eval_packs/cerebras_gpt_oss_120b_summary.md`
- `reports/eval_packs/groq_qwen3_32b_summary.md`
- `reports/eval_packs/groq_scout_summary.md`
- `reports/eval_packs/groq_llama_33_70b_versatile_summary.md`
- `reports/eval_packs/ollama_universe_summary.md`
