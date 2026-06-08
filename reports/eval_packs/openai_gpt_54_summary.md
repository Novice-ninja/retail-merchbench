# Segment Eval Pack Scores

Automated deterministic contract scoring over must_include, must_not_include, output contract fields, escalation agreement, and anti-echo penalties. This is a bootstrap scorer for baselines and model-run triage, not a substitute for final human calibration.

| Model | Overall Avg | Scored Coverage | Attempted Calls | Provider Failures | Packs Passing |
| :--- | ---: | ---: | ---: | ---: | ---: |
| `openai/gpt-5.4` | 7.3907/10 | 100/100 | 100 | 0 | 0/8 |

## Segment Detail

### `openai/gpt-5.4`

| Segment | Avg | Scored Coverage | Attempted Calls | Provider Failures | Item Passes | Pack Pass |
| :--- | ---: | ---: | ---: | ---: | ---: | :--- |
| `ambiguous_planning_judgment` | 8.5311/10 | 11/11 | 11 | 0 | 7/11 | No |
| `constraint_checking` | 8.2879/10 | 11/11 | 11 | 0 | 7/11 | No |
| `low_risk_summarization` | 7.5713/10 | 17/17 | 17 | 0 | 9/17 | No |
| `operational_triage` | 7.2776/10 | 11/11 | 11 | 0 | 5/11 | No |
| `portfolio_tradeoff` | 5.4391/10 | 11/11 | 11 | 0 | 0/11 | No |
| `pricing_promotion` | 6.4629/10 | 11/11 | 11 | 0 | 3/11 | No |
| `routine_planning_recommendation` | 6.9939/10 | 11/11 | 11 | 0 | 6/11 | No |
| `structured_extraction` | 8.0848/10 | 17/17 | 17 | 0 | 10/17 | No |
