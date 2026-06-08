# Data Card

## Dataset Summary

Retail MerchBench contains 100 synthetic, expert-authored retail merchandise-planning tasks across eight decision segments. The tasks are designed to evaluate model-routing choices for retail workflows under ambiguity, operational constraints, causal uncertainty, and economic risk.

The dataset does not contain customer personal data or proprietary retailer data.

## Segment Coverage

| Segment | Items | Typical workflow |
| :--- | ---: | :--- |
| Low-risk summarization | 17 | Vendor note recap, weekly business summary, operational update compression. |
| Structured extraction | 17 | MOQ, cost change, receipt date, compliance, and terms extraction. |
| Constraint checking | 11 | OTB, MOQ, pack, margin, timing, and capacity feasibility gates. |
| Routine planning recommendation | 11 | Low-to-moderate risk replenishment, rebalancing, allocation, or markdown recommendations. |
| Pricing and promotion | 11 | Price-match, vendor-funded promotion, markdown depth, and pull-forward risk decisions. |
| Ambiguous planning judgment | 11 | Chase, substitution, contaminated demand, and causal reframing decisions. |
| Portfolio tradeoff | 11 | Cross-category OTB, opportunity cost, and executive exception decisions. |
| Operational triage | 11 | Store receiving, customer promise, safety, labor, and exception prioritization. |

## Item Fields

Each item includes:

- title and prompt;
- retail function and category;
- ambiguity type;
- risk level and downside band;
- reversibility;
- deterministic controls;
- deterministic checks;
- escalation triggers;
- expected output contract;
- must-include and must-not-include checks;
- expected failure mode;
- scoring rationale.

## Source and Authorship

The corpus is synthetic and retail-grounded. Items are authored to reflect common merchandising, planning, pricing, allocation, vendor, and operational exception patterns without using private company data.

## Intended Uses

Appropriate uses:

- benchmark retail-specific model judgment;
- compare model or workflow fit by retail decision segment;
- test deterministic baselines and scorer robustness;
- run new provider or local-model evaluations;
- build internal retail eval packs using the same schema;
- support human-rater calibration studies.

Inappropriate uses:

- claiming universal model superiority;
- replacing retailer-specific production evals;
- automating material pricing, portfolio, safety, legal, or executive override decisions without controls;
- using public scores as procurement advice without local cost and latency calibration.

## Stored Model Artifacts

The repository includes stored responses, scores, summaries, and manifests for a curated 14-model panel with full 100-item coverage. These artifacts support offline reproduction without provider calls.

Stored results include:

- paid OpenAI ladder models;
- hosted Groq and Cerebras models;
- local Ollama models;
- deterministic adversarial baselines.

Provider results are a snapshot. Model aliases, pricing, decoding behavior, rate limits, and safety layers can change.

## Scoring Caveats

The scorer is automated and suitable for routing diagnostics. It is not a final human-validated judge. Human-rater calibration and repeated-run variance should be completed before making external benchmark-ranking claims.

## Known Limitations

- Synthetic tasks may omit retailer-specific systems, approvals, policies, and data-quality issues.
- Stored provider responses are mostly single-run artifacts.
- Production p95 latency and retry behavior are not measured.
- Public tasks can become contaminated after release.
- Economic weights are public priors, not retailer-specific value models.

## Privacy and Safety

No customer personal data is included. Production adopters should still evaluate privacy, fairness, labor impact, vendor policy, store safety, customer promise, and brand-risk implications before deploying model-assisted retail decisions.
