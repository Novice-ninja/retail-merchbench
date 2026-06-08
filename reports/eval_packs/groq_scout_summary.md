# Segment Eval Pack Scores

Automated deterministic contract scoring over must_include, must_not_include, output contract fields, escalation agreement, and anti-echo penalties. This is a bootstrap scorer for baselines and model-run triage, not a substitute for final human calibration.

| Model | Overall Avg | Scored Coverage | Attempted Calls | Provider Failures | Packs Passing |
| :--- | ---: | ---: | ---: | ---: | ---: |
| `groq/meta-llama/llama-4-scout-17b-16e-instruct` | 5.3578/10 | 100/100 | 100 | 0 | 0/8 |

## Segment Detail

### `groq/meta-llama/llama-4-scout-17b-16e-instruct`

| Segment | Avg | Scored Coverage | Attempted Calls | Provider Failures | Item Passes | Pack Pass |
| :--- | ---: | ---: | ---: | ---: | ---: | :--- |
| `ambiguous_planning_judgment` | 3.8068/10 | 11/11 | 11 | 0 | 1/11 | No |
| `constraint_checking` | 5.6443/10 | 11/11 | 11 | 0 | 3/11 | No |
| `low_risk_summarization` | 6.7423/10 | 17/17 | 17 | 0 | 6/17 | No |
| `operational_triage` | 5.4034/10 | 11/11 | 11 | 0 | 0/11 | No |
| `portfolio_tradeoff` | 6.0091/10 | 11/11 | 11 | 0 | 3/11 | No |
| `pricing_promotion` | 3.3091/10 | 11/11 | 11 | 0 | 0/11 | No |
| `routine_planning_recommendation` | 4.9758/10 | 11/11 | 11 | 0 | 2/11 | No |
| `structured_extraction` | 5.9133/10 | 17/17 | 17 | 0 | 3/17 | No |
