# Segment Eval Pack Scores

Automated deterministic contract scoring over must_include, must_not_include, output contract fields, escalation agreement, and anti-echo penalties. This is a bootstrap scorer for baselines and model-run triage, not a substitute for final human calibration.

| Model | Overall Avg | Scored Coverage | Attempted Calls | Provider Failures | Packs Passing |
| :--- | ---: | ---: | ---: | ---: | ---: |
| `cerebras/zai-glm-4.7` | 6.8471/10 | 100/100 | 100 | 0 | 0/8 |

## Segment Detail

### `cerebras/zai-glm-4.7`

| Segment | Avg | Scored Coverage | Attempted Calls | Provider Failures | Item Passes | Pack Pass |
| :--- | ---: | ---: | ---: | ---: | ---: | :--- |
| `ambiguous_planning_judgment` | 7.4038/10 | 11/11 | 11 | 0 | 5/11 | No |
| `constraint_checking` | 7.114/10 | 11/11 | 11 | 0 | 3/11 | No |
| `low_risk_summarization` | 7.3941/10 | 17/17 | 17 | 0 | 8/17 | No |
| `operational_triage` | 5.9011/10 | 11/11 | 11 | 0 | 2/11 | No |
| `portfolio_tradeoff` | 7.5106/10 | 11/11 | 11 | 0 | 4/11 | No |
| `pricing_promotion` | 5.0314/10 | 11/11 | 11 | 0 | 1/11 | No |
| `routine_planning_recommendation` | 5.9394/10 | 11/11 | 11 | 0 | 4/11 | No |
| `structured_extraction` | 7.7122/10 | 17/17 | 17 | 0 | 7/17 | No |
