# Segment Eval Pack Scores

Automated deterministic contract scoring over must_include, must_not_include, output contract fields, escalation agreement, and anti-echo penalties. This is a bootstrap scorer for baselines and model-run triage, not a substitute for final human calibration.

| Model | Overall Avg | Scored Coverage | Attempted Calls | Provider Failures | Packs Passing |
| :--- | ---: | ---: | ---: | ---: | ---: |
| `openai/gpt-5.4-mini` | 7.3693/10 | 100/100 | 100 | 0 | 0/8 |

## Segment Detail

### `openai/gpt-5.4-mini`

| Segment | Avg | Scored Coverage | Attempted Calls | Provider Failures | Item Passes | Pack Pass |
| :--- | ---: | ---: | ---: | ---: | ---: | :--- |
| `ambiguous_planning_judgment` | 7.3076/10 | 11/11 | 11 | 0 | 5/11 | No |
| `constraint_checking` | 7.1076/10 | 11/11 | 11 | 0 | 3/11 | No |
| `low_risk_summarization` | 7.5419/10 | 17/17 | 17 | 0 | 9/17 | No |
| `operational_triage` | 6.8261/10 | 11/11 | 11 | 0 | 5/11 | No |
| `portfolio_tradeoff` | 8.0008/10 | 11/11 | 11 | 0 | 6/11 | No |
| `pricing_promotion` | 6.3379/10 | 11/11 | 11 | 0 | 3/11 | No |
| `routine_planning_recommendation` | 6.7273/10 | 11/11 | 11 | 0 | 6/11 | No |
| `structured_extraction` | 8.4314/10 | 17/17 | 17 | 0 | 12/17 | No |
