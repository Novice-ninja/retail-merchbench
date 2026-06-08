# Economic Model Routing Framework

Retail MerchBench is a retail model-routing benchmark. Its core question is:

```text
What is the economically right model and workflow choice for this class of retail decision?
```

Retail teams do not make one model call in isolation. They create agents, copilots, approval flows, replenishment tools, pricing workflows, and exception-management harnesses. Every LLM call inside those systems is an economic choice: quality, error downside, latency, cost, variance, and human review all matter.

## Routing Thesis

A strong frontier model hitting a high score is not a benchmark failure. It may mean the task is solvable. The commercially useful question is whether a cheaper model, deterministic rule, optimizer, or human-in-the-loop workflow is sufficient for the same task.

Retail MerchBench should therefore report:

- The minimum model tier that reaches an acceptable decision-quality bar.
- The cost and latency required to reach that bar.
- The error downside if the model is wrong.
- The escalation triggers that should route a case to a stronger model or human reviewer.
- The retail task segments where deterministic checks should run before or instead of an LLM.

## Economic Fit Score

The model-quality score is one input to economic routing rather than the final objective.

```text
economic_fit =
  decision_quality_value
  - expected_error_cost
  - inference_cost
  - latency_penalty
  - variance_or_retry_cost
  - human_review_cost
```

The benchmark should not pretend these terms are universal constants. Retailers will calibrate them differently by category, margin structure, risk tolerance, and operating model. Retail MerchBench provides a starting prior and a repeatable structure for that calibration.

## Decision Segmentation

Every retail task should be categorized by the business properties that determine model choice.

| Dimension | Why It Matters |
| :--- | :--- |
| `task_segment` | Extraction, summary, constraint check, ambiguous planning judgment, portfolio tradeoff, or operational triage have different model needs. |
| `decision_value_band` | A $500 copy suggestion and a $500,000 OTB decision should not use the same escalation policy. |
| `error_downside_band` | Low-value but high-trust or safety-sensitive workflows can still require stronger controls. |
| `reversibility` | Irreversible vendor commitments, public promotions, or store allocations justify more expensive evaluation. |
| `time_horizon` | Cross-season decisions need stronger causal reasoning than same-day clerical tasks. |
| `latency_sla` | A batch planning review can afford a frontier call; a store-floor exception may not. |
| `call_volume_band` | High-volume workflows need a cheaper default and selective escalation. |
| `deterministic_controls` | OTB, MOQ, margin, capacity, and policy checks should often gate model output. |
| `human_review_expected` | Some workflows should never be fully autonomous regardless of model quality. |

## Model Strategy Tiers

Retail MerchBench compares model strategies, not just model brands.

| Strategy | Best Fit | Failure Mode |
| :--- | :--- | :--- |
| Rules only | Deterministic math, policy gates, schema validation, OTB feasibility. | Misses ambiguous judgment and causal tradeoffs. |
| Small model | Summaries, extraction, low-risk classification, first-pass triage. | Overconfident on ambiguous economic tradeoffs. |
| Mid model | Routine planning recommendations with clear constraints and low downside. | May miss second-order opportunity cost or contaminated evidence. |
| Frontier model | Ambiguous, high-downside, multi-driver planning decisions. | Higher cost; can still sound persuasive when wrong. |
| Cascade | Cheap default with deterministic gates and escalation. | Routing policy must be calibrated; bad confidence signals can under-escalate. |
| Human review | Irreversible, high-value, safety, legal, or brand-risk decisions. | Cost and latency; not scalable for every call. |

## Retail Routing Examples

| Retail Segment | Example Workflow | Default Strategy | Escalation Trigger |
| :--- | :--- | :--- | :--- |
| Low-risk summarization | Vendor note recap, weekly business summary | Small model | Conflicting numbers or decision recommendation requested |
| Structured extraction | Cost changes, receipt dates, MOQ, lead time | Rules plus small model | Missing required fields or schema conflict |
| Constraint checking | OTB, MOQ, pack, capacity, margin threshold | Rules first, small or mid model explanation | Any constraint violation or exception request |
| Routine recommendation | Low-risk replenishment or markdown explanation | Mid model plus deterministic checks | Low confidence, high inventory value, conflicting signals |
| Pricing and promotion | Price match, vendor-funded promo, markdown depth | Mid model plus margin and inventory checks | Margin floor breach, supply constraint, pull-forward, or competitive-response uncertainty |
| Ambiguous planning judgment | Chase, allocation, pricing, substitute supply | Mid or frontier model | Contaminated evidence, low reversibility, high markdown risk |
| Portfolio tradeoff | Holiday OTB, vendor-funding tradeoff, cross-category allocation | Frontier plus human review | Any material opportunity-cost or executive-pressure case |
| Operational triage | Store exception, receiving overload, transfer queue | Small or mid model with rules | Safety, labor capacity, customer-trust, or legal exposure |

## Segment Eval Packs

Segment eval packs make the routing map measurable at the task-class level. A summarization or extraction task is evaluated on fidelity, exact values, output contract compliance, and escalation discipline; pricing, portfolio, ambiguous planning, and operational triage tasks are evaluated on causal reasoning, constraints, uncertainty, and review boundaries.

Current packs:

| Segment | Pack | Strategy Under Test | What It Measures |
| :--- | :--- | :--- | :--- |
| `low_risk_summarization` | `eval_packs/low_risk_summarization/pack.json` | `small_model` | Faithful compression, numeric preservation, source caveats, and no-decision boundary control. |
| `structured_extraction` | `eval_packs/structured_extraction/pack.json` | `rules_only` with fallback model support | Exact field extraction, normalization, schema compliance, missing-field handling, and conflict detection. |
| `constraint_checking` | `eval_packs/constraint_checking/pack.json` | `rules_only` | OTB, MOQ, pack, margin, capacity, compliance, and timing gates. |
| `routine_planning_recommendation` | `eval_packs/routine_planning_recommendation/pack.json` | `mid_model` | Bounded replenishment, markdown, allocation, and channel-balancing actions with deterministic guardrails. |
| `pricing_promotion` | `eval_packs/pricing_promotion/pack.json` | `mid_model` | Margin-aware price and promo decisions under vendor funding, competitor pressure, supply limits, and pull-forward risk. |
| `ambiguous_planning_judgment` | `eval_packs/ambiguous_planning_judgment/pack.json` | `frontier_model` | Contaminated evidence, causal reframing, opportunity cost, and uncertainty-calibrated planning decisions. |
| `portfolio_tradeoff` | `eval_packs/portfolio_tradeoff/pack.json` | `frontier_plus_human_review` | Cross-category OTB allocation, leadership pressure, customer-trust risk, and human-review boundaries. |
| `operational_triage` | `eval_packs/operational_triage/pack.json` | `cascade` | Priority classification, owner routing, safety gates, compliance gates, and safe next steps. |

The suite contains 100 eval items. The current repo includes deterministic baselines and a curated `100/100` provider panel across local Ollama models, hosted free-tier Groq/Cerebras models, and the paid OpenAI ladder. OpenRouter free-tier probes are partial because the daily free-model cap was reached, and xAI is excluded until the account has credits or a license. Routing reports should still distinguish automated scorer triage from human-calibrated claims.

Local deterministic baselines can already be generated with:

```bash
make eval-pack-baselines
```

The scorer writes responses, scores, and a summary under `reports/eval_packs/`. API-backed model runs should emit the same response shape as `reports/eval_packs/baseline_responses.json` so they can be scored with `python3 -m merchbench.cli eval-pack-score`.

The OpenRouter runner implements that shape directly:

```bash
python3 -m merchbench.cli eval-pack-openrouter --items-per-pack 1 --resume
```

Use `--items-per-pack` for quota-aware balanced probes across every segment, and use `make eval-pack-openrouter-dry-run` to inspect the run plan without credentials or network calls.

## Reporting Format

For each task segment, report:

- `quality_floor`: minimum acceptable task score and required dimensions.
- `cheapest_passing_strategy`: lowest-cost strategy that clears the floor.
- `frontier_delta`: incremental quality from a frontier model over the cheaper strategy.
- `economic_delta`: whether the frontier improvement justifies its cost and latency.
- `escalation_policy`: conditions that route to stronger model or human review.
- `residual_risk`: remaining business risk even after the recommended strategy.

The current backend report is generated by:

```bash
make routing-report
```

It writes `reports/routing/recommendations.json` and `reports/routing/segment_recommendations.md`. The backend report and Atlas now read the current segment eval-pack score artifacts; the Atlas remains the executive-facing visual artifact, while `reports/routing/` is the machine-readable policy handoff.

## Current Measured Findings

The first full-suite segment-pack provider result set, re-scored after anti-echo hardening, supports these directional routing priors.

- `gpt-5.5` is the current overall leader at 7.4614/10, followed by `gpt-5.4` at 7.3907/10 and `gpt-5.4-mini` at 7.3693/10.
- `gpt-5.4-mini` is the strongest economic frontier result: it is within 0.0921 points of `gpt-5.5` at roughly 13 percent of the observed artifact cost.
- `gpt-5-mini` is the best cheap paid specialist for low-risk summarization, structured extraction, and portfolio tradeoff.
- `cerebras/zai-glm-4.7` is the strongest free hosted result at 6.8471/10, ahead of `cerebras/gpt-oss-120b`, the Groq-hosted open models, and the local Ollama set.
- Pricing/promotion and routine planning remain below the 7.0 proxy autonomy bar even for the strongest models; material decisions should retain deterministic checks and human review.
- Anti-echo baselines help audit scorer robustness: `baseline/source_echo` scores 3.3530 and `baseline/keyword_guardrail` scores 4.3280 on the full 100-item corpus. Human calibration is still required before external benchmark claims.

The current analysis artifacts are:

- `reports/atlas/analysis.md`
- `reports/atlas/index.html`
- `reports/atlas/model_frontier.svg`
- `reports/atlas/segment_heatmap.svg`
- `reports/eval_packs/openai_paid_ladder_results.md`
- `reports/publication_metrics/economic_metrics.md`
- `docs/HUMAN_RATER_PROTOCOL.md`

## Public Artifact: Retail AI Model Routing Atlas

The primary public work product should be an executive-readable Atlas, not only a CSV or leaderboard. Retail leaders are used to quickly scanning quadrants, horizons, and segment cards. MerchBench should use that visual language while keeping the evidence auditable.

The Atlas should include:

- A model cluster map across judgment quality, cost burden, and experience latency.
- Task-segment cards with a recommended default strategy, quality floor, use case, avoid case, and escalation triggers.
- Pareto views for cost per passing answer and latency per passing answer once telemetry is available.
- Clear caveats separating measured results from routing priors.

The current static Atlas is generated from real eval-pack score artifacts and lives in `reports/atlas/index.html`. It can be regenerated with `make atlas`.

## What MerchBench Should Not Claim

MerchBench should not claim that a universal model choice exists for all retailers. A grocery chain, apparel specialty retailer, marketplace, and big-box retailer have different margins, labor models, inventory constraints, approval cultures, and risk tolerances.

The right claim is narrower and more useful:

```text
Given this retail task class and these economic assumptions, this model/workflow tier is the cheapest strategy that appears sufficient, and these are the escalation triggers.
```

That makes MerchBench a practical baseline for teams building retail AI harnesses, not a replacement for their internal evals.
