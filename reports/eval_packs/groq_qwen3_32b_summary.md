# Segment Eval Pack Scores

Automated deterministic contract scoring over must_include, must_not_include, output contract fields, escalation agreement, and anti-echo penalties. This is a bootstrap scorer for baselines and model-run triage, not a substitute for final human calibration.

| Model | Overall Avg | Scored Coverage | Attempted Calls | Provider Failures | Packs Passing |
| :--- | ---: | ---: | ---: | ---: | ---: |
| `groq/qwen/qwen3-32b` | 5.6355/10 | 100/100 | 100 | 0 | 0/8 |

## Segment Detail

### `groq/qwen/qwen3-32b`

| Segment | Avg | Scored Coverage | Attempted Calls | Provider Failures | Item Passes | Pack Pass |
| :--- | ---: | ---: | ---: | ---: | ---: | :--- |
| `ambiguous_planning_judgment` | 5.2833/10 | 11/11 | 11 | 0 | 3/11 | No |
| `constraint_checking` | 6.342/10 | 11/11 | 11 | 0 | 2/11 | No |
| `low_risk_summarization` | 7.1773/10 | 17/17 | 17 | 0 | 8/17 | No |
| `operational_triage` | 5.6182/10 | 11/11 | 11 | 0 | 0/11 | No |
| `portfolio_tradeoff` | 5.5845/10 | 11/11 | 11 | 0 | 2/11 | No |
| `pricing_promotion` | 4.3826/10 | 11/11 | 11 | 0 | 0/11 | No |
| `routine_planning_recommendation` | 6.0985/10 | 11/11 | 11 | 0 | 5/11 | No |
| `structured_extraction` | 4.4196/10 | 17/17 | 17 | 0 | 2/17 | No |
