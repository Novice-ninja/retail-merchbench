# Segment Eval Pack Scores

Automated deterministic contract scoring over must_include, must_not_include, output contract fields, escalation agreement, and anti-echo penalties. This is a bootstrap scorer for baselines and model-run triage, not a substitute for final human calibration.

| Model | Overall Avg | Scored Coverage | Attempted Calls | Provider Failures | Packs Passing |
| :--- | ---: | ---: | ---: | ---: | ---: |
| `groq/llama-3.3-70b-versatile` | 4.835/10 | 100/100 | 100 | 0 | 0/8 |

## Segment Detail

### `groq/llama-3.3-70b-versatile`

| Segment | Avg | Scored Coverage | Attempted Calls | Provider Failures | Item Passes | Pack Pass |
| :--- | ---: | ---: | ---: | ---: | ---: | :--- |
| `ambiguous_planning_judgment` | 2.0273/10 | 11/11 | 11 | 0 | 0/11 | No |
| `constraint_checking` | 3.9057/10 | 11/11 | 11 | 0 | 0/11 | No |
| `low_risk_summarization` | 6.5354/10 | 17/17 | 17 | 0 | 5/17 | No |
| `operational_triage` | 5.3125/10 | 11/11 | 11 | 0 | 0/11 | No |
| `portfolio_tradeoff` | 5.8927/10 | 11/11 | 11 | 0 | 2/11 | No |
| `pricing_promotion` | 3.0943/10 | 11/11 | 11 | 0 | 0/11 | No |
| `routine_planning_recommendation` | 3.5682/10 | 11/11 | 11 | 0 | 1/11 | No |
| `structured_extraction` | 6.5056/10 | 17/17 | 17 | 0 | 5/17 | No |
