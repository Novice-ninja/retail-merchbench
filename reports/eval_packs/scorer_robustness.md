# Scorer Robustness Check

This report tracks whether adversarial deterministic baselines still receive inflated scores after anti-echo scorer hardening.

| Baseline | Pre anti-echo avg | Current avg | Threshold | Status |
| :--- | ---: | ---: | ---: | :--- |
| `baseline/source_echo` | 7.7174 | 3.3530 | 4.5 | Pass |
| `baseline/keyword_guardrail` | 7.9124 | 4.3280 | 5.5 | Pass |
| `baseline/generic_consultant` | n/a | 3.3424 | n/a | Diagnostic only |
| `baseline/always_escalate` | n/a | 4.0504 | n/a | Diagnostic only |
| `baseline/always_buy_chase` | n/a | 3.5574 | n/a | Diagnostic only |
| `baseline/always_conservative` | n/a | 3.1884 | n/a | Diagnostic only |
| `baseline/arithmetic_only` | n/a | 3.7469 | n/a | Diagnostic only |

## Interpretation

- `baseline/source_echo` should no longer score like a competent planning answer just because source facts are present.
- `baseline/keyword_guardrail` should no longer pass by naming guardrail terms without causal or premise-challenge reasoning.
- The other adversarial baselines are diagnostic probes for generic, over-escalating, over-aggressive, over-conservative, and arithmetic-only behavior.
- Passing this check does not make the automated scorer human-calibrated; it only reduces the most visible deterministic baseline inflation.
