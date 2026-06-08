# MerchBench Human Rating Form

Use this form together with `rater_subset.json` and `ratings_template.csv`.

For each anonymous response, score every dimension from 1 to 5:

- 1: unsafe or materially wrong.
- 2: weak; misses important retail signal or control.
- 3: usable draft but requires meaningful correction.
- 4: strong; minor gaps or caveats.
- 5: retail-practitioner quality for the requested task.

## Dimensions

Evidence quality: Does the response identify valid, weak, missing, or contaminated evidence?

Problem framing: Does it answer the right retail question, including challenging a bad premise when needed?

Constraint handling: Does it respect OTB, MOQ, pack, margin, lead-time, channel, labor, capacity, compliance, or other deterministic controls?

Causal reasoning: Does it explain why the action follows from the evidence rather than repeating surface facts?

Uncertainty calibration: Does it match confidence to the quality and completeness of evidence?

Actionability: Is the recommendation or output usable for the requested workflow?

Economic risk: Does it avoid margin, inventory, customer-trust, opportunity-cost, or irreversible-decision errors?

Escalation appropriateness: Does it escalate high-downside or unresolved cases without over-escalating routine ones?

## Notes

Judge the answer against the task segment. A summary can be excellent without a recommendation. A pricing answer can be fluent and still unsafe if it misses margin, funding, MAP, or pull-forward risk.

Do not reward anonymous responses for style alone. Reward commercially correct retail judgment.
