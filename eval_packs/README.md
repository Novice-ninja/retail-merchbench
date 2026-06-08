# Segment Eval Packs

Segment eval packs are Retail MerchBench's task-class evals for economic model routing. Each pack targets a workflow class that can justify a different model tier, deterministic control, cascade, or human-review boundary.

Each pack defines:

- The retail task segment and strategy under test.
- A coverage matrix across categories, retail functions, ambiguity sources, externalities, and escalation patterns.
- A strict output contract for future model runners.
- Objective scoring dimensions and quality floors.
- A set of retail-native question items with expected outputs, deterministic checks, and escalation triggers.

Current packs:

| Segment | Pack | Strategy Under Test | Status |
| :--- | :--- | :--- | :--- |
| `low_risk_summarization` | `low_risk_summarization/pack.json` | `small_model` | 17 items |
| `structured_extraction` | `structured_extraction/pack.json` | `rules_only` with `small_model` fallback | 17 items |
| `constraint_checking` | `constraint_checking/pack.json` | `rules_only` | 11 items |
| `routine_planning_recommendation` | `routine_planning_recommendation/pack.json` | `mid_model` | 11 items |
| `pricing_promotion` | `pricing_promotion/pack.json` | `mid_model` | 11 items |
| `ambiguous_planning_judgment` | `ambiguous_planning_judgment/pack.json` | `frontier_model` | 11 items |
| `portfolio_tradeoff` | `portfolio_tradeoff/pack.json` | `frontier_plus_human_review` | 11 items |
| `operational_triage` | `operational_triage/pack.json` | `cascade` | 11 items |

The suite currently contains 100 eval items. Deterministic baselines and the curated provider-backed panel now cover the full `100/100` corpus for 14 real models across local Ollama, hosted Groq/Cerebras, and paid OpenAI runs. OpenRouter free-tier probes are intentionally marked partial because the daily free-model cap was reached; xAI is documented as unavailable until the account has credits or a license.

Run the local deterministic baselines with:

```bash
make eval-pack-baselines
```

The current baseline runner writes:

- `reports/eval_packs/baseline_responses.json`
- `reports/eval_packs/baseline_scores.json`
- `reports/eval_packs/baseline_summary.md`
- `reports/eval_packs/scorer_robustness.md`

Score any future model response file with:

```bash
python3 -m merchbench.cli eval-pack-score \
  --responses path/to/model_responses.json \
  --output-scores reports/eval_packs/model_scores.json \
  --output-summary reports/eval_packs/model_summary.md
```

The response file should use the same shape as `baseline_responses.json`: top-level `models`, then model IDs, then `packs`, pack IDs, item IDs, and a `content` object for each response.

Dry-run the OpenRouter model runner without credentials:

```bash
make eval-pack-openrouter-dry-run
```

Run OpenRouter calls once `.env.local` has `OPENROUTER_API_KEY`:

```bash
python3 -m merchbench.cli eval-pack-openrouter \
  --models liquid/lfm-2.5-1.2b-instruct:free nvidia/nemotron-nano-9b-v2:free poolside/laguna-xs.2:free \
  --items-per-pack 1 \
  --resume
```

Use `--items-per-pack` for quota-aware balanced probes across every segment, then remove it for full-suite runs once paid credits are available. The OpenRouter runner writes response, score, summary, and manifest files under `reports/eval_packs/` using the `openrouter_*.json` and `openrouter_*.md` names. Those files are ignored by default until a run is intentionally curated.

## Design Bar

These packs should separate models on economic usefulness, not just generic language quality:

- Retail context must be realistic enough that mistakes map to operational risk.
- Inputs must include noisy source material, conflicting values, or missing fields where the segment naturally encounters them.
- Tasks must specify when the model should refuse to make a recommendation or escalate.
- Scoring must reward exact values, source fidelity, schema compliance, and escalation discipline.
- Deterministic checks should remain explicit so rules-only or hybrid workflows can be evaluated fairly against LLM-only workflows.
