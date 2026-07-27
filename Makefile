.PHONY: dev check build web-install pipeline-install pipeline-test \
        data-collect data-validate data-release data-verify test

# ---- Web (Node only) ----
web-install:
	cd web && npm ci

dev:
	cd web && npm run dev

check:
	cd web && npm run check

build:
	cd web && npm run build

# ---- Pipeline (Python, offline/manual) ----
# Assumes the pipeline venv is active (see pipeline/.python-version), or override TRADECHORD.
TRADECHORD ?= tradechord-data
STAGING ?=
VERSION ?=

pipeline-install:
	cd pipeline && pip install -e ".[dev]"

pipeline-test:
	cd pipeline && python -m pytest

# e.g. make data-collect ARGS="--reporters TOP50 --years 2002-2022"
data-collect:
	$(TRADECHORD) collect --out data/staging $(ARGS)

# e.g. make data-validate STAGING=data/staging/<run>
data-validate:
	$(TRADECHORD) validate --input $(STAGING)

# e.g. make data-release STAGING=data/staging/<run> VERSION=2026-01
data-release:
	$(TRADECHORD) release --input $(STAGING) --version $(VERSION) --releases-root data/releases

# e.g. make data-verify VERSION=2026-07.1
data-verify:
	PYTHONPATH=pipeline/src python -m tradechord_pipeline.cli verify \
		--release data/releases/$(VERSION) --repo-root .

# ---- Aggregate ----
# NOTE: `build` intentionally does NOT depend on data-collect; it uses the committed release.
test: pipeline-test check
