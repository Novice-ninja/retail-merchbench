PYTHON ?= python3
export PYTHONDONTWRITEBYTECODE := 1

.PHONY: validate smoke-test reproduce atlas routing-report eval-pack-baselines eval-pack-score-stored human-validation-subset human-rating-analysis publication-metrics provider-ollama-dry-run provider-ollama-smoke

validate:
	$(PYTHON) -m harness.validate_repo

smoke-test: validate

reproduce: eval-pack-baselines eval-pack-score-stored routing-report atlas publication-metrics atlas human-validation-subset human-rating-analysis validate

atlas:
	$(PYTHON) analysis/generate_publication_atlas.py

routing-report:
	$(PYTHON) analysis/generate_routing_report.py

eval-pack-baselines:
	$(PYTHON) -m merchbench.cli eval-pack-baselines

eval-pack-score-stored:
	$(PYTHON) analysis/rescore_eval_pack_responses.py

human-validation-subset:
	$(PYTHON) analysis/build_human_validation_subset.py

human-rating-analysis:
	$(PYTHON) analysis/analyze_human_ratings.py

publication-metrics:
	$(PYTHON) analysis/generate_publication_metrics.py

provider-ollama-dry-run:
	$(PYTHON) -m merchbench.cli eval-pack-provider --provider ollama --dry-run --items-per-pack 1

provider-ollama-smoke:
	$(PYTHON) -m merchbench.cli eval-pack-provider --provider ollama --models llama3.2:3b --max-items 1 --resume --unload-after-item
