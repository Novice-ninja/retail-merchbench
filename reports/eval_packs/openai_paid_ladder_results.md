# OpenAI Paid Ladder Results

Run completed on 2026-06-07 UTC using the provider-agnostic eval-pack runner. Scores below were refreshed after Session 2 anti-echo scorer hardening.

## Summary

All listed OpenAI models completed the full 100-item segment eval-pack corpus with zero provider failures after targeted retries for reasoning-only empty responses on `gpt-5-nano` and `gpt-5-mini`. The hardened scorer treats these numbers as routing diagnostics, not final human-validated rankings.

| Rank in hardened OpenAI ladder | Model | Overall Avg | Scored Coverage | Provider Failures | Packs Passing | Prompt Tokens | Completion Tokens | Reasoning Tokens | Estimated Artifact Cost |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | `openai/gpt-5.5` | 7.4614/10 | 100/100 | 0/100 | 0/8 | 47,865 | 36,592 | 0 | $1.3371 |
| 2 | `openai/gpt-5.4` | 7.3907/10 | 100/100 | 0/100 | 0/8 | 47,865 | 41,488 | 0 | $0.7420 |
| 3 | `openai/gpt-5.4-mini` | 7.3693/10 | 100/100 | 0/100 | 0/8 | 47,865 | 30,349 | 0 | $0.1725 |
| 4 | `openai/gpt-5-mini` | 7.0175/10 | 100/100 | 0/100 | 0/8 | 47,865 | 65,976 | 0 | $0.1439 |
| 5 | `openai/gpt-5-nano` | 5.7188/10 | 100/100 | 0/100 | 0/8 | 47,865 | 29,140 | 0 | $0.0140 |
| 6 | `openai/gpt-4.1-nano` | 5.1859/10 | 100/100 | 0/100 | 0/8 | 47,965 | 16,010 | 0 | $0.0112 |

Estimated GPT-5 ladder artifact cost total: $2.4095. Total estimated OpenAI artifact cost including `gpt-4.1-nano`: $2.4207. Dashboard burn can differ because retries and smoke calls may not be represented in the final stored response artifacts.

## Interpretation

- `openai/gpt-5.5` is the full-suite OpenAI leader and the premium anchor for high-downside exceptions.
- `openai/gpt-5.4-mini` is the best economic frontier default: near-premium overall quality at much lower observed artifact cost.
- `openai/gpt-5-mini` remains the best cheap paid specialist for summarization, structured extraction, and portfolio tradeoff.
- `openai/gpt-5.4` is the strongest ambiguous-judgment and constraint-checking profile.
- Pricing/promotion remains below an autonomy bar and needs deterministic margin/funding checks plus human review even with premium models.
- `openai/gpt-5-nano` is a useful cheap baseline, but it is not sufficient for high-downside planning segments.

## Artifacts

- `reports/eval_packs/openai_gpt_5_nano_summary.md`
- `reports/eval_packs/openai_gpt_5_mini_summary.md`
- `reports/eval_packs/openai_gpt_54_mini_summary.md`
- `reports/eval_packs/openai_gpt_54_summary.md`
- `reports/eval_packs/openai_gpt_55_summary.md`
