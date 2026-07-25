.PHONY: dev check build web-install pipeline-install pipeline-test \
        data-collect data-validate data-release test

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
pipeline-install:
	cd pipeline && pip install -e ".[dev]"

pipeline-test:
	cd pipeline && python -m pytest

data-collect:
	cd pipeline && tradechord-data collect

data-validate:
	cd pipeline && tradechord-data validate

data-release:
	cd pipeline && tradechord-data release

# ---- Aggregate ----
# NOTE: `build` intentionally does NOT depend on data-collect; it uses the committed release.
test: pipeline-test check
