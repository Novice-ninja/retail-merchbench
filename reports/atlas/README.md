# Retail MerchBench Artifacts

This directory contains the current executive artifact package.

- `index.html`: visual Atlas.
- `report.md`: written report.
- `atlas_data.json`: structured data used by the Atlas and report.
- `model_frontier.svg`: quality-cost frontier.
- `segment_heatmap.svg`: OpenAI segment heatmap.
- `segment_quadrants.svg`: segment-level cost-quality 2x2 grid.
- `routing_ladder.svg`: workflow-tier routing ladder.
- `economic_regret.svg`: quality gap between segment quality leader and economic pick.

Regenerate with:

```bash
make atlas
```
