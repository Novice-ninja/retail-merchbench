# Segment Eval Pack Scores

Automated deterministic contract scoring over must_include, must_not_include, output contract fields, escalation agreement, and anti-echo penalties. This is a bootstrap scorer for baselines and model-run triage, not a substitute for final human calibration.

| Model | Overall Avg | Scored Coverage | Attempted Calls | Provider Failures | Packs Passing |
| :--- | ---: | ---: | ---: | ---: | ---: |
| `openai/gpt-5-nano` | 5.7188/10 | 100/100 | 100 | 0 | 0/8 |

## Segment Detail

### `openai/gpt-5-nano`

| Segment | Avg | Scored Coverage | Attempted Calls | Provider Failures | Item Passes | Pack Pass |
| :--- | ---: | ---: | ---: | ---: | ---: | :--- |
| `ambiguous_planning_judgment` | 3.5947/10 | 11/11 | 11 | 0 | 1/11 | No |
| `constraint_checking` | 6.0966/10 | 11/11 | 11 | 0 | 1/11 | No |
| `low_risk_summarization` | 6.6173/10 | 17/17 | 17 | 0 | 4/17 | No |
| `operational_triage` | 3.7318/10 | 11/11 | 11 | 0 | 0/11 | No |
| `portfolio_tradeoff` | 7.1717/10 | 11/11 | 11 | 0 | 4/11 | No |
| `pricing_promotion` | 4.7019/10 | 11/11 | 11 | 0 | 2/11 | No |
| `routine_planning_recommendation` | 5.9735/10 | 11/11 | 11 | 0 | 3/11 | No |
| `structured_extraction` | 6.7889/10 | 17/17 | 17 | 0 | 6/17 | No |
