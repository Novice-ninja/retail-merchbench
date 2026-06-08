# Segment Eval Pack Scores

Automated deterministic contract scoring over must_include, must_not_include, output contract fields, escalation agreement, and anti-echo penalties. This is a bootstrap scorer for baselines and model-run triage, not a substitute for final human calibration.

| Model | Overall Avg | Scored Coverage | Attempted Calls | Provider Failures | Packs Passing |
| :--- | ---: | ---: | ---: | ---: | ---: |
| `baseline/source_echo` | 3.353/10 | 100/100 | 100 | 0 | 0/8 |
| `baseline/keyword_guardrail` | 4.328/10 | 100/100 | 100 | 0 | 0/8 |
| `baseline/generic_consultant` | 3.3424/10 | 100/100 | 100 | 0 | 0/8 |
| `baseline/always_escalate` | 4.0504/10 | 100/100 | 100 | 0 | 0/8 |
| `baseline/always_buy_chase` | 3.5574/10 | 100/100 | 100 | 0 | 0/8 |
| `baseline/always_conservative` | 3.1884/10 | 100/100 | 100 | 0 | 0/8 |
| `baseline/arithmetic_only` | 3.7469/10 | 100/100 | 100 | 0 | 0/8 |

## Segment Detail

### `baseline/source_echo`

| Segment | Avg | Scored Coverage | Attempted Calls | Provider Failures | Item Passes | Pack Pass |
| :--- | ---: | ---: | ---: | ---: | ---: | :--- |
| `ambiguous_planning_judgment` | 3.1/10 | 11/11 | 11 | 0 | 0/11 | No |
| `constraint_checking` | 3.4864/10 | 11/11 | 11 | 0 | 0/11 | No |
| `low_risk_summarization` | 4.0/10 | 17/17 | 17 | 0 | 0/17 | No |
| `operational_triage` | 4.0/10 | 11/11 | 11 | 0 | 0/11 | No |
| `portfolio_tradeoff` | 2.9/10 | 11/11 | 11 | 0 | 0/11 | No |
| `pricing_promotion` | 2.2136/10 | 11/11 | 11 | 0 | 0/11 | No |
| `routine_planning_recommendation` | 3.1818/10 | 11/11 | 11 | 0 | 0/11 | No |
| `structured_extraction` | 3.5059/10 | 17/17 | 17 | 0 | 0/17 | No |

### `baseline/keyword_guardrail`

| Segment | Avg | Scored Coverage | Attempted Calls | Provider Failures | Item Passes | Pack Pass |
| :--- | ---: | ---: | ---: | ---: | ---: | :--- |
| `ambiguous_planning_judgment` | 4.6727/10 | 11/11 | 11 | 0 | 0/11 | No |
| `constraint_checking` | 3.4864/10 | 11/11 | 11 | 0 | 0/11 | No |
| `low_risk_summarization` | 4.9824/10 | 17/17 | 17 | 0 | 0/17 | No |
| `operational_triage` | 5.0/10 | 11/11 | 11 | 0 | 0/11 | No |
| `portfolio_tradeoff` | 4.3636/10 | 11/11 | 11 | 0 | 0/11 | No |
| `pricing_promotion` | 3.6648/10 | 11/11 | 11 | 0 | 0/11 | No |
| `routine_planning_recommendation` | 4.2212/10 | 11/11 | 11 | 0 | 0/11 | No |
| `structured_extraction` | 4.0355/10 | 17/17 | 17 | 0 | 0/17 | No |

### `baseline/generic_consultant`

| Segment | Avg | Scored Coverage | Attempted Calls | Provider Failures | Item Passes | Pack Pass |
| :--- | ---: | ---: | ---: | ---: | ---: | :--- |
| `ambiguous_planning_judgment` | 3.3182/10 | 11/11 | 11 | 0 | 0/11 | No |
| `constraint_checking` | 3.05/10 | 11/11 | 11 | 0 | 0/11 | No |
| `low_risk_summarization` | 4.0/10 | 17/17 | 17 | 0 | 0/17 | No |
| `operational_triage` | 3.7045/10 | 11/11 | 11 | 0 | 0/11 | No |
| `portfolio_tradeoff` | 2.7036/10 | 11/11 | 11 | 0 | 0/11 | No |
| `pricing_promotion` | 2.8727/10 | 11/11 | 11 | 0 | 0/11 | No |
| `routine_planning_recommendation` | 3.2955/10 | 11/11 | 11 | 0 | 0/11 | No |
| `structured_extraction` | 3.4029/10 | 17/17 | 17 | 0 | 0/17 | No |

### `baseline/always_escalate`

| Segment | Avg | Scored Coverage | Attempted Calls | Provider Failures | Item Passes | Pack Pass |
| :--- | ---: | ---: | ---: | ---: | ---: | :--- |
| `ambiguous_planning_judgment` | 3.8091/10 | 11/11 | 11 | 0 | 0/11 | No |
| `constraint_checking` | 3.85/10 | 11/11 | 11 | 0 | 0/11 | No |
| `low_risk_summarization` | 4.6176/10 | 17/17 | 17 | 0 | 0/17 | No |
| `operational_triage` | 5.0727/10 | 11/11 | 11 | 0 | 0/11 | No |
| `portfolio_tradeoff` | 4.4036/10 | 11/11 | 11 | 0 | 0/11 | No |
| `pricing_promotion` | 3.35/10 | 11/11 | 11 | 0 | 0/11 | No |
| `routine_planning_recommendation` | 3.7182/10 | 11/11 | 11 | 0 | 0/11 | No |
| `structured_extraction` | 3.5471/10 | 17/17 | 17 | 0 | 0/17 | No |

### `baseline/always_buy_chase`

| Segment | Avg | Scored Coverage | Attempted Calls | Provider Failures | Item Passes | Pack Pass |
| :--- | ---: | ---: | ---: | ---: | ---: | :--- |
| `ambiguous_planning_judgment` | 3.3727/10 | 11/11 | 11 | 0 | 0/11 | No |
| `constraint_checking` | 3.4455/10 | 11/11 | 11 | 0 | 0/11 | No |
| `low_risk_summarization` | 4.1176/10 | 17/17 | 17 | 0 | 0/17 | No |
| `operational_triage` | 3.7159/10 | 11/11 | 11 | 0 | 0/11 | No |
| `portfolio_tradeoff` | 3.0923/10 | 11/11 | 11 | 0 | 0/11 | No |
| `pricing_promotion` | 3.3261/10 | 11/11 | 11 | 0 | 0/11 | No |
| `routine_planning_recommendation` | 3.2955/10 | 11/11 | 11 | 0 | 0/11 | No |
| `structured_extraction` | 3.7064/10 | 17/17 | 17 | 0 | 0/17 | No |

### `baseline/always_conservative`

| Segment | Avg | Scored Coverage | Attempted Calls | Provider Failures | Item Passes | Pack Pass |
| :--- | ---: | ---: | ---: | ---: | ---: | :--- |
| `ambiguous_planning_judgment` | 2.3727/10 | 11/11 | 11 | 0 | 0/11 | No |
| `constraint_checking` | 3.05/10 | 11/11 | 11 | 0 | 0/11 | No |
| `low_risk_summarization` | 4.0588/10 | 17/17 | 17 | 0 | 0/17 | No |
| `operational_triage` | 3.9773/10 | 11/11 | 11 | 0 | 0/11 | No |
| `portfolio_tradeoff` | 2.7036/10 | 11/11 | 11 | 0 | 0/11 | No |
| `pricing_promotion` | 2.8727/10 | 11/11 | 11 | 0 | 0/11 | No |
| `routine_planning_recommendation` | 2.4773/10 | 11/11 | 11 | 0 | 0/11 | No |
| `structured_extraction` | 3.4029/10 | 17/17 | 17 | 0 | 0/17 | No |

### `baseline/arithmetic_only`

| Segment | Avg | Scored Coverage | Attempted Calls | Provider Failures | Item Passes | Pack Pass |
| :--- | ---: | ---: | ---: | ---: | ---: | :--- |
| `ambiguous_planning_judgment` | 3.5409/10 | 11/11 | 11 | 0 | 0/11 | No |
| `constraint_checking` | 3.8352/10 | 11/11 | 11 | 0 | 0/11 | No |
| `low_risk_summarization` | 3.8696/10 | 17/17 | 17 | 0 | 0/17 | No |
| `operational_triage` | 5.0/10 | 11/11 | 11 | 0 | 0/11 | No |
| `portfolio_tradeoff` | 3.3536/10 | 11/11 | 11 | 0 | 0/11 | No |
| `pricing_promotion` | 2.908/10 | 11/11 | 11 | 0 | 0/11 | No |
| `routine_planning_recommendation` | 3.1818/10 | 11/11 | 11 | 0 | 0/11 | No |
| `structured_extraction` | 4.0527/10 | 17/17 | 17 | 0 | 0/17 | No |
