# MerchBench Routing Recommendations

This report is generated from the current 100-item segment eval-pack score artifacts and mirrors the measured routing readout in the Atlas.

- Corpus: 100 segment eval-pack items.
- Curated model panel: 100/100 scored items for the ranked provider panel.
- Scope: automated routing priors until human-rater calibration and repeated-run variance are complete.

| Segment | Quality Leader | Economic Pick | Human Review Boundary |
| :--- | :--- | :--- | :--- |
| `low_risk_summarization` | `GPT-5 Mini` (8.0696/10) | `GPT-5 Mini` (8.0696/10) | No, unless the summary becomes a decision recommendation or contains conflicting financial figures. |
| `structured_extraction` | `GPT-5 Mini` (8.57/10) | `GPT-5 Mini` (8.57/10) | Only for material missing values or field conflicts. |
| `constraint_checking` | `GPT-5.4` (8.2879/10) | `GPT-5 Mini` (7.7792/10) | Required when a violated constraint is overridden. |
| `routine_planning_recommendation` | `GPT-5.4` (6.9939/10) | `GPT-5.4 Mini` (6.7273/10) | Only for high inventory value, low confidence, or irreversible actions. |
| `pricing_promotion` | `GPT-5.5` (6.778/10) | `GPT-5.4` (6.4629/10) | Yes for material price moves, below-floor margin, or high competitive-response uncertainty. |
| `ambiguous_planning_judgment` | `GPT-5.4` (8.5311/10) | `GPT-5.4 Mini` (7.3076/10) | Recommended for vendor commitments, high markdown risk, or executive-pressure cases. |
| `portfolio_tradeoff` | `GPT-5 Mini` (8.0774/10) | `GPT-5.4 Mini` (8.0008/10) | Yes. This should not be fully autonomous in the current evidence base. |
| `operational_triage` | `GPT-5.5` (7.5235/10) | `GPT-5.4 Mini` (6.8261/10) | Yes when safety, legal, public commitment, or customer-trust exposure appears. |

## Segment Details

### Summarization

- Recommended route: GPT-5 Mini for paid production; GPT-OSS 120B when free hosted quota is available.
- Rationale: GPT-5 Mini leads the full-suite readout at 8.0696/10 and remains inexpensive in the paid ladder.
- Evidence status: `full_100_item_segment_pack_scored_curated_panel`
- Eval pack: `eval_packs/low_risk_summarization/pack.json`
- Human review expected: `false`
- Human review boundary: No, unless the summary becomes a decision recommendation or contains conflicting financial figures.
- Deterministic controls: Source citation, numeric preservation, no-recommendation boundary check.

| Top Scored Models | Score | Artifact Cost |
| :--- | ---: | ---: |
| `GPT-5 Mini` | 8.0696/10 | $0.1439 |
| `GPT-5.4` | 7.5713/10 | $0.7420 |
| `GPT-5.4 Mini` | 7.5419/10 | $0.1725 |
| `Z.ai GLM 4.7` | 7.3941/10 | $0 |
| `Qwen3 32B` | 7.1773/10 | $0 |

### Extraction

- Recommended route: Rules/schema first, GPT-5 Mini fallback for messy source text.
- Rationale: GPT-5 Mini leads at 8.5700/10; structured extraction still needs deterministic validation.
- Evidence status: `full_100_item_segment_pack_scored_curated_panel`
- Eval pack: `eval_packs/structured_extraction/pack.json`
- Human review expected: `true`
- Human review boundary: Only for material missing values or field conflicts.
- Deterministic controls: Schema validation, required-field checks, range checks, conflict detection.

| Top Scored Models | Score | Artifact Cost |
| :--- | ---: | ---: |
| `GPT-5 Mini` | 8.57/10 | $0.1439 |
| `GPT-5.4 Mini` | 8.4314/10 | $0.1725 |
| `GPT-5.5` | 8.3748/10 | $1.3371 |
| `GPT-5.4` | 8.0848/10 | $0.7420 |
| `Z.ai GLM 4.7` | 7.7122/10 | $0 |

### Constraint checks

- Recommended route: Deterministic checks first; GPT-5.4 for high-severity explanation, GPT-5 Mini for cheaper routine triage.
- Rationale: GPT-5.4 leads at 8.2879/10, while GPT-5 Mini remains the lower-cost paid option at 7.7792/10.
- Evidence status: `full_100_item_segment_pack_scored_curated_panel`
- Eval pack: `eval_packs/constraint_checking/pack.json`
- Human review expected: `true`
- Human review boundary: Required when a violated constraint is overridden.
- Deterministic controls: OTB, MOQ, pack multiple, margin floor, capacity, and compliance gates.

| Top Scored Models | Score | Artifact Cost |
| :--- | ---: | ---: |
| `GPT-5.4` | 8.2879/10 | $0.7420 |
| `GPT-5.5` | 7.8349/10 | $1.3371 |
| `GPT-5 Mini` | 7.7792/10 | $0.1439 |
| `Z.ai GLM 4.7` | 7.114/10 | $0 |
| `GPT-5.4 Mini` | 7.1076/10 | $0.1725 |

### Routine planning

- Recommended route: GPT-5.4 Mini with deterministic guardrails; escalate low-confidence recommendations.
- Rationale: GPT-5.5 and GPT-5.4 tie for the lead at 6.9939/10, which is below the proxy autonomy floor; GPT-5.4 Mini is the cheaper near-frontier option.
- Evidence status: `full_100_item_segment_pack_scored_curated_panel`
- Eval pack: `eval_packs/routine_planning_recommendation/pack.json`
- Human review expected: `true`
- Human review boundary: Only for high inventory value, low confidence, or irreversible actions.
- Deterministic controls: Inventory cover, margin, pack, timing, and stockout-censoring checks.

| Top Scored Models | Score | Artifact Cost |
| :--- | ---: | ---: |
| `GPT-5.4` | 6.9939/10 | $0.7420 |
| `GPT-5.5` | 6.9939/10 | $1.3371 |
| `GPT-5.4 Mini` | 6.7273/10 | $0.1725 |
| `GPT-5 Mini` | 6.1939/10 | $0.1439 |
| `Qwen3 32B` | 6.0985/10 | $0 |

### Pricing & promo

- Recommended route: GPT-5.5 or GPT-5.4 with margin and vendor-funding controls; human review for material decisions.
- Rationale: GPT-5.5 leads pricing/promotion at 6.7780/10, but no model clears the 7.0 proxy autonomy floor.
- Evidence status: `full_100_item_segment_pack_scored_curated_panel`
- Eval pack: `eval_packs/pricing_promotion/pack.json`
- Human review expected: `true`
- Human review boundary: Yes for material price moves, below-floor margin, or high competitive-response uncertainty.
- Deterministic controls: Margin floor, vendor funding, inventory cover, pull-forward, and competitor response checks.

| Top Scored Models | Score | Artifact Cost |
| :--- | ---: | ---: |
| `GPT-5.5` | 6.778/10 | $1.3371 |
| `GPT-5.4` | 6.4629/10 | $0.7420 |
| `GPT-5.4 Mini` | 6.3379/10 | $0.1725 |
| `GPT-5 Mini` | 5.6587/10 | $0.1439 |
| `Z.ai GLM 4.7` | 5.0314/10 | $0 |

### Ambiguous judgment

- Recommended route: GPT-5.4 for ambiguous judgment; GPT-5.4 Mini when the decision is reversible and well-guardrailed.
- Rationale: GPT-5.4 leads at 8.5311/10; GPT-5.5 is second at 7.7152/10 and Z.ai GLM 4.7 is the strongest free hosted comparator at 7.4038/10.
- Evidence status: `full_100_item_segment_pack_scored_curated_panel`
- Eval pack: `eval_packs/ambiguous_planning_judgment/pack.json`
- Human review expected: `true`
- Human review boundary: Recommended for vendor commitments, high markdown risk, or executive-pressure cases.
- Deterministic controls: Evidence contamination, OTB, lead time, margin, opportunity cost, and confidence gates.

| Top Scored Models | Score | Artifact Cost |
| :--- | ---: | ---: |
| `GPT-5.4` | 8.5311/10 | $0.7420 |
| `GPT-5.5` | 7.7152/10 | $1.3371 |
| `Z.ai GLM 4.7` | 7.4038/10 | $0 |
| `GPT-5.4 Mini` | 7.3076/10 | $0.1725 |
| `GPT-OSS 120B` | 6.5197/10 | $0 |

### Portfolio tradeoff

- Recommended route: GPT-5 Mini or GPT-5.4 Mini plus human review.
- Rationale: GPT-5 Mini narrowly leads at 8.0774/10, with GPT-5.4 Mini close at 8.0008/10; cross-category OTB decisions remain high-downside.
- Evidence status: `full_100_item_segment_pack_scored_curated_panel`
- Eval pack: `eval_packs/portfolio_tradeoff/pack.json`
- Human review expected: `true`
- Human review boundary: Yes. This should not be fully autonomous in the current evidence base.
- Deterministic controls: Portfolio OTB, opportunity cost, receiving capacity, leadership override, and customer-trust gates.

| Top Scored Models | Score | Artifact Cost |
| :--- | ---: | ---: |
| `GPT-5 Mini` | 8.0774/10 | $0.1439 |
| `GPT-5.4 Mini` | 8.0008/10 | $0.1725 |
| `Z.ai GLM 4.7` | 7.5106/10 | $0 |
| `GPT-5 Nano` | 7.1717/10 | $0.0140 |
| `GPT-5.5` | 7.097/10 | $1.3371 |

### Ops triage

- Recommended route: GPT-5.4 Mini for normal exceptions; GPT-5.5 or human review for safety/customer-trust risk.
- Rationale: GPT-5.5 leads at 7.5235/10; GPT-5.4 remains close at 7.2776/10, and GPT-5.4 Mini is the cheaper near-frontier option at 6.8261/10.
- Evidence status: `full_100_item_segment_pack_scored_curated_panel`
- Eval pack: `eval_packs/operational_triage/pack.json`
- Human review expected: `true`
- Human review boundary: Yes when safety, legal, public commitment, or customer-trust exposure appears.
- Deterministic controls: Safety, labor capacity, service-level, compliance, and owner-routing checks.

| Top Scored Models | Score | Artifact Cost |
| :--- | ---: | ---: |
| `GPT-5.5` | 7.5235/10 | $1.3371 |
| `GPT-5.4` | 7.2776/10 | $0.7420 |
| `GPT-5.4 Mini` | 6.8261/10 | $0.1725 |
| `Z.ai GLM 4.7` | 5.9011/10 | $0 |
| `Qwen3 32B` | 5.6182/10 | $0 |
