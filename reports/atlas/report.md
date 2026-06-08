# Retail MerchBench Report

Generated: 2026-06-08T03:19:27+00:00

## Executive Summary

Retail MerchBench reframes the benchmark around economic model routing for retail decisions. The question is not only which model scores highest. The question is which model or workflow tier is economically sufficient for each class of retail work once quality, cost, latency burden, deterministic controls, downside risk, and human review are considered.

The current evidence package contains 100 segment eval-pack items and a curated provider panel with 100/100 scored coverage for 14 real models. The scored panel spans local Ollama, hosted Groq/Cerebras, and the paid OpenAI ladder. OpenRouter free-tier probes and xAI availability are documented as capacity findings, not ranked results.

## Decision Readout

- Broad economic default: `openai/gpt-5.4-mini`.
- Premium quality anchor: `openai/gpt-5.5`.
- Cheap paid specialist: `openai/gpt-5-mini`.
- Strongest free hosted comparator: `cerebras/zai-glm-4.7`.
- Non-autonomous segments: pricing/promotion, routine planning, portfolio tradeoff, and high-risk operational triage still need deterministic controls and human review boundaries.

## Key Findings

- Retail MerchBench contains 100 segment eval items, and the curated provider panel has 100/100 scored coverage for 14 real models plus deterministic baselines.
- GPT-5.5 is the overall leader at 7.4614/10, followed by GPT-5.4 at 7.3907/10 and GPT-5.4 Mini at 7.3693/10.
- GPT-5.4 Mini is the economic frontier result: it lands within 0.0921 points of GPT-5.5 at about 13 percent of the observed artifact cost.
- GPT-5 Mini is the best cheap paid specialist for summarization, structured extraction, and portfolio tradeoff.
- Z.ai GLM 4.7 is the strongest free hosted result at 6.8471/10, clearly ahead of GPT-OSS 120B, Groq-hosted open models, and local Ollama models in this run.
- The anti-echo scorer rejects shallow deterministic baselines: source echo scores 3.3530 and keyword guardrail stuffing scores 4.3280 on the 100-item corpus.
- Pricing/promotion and routine planning remain below the 7.0 proxy autonomy floor even for the strongest models; these workflows need deterministic controls and human review.
- Local Ollama models are useful for low-cost experimentation, but none clears deterministic keyword-guardrail baseline quality on this full-suite judgment benchmark.
- OpenRouter free-tier probes stopped at the daily free-model cap and xAI was unavailable; they are documented as capacity findings, not ranked model results.
- The scorer includes adversarial anti-echo baselines, but public benchmark claims still need human-rater calibration and repeated-run variance.

## Model Leaderboard

| Rank | Model | Overall | Risk-Weighted | Artifact Cost | Cost / 1k Calls | Routing Readout |
| ---: | :--- | ---: | ---: | ---: | ---: | :--- |
| 1 | `openai/gpt-5.5` | 7.4614/10 | 7.3718/10 | $1.3371 | $13.3709 | Overall quality leader in the 100-item run; best reserved for high-downside exceptions. |
| 2 | `openai/gpt-5.4` | 7.3907/10 | 7.1874/10 | $0.7420 | $7.4198 | Near-top overall quality and the strongest ambiguous-judgment/constraint-checking profile. |
| 3 | `openai/gpt-5.4-mini` | 7.3693/10 | 7.2283/10 | $0.1725 | $1.7247 | Near-frontier quality at materially lower observed artifact cost than the premium models. |
| 4 | `openai/gpt-5-mini` | 7.0175/10 | 6.6453/10 | $0.1439 | $1.4392 | Best cheap paid default for summarization, extraction, and portfolio triage in this run. |
| 5 | `cerebras/zai-glm-4.7` | 6.8471/10 | 6.6584/10 | $0 | n/a | Strongest free hosted result; competitive with paid small models on several segments. |
| 6 | `cerebras/gpt-oss-120b` | 5.978/10 | 5.8128/10 | $0 | n/a | Strong open model and a good free-capacity comparator. |
| 7 | `openai/gpt-5-nano` | 5.7188/10 | 5.4273/10 | $0.0140 | $0.1405 | Very cheap paid baseline with useful quality for bounded, low-risk workflows. |
| 8 | `groq/qwen/qwen3-32b` | 5.6355/10 | 5.5091/10 | $0 | n/a | Best Groq-hosted model in the full-suite run; required higher caps to suppress thinking traces. |
| 9 | `groq/meta-llama/llama-4-scout-17b-16e-instruct` | 5.3578/10 | 5.0503/10 | $0 | n/a | Efficient hosted baseline, but below the paid OpenAI frontier. |
| 10 | `openai/gpt-4.1-nano` | 5.1859/10 | 5.0006/10 | $0.0112 | $0.1120 | Small direct-OpenAI baseline for low-cost comparisons. |
| 11 | `groq/llama-3.3-70b-versatile` | 4.835/10 | 4.4095/10 | $0 | n/a | Large open hosted comparator with solid but not leading quality. |
| 12 | `ollama/gemma4:e2b` | 3.4145/10 | 3.1942/10 | $0 | n/a | Best local score, but many rows returned empty or parse-invalid content; use only for tightly bounded local experiments. |
| 13 | `ollama/llama3.2:3b` | 3.2148/10 | 2.8997/10 | $0 | n/a | Reliable output producer, but materially weaker judgment. |
| 14 | `ollama/lfm2.5-thinking:1.2b` | 2.3328/10 | 2.1933/10 | $0 | n/a | Tiny local comparator with frequent empty or parse-invalid responses; not attractive for this eval shape. |

## Segment Routing Matrix

| Segment | Quality Leader | Economic Pick | Default Route | Human Review Boundary |
| :--- | :--- | :--- | :--- | :--- |
| Summarization | `openai/gpt-5-mini` (8.0696/10) | `openai/gpt-5-mini` (8.0696/10) | GPT-5 Mini for paid production; GPT-OSS 120B when free hosted quota is available. | No, unless the summary becomes a decision recommendation or contains conflicting financial figures. |
| Extraction | `openai/gpt-5-mini` (8.57/10) | `openai/gpt-5-mini` (8.57/10) | Rules/schema first, GPT-5 Mini fallback for messy source text. | Only for material missing values or field conflicts. |
| Constraint checks | `openai/gpt-5.4` (8.2879/10) | `openai/gpt-5-mini` (7.7792/10) | Deterministic checks first; GPT-5.4 for high-severity explanation, GPT-5 Mini for cheaper routine triage. | Required when a violated constraint is overridden. |
| Routine planning | `openai/gpt-5.4` (6.9939/10) | `openai/gpt-5.4-mini` (6.7273/10) | GPT-5.4 Mini with deterministic guardrails; escalate low-confidence recommendations. | Only for high inventory value, low confidence, or irreversible actions. |
| Pricing & promo | `openai/gpt-5.5` (6.778/10) | `openai/gpt-5.4` (6.4629/10) | GPT-5.5 or GPT-5.4 with margin and vendor-funding controls; human review for material decisions. | Yes for material price moves, below-floor margin, or high competitive-response uncertainty. |
| Ambiguous judgment | `openai/gpt-5.4` (8.5311/10) | `openai/gpt-5.4-mini` (7.3076/10) | GPT-5.4 for ambiguous judgment; GPT-5.4 Mini when the decision is reversible and well-guardrailed. | Recommended for vendor commitments, high markdown risk, or executive-pressure cases. |
| Portfolio tradeoff | `openai/gpt-5-mini` (8.0774/10) | `openai/gpt-5.4-mini` (8.0008/10) | GPT-5 Mini or GPT-5.4 Mini plus human review. | Yes. This should not be fully autonomous in the current evidence base. |
| Ops triage | `openai/gpt-5.5` (7.5235/10) | `openai/gpt-5.4-mini` (6.8261/10) | GPT-5.4 Mini for normal exceptions; GPT-5.5 or human review for safety/customer-trust risk. | Yes when safety, legal, public commitment, or customer-trust exposure appears. |

## Visual Routing System

The visual package contains four complementary views:

- `model_frontier.svg`: master cost-quality frontier across the full model panel.
- `segment_quadrants.svg`: eight segment-level 2x2s plotting each model by segment quality and economic burden.
- `routing_ladder.svg`: model-tier workflow ladder showing default route, premium escalation, and human-review boundary by segment.
- `economic_regret.svg`: segment-level quality gap between the quality leader and the economic pick.

## Provider Coverage

| Provider | Models in Ranked Panel | Best Model | Best Score | Notes |
| :--- | ---: | :--- | ---: | :--- |
| `cerebras` | 2 | `cerebras/zai-glm-4.7` | 6.8471/10 | Strongest free hosted result comes from Z.ai GLM 4.7. |
| `groq` | 3 | `groq/qwen/qwen3-32b` | 5.6355/10 | Useful free hosted open-model comparator pool. |
| `ollama` | 3 | `ollama/gemma4:e2b` | 3.4145/10 | Local/no-quota, but current local scores are below deployable thresholds; two local runs have response-contract caveats. |
| `openai` | 6 | `openai/gpt-5.5` | 7.4614/10 | Paid ladder defines the quality-cost frontier in Retail MerchBench. |

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
