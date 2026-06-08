# Routing Reports

This directory stores generated non-visual routing recommendations. These are backend policy-handoff artifacts generated from the current segment eval-pack score files.

The executive-facing artifact is the Atlas in `reports/atlas/`. It uses the same 100-item scored provider panel and presents the recommendations as model-frontier visuals, heatmaps, and segment cards.

Regenerate with:

```bash
make routing-report
```
