# Publication Metrics

Offline metrics from stored artifacts. Repeated-run variance is planned but not yet measured.

The risk-weighted average is a proxy designed to keep low-risk summarization and extraction from hiding failures in pricing, portfolio, ambiguous judgment, or operational triage. It is not a retailer-specific value model.

| Model | Overall Avg | Risk-Weighted Avg | Artifact Cost | Est. Cost / 1k Calls | Score / Dollar | Coverage | Clears 7.0/10 Floor |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | :--- |
| `openai/gpt-5.5` | 7.4614/10 | 7.3718/10 | $1.3371 | $13.3709 | 5.58 | 100/100 | Yes |
| `openai/gpt-5.4-mini` | 7.3693/10 | 7.2283/10 | $0.1725 | $1.7247 | 42.73 | 100/100 | Yes |
| `openai/gpt-5.4` | 7.3907/10 | 7.1874/10 | $0.7420 | $7.4198 | 9.96 | 100/100 | Yes |
| `cerebras/zai-glm-4.7` | 6.8471/10 | 6.6584/10 | $0 | n/a | free/local | 100/100 | No |
| `openai/gpt-5-mini` | 7.0175/10 | 6.6453/10 | $0.1439 | $1.4392 | 48.76 | 100/100 | Yes |
| `cerebras/gpt-oss-120b` | 5.978/10 | 5.8128/10 | $0 | n/a | free/local | 100/100 | No |
| `groq/qwen/qwen3-32b` | 5.6355/10 | 5.5091/10 | $0 | n/a | free/local | 100/100 | No |
| `openai/gpt-5-nano` | 5.7188/10 | 5.4273/10 | $0.0140 | $0.1405 | 407.06 | 100/100 | No |
| `groq/meta-llama/llama-4-scout-17b-16e-instruct` | 5.3578/10 | 5.0503/10 | $0 | n/a | free/local | 100/100 | No |
| `openai/gpt-4.1-nano` | 5.1859/10 | 5.0006/10 | $0.0112 | $0.1120 | 462.99 | 100/100 | No |
| `groq/llama-3.3-70b-versatile` | 4.835/10 | 4.4095/10 | $0 | n/a | free/local | 100/100 | No |
| `ollama/gemma4:e2b` | 3.4145/10 | 3.1942/10 | $0 | n/a | free/local | 100/100 | No |
| `ollama/llama3.2:3b` | 3.2148/10 | 2.8997/10 | $0 | n/a | free/local | 100/100 | No |
| `ollama/lfm2.5-thinking:1.2b` | 2.3328/10 | 2.1933/10 | $0 | n/a | free/local | 100/100 | No |

## Interpretation Rules

- Use `overall_average` for broad diagnostic comparison.
- Use `risk_weighted_average` when evaluating merchant-facing decision support.
- Use `estimated_cost_per_1000_workflow_calls_usd` only as a rough artifact-scale proxy; production cost needs live token, cache, retry, and latency telemetry.
- Treat all `single_run_only` models as variance-unknown until repeated runs are completed.
