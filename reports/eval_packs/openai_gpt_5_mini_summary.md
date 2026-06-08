# Segment Eval Pack Scores

Automated deterministic contract scoring over must_include, must_not_include, output contract fields, escalation agreement, and anti-echo penalties. This is a bootstrap scorer for baselines and model-run triage, not a substitute for final human calibration.

| Model | Overall Avg | Scored Coverage | Attempted Calls | Provider Failures | Packs Passing |
| :--- | ---: | ---: | ---: | ---: | ---: |
| `openai/gpt-5-mini` | 7.0175/10 | 100/100 | 100 | 0 | 0/8 |

## Segment Detail

### `openai/gpt-5-mini`

| Segment | Avg | Scored Coverage | Attempted Calls | Provider Failures | Item Passes | Pack Pass |
| :--- | ---: | ---: | ---: | ---: | ---: | :--- |
| `ambiguous_planning_judgment` | 5.6636/10 | 11/11 | 11 | 0 | 1/11 | No |
| `constraint_checking` | 7.7792/10 | 11/11 | 11 | 0 | 6/11 | No |
| `low_risk_summarization` | 8.0696/10 | 17/17 | 17 | 0 | 12/17 | No |
| `operational_triage` | 4.7072/10 | 11/11 | 11 | 0 | 0/11 | No |
| `portfolio_tradeoff` | 8.0774/10 | 11/11 | 11 | 0 | 6/11 | No |
| `pricing_promotion` | 5.6587/10 | 11/11 | 11 | 0 | 0/11 | No |
| `routine_planning_recommendation` | 6.1939/10 | 11/11 | 11 | 0 | 4/11 | No |
| `structured_extraction` | 8.57/10 | 17/17 | 17 | 0 | 12/17 | No |
