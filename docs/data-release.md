# Publishing a data release

Data publication is manual and offline. Normal web development never invokes
Python or contacts WITS.

## 1. Install

Use the versions declared in `.nvmrc` and `pipeline/.python-version`.

```bash
make pipeline-install
make pipeline-test
```

## 2. Pilot

Before a full historical collection, run a small dual-flow pilot:

```bash
make data-collect ARGS="--reporters USA,DEU --years 2002,2012,2022 --flows both --top-k 15"
```

Collection prints the staging run directory. Review its `run.manifest.json`
and reporter-flow manifests. Unresolved HTTP, retry, or parse failures make a
release ineligible.

## 3. Validate

```bash
make data-validate STAGING=data/staging/<run-id>
```

Validation requires the full requested reporter × flow shape, matching years,
unique canonical keys, valid values, and flow-specific WLD reconciliation.

## 4. Publish an immutable version

Never overwrite a committed release:

```bash
make data-release STAGING=data/staging/<run-id> VERSION=2026-08
```

This writes:

- `data/releases/2026-08/`
- `web/static/data/2026-08/`
- `web/static/data/current.json` last

Verify integrity:

```bash
PYTHONPATH=pipeline/src pipeline/.venv/bin/python \
  -m tradechord_pipeline.cli verify \
  --release data/releases/2026-08 --repo-root .
```

Then run `make test` and `make build`, inspect representative reporters, and
commit the canonical release, projections, and pointer together.

## Projection-only compatibility release

When projection semantics change without recollecting WITS, preserve the
original release and publish a new version:

```bash
tradechord-data reproject \
  --source data/releases/2026-07 \
  --version 2026-07.1
```

## Rollback

Set `web/static/data/current.json` back to a previous committed version and its
manifest hash. No canonical files need to be deleted.

## Safety

`data/staging/`, `pipeline/data/`, caches, shards, and raw responses are
ignored. Before a release commit, review:

```bash
git status --short
git diff --cached --stat
git diff --cached --name-only
```

Do not use `git add .` for the first commit of a large regenerated release.
