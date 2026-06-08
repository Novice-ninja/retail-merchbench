# Retail MerchBench Launch

## What Is MerchBench?

Retail MerchBench is a retail AI benchmark for deciding which model or workflow tier is economically right for each retail decision. It evaluates 100 merchandise-planning tasks across summarization, extraction, constraints, routine planning, pricing, ambiguous judgment, portfolio tradeoffs, and operational triage.

The core idea: do not route every retail workflow to the biggest model. Use the cheapest safe workflow that clears the quality floor, escalates risky cases, and keeps human review where the downside is material.

## How To Reproduce?

```bash
git clone https://github.com/Novice-ninja/retail-merchbench.git
cd retail-merchbench
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
make reproduce
```

Open `reports/atlas/index.html`, `reports/atlas/report.md`, and `paper/retail_merchbench.pdf`.

## How To Contribute In 30 Minutes?

1. Fork the repo.
2. Run one model on a small smoke test:

```bash
python3 -m merchbench.cli eval-pack-provider \
  --provider ollama \
  --models llama3.2:3b \
  --max-items 1 \
  --resume \
  --unload-after-item
```

3. Open a PR with the stored response artifact, propose a retail eval case, or challenge the scorer with a concrete failure case.
