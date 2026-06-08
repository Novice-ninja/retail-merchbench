# Methodology

Retail MerchBench evaluates language-model and workflow fit for retail merchandise-planning decisions. The benchmark is organized around economic sufficiency: the goal is to identify the cheapest safe model, deterministic control, cascade, or human-review workflow for each class of retail decision.

## Evaluation Object

The benchmark evaluates one response to one self-contained retail task. It does not require private retailer systems, retrieval, tools, or multi-turn agency. This isolates merchant and planner judgment before adding production integrations.

Each task asks whether a model can:

- preserve and use the relevant evidence;
- identify weak, missing, conflicting, or contaminated signals;
- respect operational constraints such as OTB, MOQ, pack multiples, margin floors, lead time, receiving capacity, and labor capacity;
- reason about causal drivers and reflexive effects;
- calibrate uncertainty;
- recommend an action, non-action, or escalation that a retail operator could use.

## Segment Design

The 100-item corpus is split across eight retail decision segments:

| Segment | Items | Evaluation role |
| :--- | ---: | :--- |
| Low-risk summarization | 17 | Faithful recap, number preservation, source caveats, no unsupported recommendation. |
| Structured extraction | 17 | Schema-ready extraction from messy vendor, inventory, cost, or operational text. |
| Constraint checking | 11 | OTB, MOQ, pack, margin, capacity, timing, and policy feasibility checks. |
| Routine planning recommendation | 11 | Bounded, reversible actions with deterministic guardrails and next-read triggers. |
| Pricing and promotion | 11 | Margin-aware, supply-aware, competitor-aware promotion and price decisions. |
| Ambiguous planning judgment | 11 | Contaminated evidence, causal reframing, uncertainty, and conditional action. |
| Portfolio tradeoff | 11 | Cross-category OTB, opportunity cost, leadership pressure, and review boundaries. |
| Operational triage | 11 | Exception prioritization across safety, customer promise, labor, and compliance. |

Each segment exists because it implies a different routing decision. Some workflows should be rules-first. Others require a cheap model with schema validation. Others justify frontier-model escalation or human review.

## Item Metadata

Each eval item includes:

- `ambiguity_type`
- `risk_level`
- `reversibility`
- `deterministic_controls`
- `escalation_triggers`
- `expected_failure_mode`
- `scoring_rationale`
- required output fields
- must-include and must-not-include checks

This metadata is part of the benchmark, not decoration. It makes the intended retail construct explicit and lets validation catch shallow or under-specified items.

## Difficulty Principles

Retail MerchBench items are difficult for retail reasons:

- demand signals can be stockout-censored or return-contaminated;
- promotions can pull forward demand instead of creating incrementality;
- vendor funding can hide margin or supply risk;
- social trend signals can be real but operationally mistimed;
- a recommendation can change the future evidence stream;
- OTB, pack, MOQ, capacity, and lead-time constraints can make plausible actions infeasible;
- high-value portfolio tradeoffs can require escalation even when a model produces a high-quality answer.

The benchmark avoids hidden facts. Strong answers should be possible from the prompt alone.

## Scoring

Segment eval-pack scores use a 10-point normalized scale. The scorer combines:

- output-contract compliance;
- required-signal coverage;
- known-bad-pattern avoidance;
- deterministic-field checks;
- escalation agreement;
- anti-echo penalties.

Scoring is automated and inspectable. It is suitable for routing diagnostics and stored-artifact comparisons, but not a substitute for human-rater calibration.

## Baselines

The release includes deterministic adversarial baselines:

- source echo;
- keyword guardrail stuffing;
- generic consultant answer;
- always escalate;
- always buy or chase;
- always conservative or no action;
- arithmetic-only answer.

These baselines are scorer sanity checks. If shallow echoing or keyword stuffing scores like a strong model, the scorer is not robust enough.

## Routing Interpretation

Scores are interpreted by segment. A model can be the quality leader but not the economic pick. A cheaper model can be preferred if it clears the segment quality floor and the remaining risk is controlled by deterministic checks or human review.

Retail MerchBench reports:

- quality leader;
- economic pick;
- default route;
- premium escalation point;
- human-review boundary;
- residual validity caveats.

## Validity Boundaries

The current results are automated routing priors. Production users should calibrate them against:

- internal category economics;
- contracted model pricing;
- latency requirements;
- retry behavior;
- cache policy;
- retailer-specific data quality;
- approval workflows;
- human-rater agreement.
