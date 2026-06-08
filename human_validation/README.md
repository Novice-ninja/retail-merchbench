# Human Validation

This folder contains the first blind human-rater package for MerchBench.

Generate or refresh the package with:

```bash
make human-validation-subset
```

Files:

- `rater_subset.json`: 24-item blind subset, with anonymous responses.
- `ratings_template.csv`: fillable rating table for retail practitioners.
- `rater_answer_key.json`: internal mapping from anonymous response IDs to model IDs. Do not share this with raters.
- `rating_form.md`: plain-language scoring form and instructions.

Analyze completed ratings with:

```bash
python3 analysis/analyze_human_ratings.py \
  --ratings human_validation/ratings_template.csv
```

No human-score claims should be published until real ratings are collected and the analysis output is reviewed.
