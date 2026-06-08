# Segment Eval Pack Scores

Automated deterministic contract scoring over must_include, must_not_include, output contract fields, escalation agreement, and anti-echo penalties. This is a bootstrap scorer for baselines and model-run triage, not a substitute for final human calibration.

| Model | Overall Avg | Scored Coverage | Attempted Calls | Provider Failures | Packs Passing |
| :--- | ---: | ---: | ---: | ---: | ---: |
| `cerebras/gpt-oss-120b` | 5.978/10 | 100/100 | 100 | 0 | 0/8 |

## Segment Detail

### `cerebras/gpt-oss-120b`

| Segment | Avg | Scored Coverage | Attempted Calls | Provider Failures | Item Passes | Pack Pass |
| :--- | ---: | ---: | ---: | ---: | ---: | :--- |
| `ambiguous_planning_judgment` | 6.5197/10 | 11/11 | 11 | 0 | 5/11 | No |
| `constraint_checking` | 5.7614/10 | 11/11 | 11 | 0 | 0/11 | No |
| `low_risk_summarization` | 6.779/10 | 17/17 | 17 | 0 | 4/17 | No |
| `operational_triage` | 5.1057/10 | 11/11 | 11 | 0 | 0/11 | No |
| `portfolio_tradeoff` | 6.772/10 | 11/11 | 11 | 0 | 2/11 | No |
| `pricing_promotion` | 3.9955/10 | 11/11 | 11 | 0 | 0/11 | No |
| `routine_planning_recommendation` | 5.8788/10 | 11/11 | 11 | 0 | 4/11 | No |
| `structured_extraction` | 6.3645/10 | 17/17 | 17 | 0 | 4/17 | No |
