# Segment Eval Pack Scores

Automated deterministic contract scoring over must_include, must_not_include, output contract fields, escalation agreement, and anti-echo penalties. This is a bootstrap scorer for baselines and model-run triage, not a substitute for final human calibration.

| Model | Overall Avg | Scored Coverage | Attempted Calls | Provider Failures | Packs Passing |
| :--- | ---: | ---: | ---: | ---: | ---: |
| `openai/gpt-5.5` | 7.4614/10 | 100/100 | 100 | 0 | 0/8 |

## Segment Detail

### `openai/gpt-5.5`

| Segment | Avg | Scored Coverage | Attempted Calls | Provider Failures | Item Passes | Pack Pass |
| :--- | ---: | ---: | ---: | ---: | ---: | :--- |
| `ambiguous_planning_judgment` | 7.7152/10 | 11/11 | 11 | 0 | 5/11 | No |
| `constraint_checking` | 7.8349/10 | 11/11 | 11 | 0 | 6/11 | No |
| `low_risk_summarization` | 7.0825/10 | 17/17 | 17 | 0 | 6/17 | No |
| `operational_triage` | 7.5235/10 | 11/11 | 11 | 0 | 6/11 | No |
| `portfolio_tradeoff` | 7.097/10 | 11/11 | 11 | 0 | 4/11 | No |
| `pricing_promotion` | 6.778/10 | 11/11 | 11 | 0 | 4/11 | No |
| `routine_planning_recommendation` | 6.9939/10 | 11/11 | 11 | 0 | 6/11 | No |
| `structured_extraction` | 8.3748/10 | 17/17 | 17 | 0 | 11/17 | No |
