PY ?= .venv/bin/python
A = PYTHONPATH=paper $(PY) -m analysis

all: harvest pull analysis paper readme

harvest:      # Every Limitless fill and AMM trade on Base. Fast with ENVIO_API_TOKEN in .env.
	$(PY) -m py.harvest_limitless
	$(PY) -m py.harvest_limitless_amm

pull:         # Who funded the large wallets, and where their USDC and the fees went. Needs ENVIO_API_TOKEN in .env.
	$(PY) -m py.pull_funders
	$(A).a06_limitless_clusters
	$(PY) -m py.pull_cluster_usdc_in
	$(PY) -m py.pull_fee_trail
	$(PY) -m py.safe_owners
	$(PY) -m py.pull_binance

analysis:
	$(A).a06_limitless_clusters
	$(A).a16_limitless_volume
	$(A).a17_limitless_claims
	$(A).a17_limitless_weekly
	$(A).a08_self_crossing
	$(A).a11_fee_timeline
	$(A).a06_limitless_flow
	$(A).a19_limitless_anatomy --groups 0:12
	$(A).a19_limitless_anatomy --groups 12:999
	$(A).a19_limitless_anatomy
	$(A).a19_amm_daily
	$(A).a19_market_example
	$(A).a21_fee_trail
	$(A).a06_limitless_figure
	$(A).a20_limitless_figures

paper:        # Needs tectonic (tectonic-typesetting.github.io).
	cd paper && tectonic limitless.tex

readme:
	$(PY) paper/tex2readme.py

.PHONY: all harvest pull analysis paper readme
