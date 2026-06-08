# Segment Eval Pack Scores

Automated deterministic contract scoring over must_include, must_not_include, output contract fields, escalation agreement, and anti-echo penalties. This is a bootstrap scorer for baselines and model-run triage, not a substitute for final human calibration.

| Model | Overall Avg | Scored Coverage | Attempted Calls | Provider Failures | Packs Passing |
| :--- | ---: | ---: | ---: | ---: | ---: |
| `ollama/gemma4:e2b` | 3.4145/10 | 100/100 | 100 | 0 | 0/8 |
| `ollama/lfm2.5-thinking:1.2b` | 2.3328/10 | 100/100 | 100 | 0 | 0/8 |
| `ollama/llama3.2:3b` | 3.2148/10 | 100/100 | 100 | 0 | 0/8 |

## Segment Detail

### `ollama/gemma4:e2b`

| Segment | Avg | Scored Coverage | Attempted Calls | Provider Failures | Item Passes | Pack Pass |
| :--- | ---: | ---: | ---: | ---: | ---: | :--- |
| `ambiguous_planning_judgment` | 3.3545/10 | 11/11 | 11 | 0 | 1/11 | No |
| `constraint_checking` | 2.1402/10 | 11/11 | 11 | 0 | 0/11 | No |
| `low_risk_summarization` | 3.7362/10 | 17/17 | 17 | 0 | 1/17 | No |
| `operational_triage` | 3.5648/10 | 11/11 | 11 | 0 | 3/11 | No |
| `portfolio_tradeoff` | 3.6309/10 | 11/11 | 11 | 0 | 1/11 | No |
| `pricing_promotion` | 1.8917/10 | 11/11 | 11 | 0 | 0/11 | No |
| `routine_planning_recommendation` | 2.9591/10 | 11/11 | 11 | 0 | 1/11 | No |
| `structured_extraction` | 4.9989/10 | 17/17 | 17 | 0 | 3/17 | No |

### `ollama/lfm2.5-thinking:1.2b`

| Segment | Avg | Scored Coverage | Attempted Calls | Provider Failures | Item Passes | Pack Pass |
| :--- | ---: | ---: | ---: | ---: | ---: | :--- |
| `ambiguous_planning_judgment` | 2.0091/10 | 11/11 | 11 | 0 | 0/11 | No |
| `constraint_checking` | 1.6864/10 | 11/11 | 11 | 0 | 0/11 | No |
| `low_risk_summarization` | 2.9962/10 | 17/17 | 17 | 0 | 0/17 | No |
| `operational_triage` | 2.2943/10 | 11/11 | 11 | 0 | 0/11 | No |
| `portfolio_tradeoff` | 2.3218/10 | 11/11 | 11 | 0 | 0/11 | No |
| `pricing_promotion` | 1.7102/10 | 11/11 | 11 | 0 | 0/11 | No |
| `routine_planning_recommendation` | 2.3273/10 | 11/11 | 11 | 0 | 1/11 | No |
| `structured_extraction` | 2.7353/10 | 17/17 | 17 | 0 | 0/17 | No |

### `ollama/llama3.2:3b`

| Segment | Avg | Scored Coverage | Attempted Calls | Provider Failures | Item Passes | Pack Pass |
| :--- | ---: | ---: | ---: | ---: | ---: | :--- |
| `ambiguous_planning_judgment` | 2.4636/10 | 11/11 | 11 | 0 | 0/11 | No |
| `constraint_checking` | 3.542/10 | 11/11 | 11 | 0 | 0/11 | No |
| `low_risk_summarization` | 3.7838/10 | 17/17 | 17 | 0 | 1/17 | No |
| `operational_triage` | 3.7318/10 | 11/11 | 11 | 0 | 0/11 | No |
| `portfolio_tradeoff` | 2.5673/10 | 11/11 | 11 | 0 | 0/11 | No |
| `pricing_promotion` | 1.7705/10 | 11/11 | 11 | 0 | 0/11 | No |
| `routine_planning_recommendation` | 1.9841/10 | 11/11 | 11 | 0 | 0/11 | No |
| `structured_extraction` | 4.7354/10 | 17/17 | 17 | 0 | 1/17 | No |
