# Segment Eval Pack Scores

Automated deterministic contract scoring over must_include, must_not_include, output contract fields, escalation agreement, and anti-echo penalties. This is a bootstrap scorer for baselines and model-run triage, not a substitute for final human calibration.

| Model | Overall Avg | Scored Coverage | Attempted Calls | Provider Failures | Packs Passing |
| :--- | ---: | ---: | ---: | ---: | ---: |
| `openai/gpt-4.1-nano` | 5.1859/10 | 100/100 | 100 | 0 | 0/8 |

## Segment Detail

### `openai/gpt-4.1-nano`

| Segment | Avg | Scored Coverage | Attempted Calls | Provider Failures | Item Passes | Pack Pass |
| :--- | ---: | ---: | ---: | ---: | ---: | :--- |
| `ambiguous_planning_judgment` | 5.4356/10 | 11/11 | 11 | 0 | 1/11 | No |
| `constraint_checking` | 5.5216/10 | 11/11 | 11 | 0 | 1/11 | No |
| `low_risk_summarization` | 6.1035/10 | 17/17 | 17 | 0 | 2/17 | No |
| `operational_triage` | 5.1841/10 | 11/11 | 11 | 0 | 0/11 | No |
| `portfolio_tradeoff` | 6.4636/10 | 11/11 | 11 | 0 | 3/11 | No |
| `pricing_promotion` | 2.5091/10 | 11/11 | 11 | 0 | 0/11 | No |
| `routine_planning_recommendation` | 3.7894/10 | 11/11 | 11 | 0 | 0/11 | No |
| `structured_extraction` | 5.6997/10 | 17/17 | 17 | 0 | 2/17 | No |
